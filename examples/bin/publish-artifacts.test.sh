#!/usr/bin/env bash
# Focused checks for the illustrative publishing helper.
# Run: bash examples/bin/publish-artifacts.test.sh
# Uses disposable directories only; never touches /srv and needs no root.
# Host eligibility is injected with PUBLISH_ARTIFACTS_HOST (test fixture hook).
set -uo pipefail

script_dir=$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")
helper=$script_dir/publish-artifacts.sh
if [[ ! -f $helper ]]; then
    printf 'missing helper: %s\n' "$helper" >&2
    exit 1
fi

failures=0
checks=0
skips=0
workspace=$(mktemp -d)
trap 'rm -rf --one-file-system -- "$workspace"' EXIT
log=$workspace/last.log
cwd_for=""

pass() { (( ++checks )); printf 'ok   %s\n' "$1"; }
fail() {
    (( ++checks ))
    (( ++failures ))
    printf 'FAIL %s\n' "$1"
    [[ -n "${2:-}" ]] && printf '     %s\n' "$2"
}
skip() { (( ++skips )); printf 'skip %s (%s)\n' "$1" "${2:-}"; }

# expect STATUS LABEL [VAR=VALUE ...] -- [ARGS...]
# Everything after `--` is passed to the helper verbatim. Runs from cwd_for
# when set; otherwise from the current directory.
expect() {
    local want=$1 label=$2
    shift 2
    local env_args=()
    while (( $# )) && [[ $1 != -- ]]; do
        env_args+=("$1")
        shift
    done
    shift
    local out status=0
    if [[ -n $cwd_for ]]; then
        out=$(env -C "$cwd_for" "${env_args[@]}" "$helper" "$@" 2>&1) || status=$?
    else
        out=$(env "${env_args[@]}" "$helper" "$@" 2>&1) || status=$?
    fi
    printf '%s' "$out" > "$log"
    if (( status != want )); then
        fail "$label" "expected exit $want, got $status; output: $(tr '\n' ' ' <<< "$out")"
        return 1
    fi
    return 0
}

# Fixture: publishing root plus a spaced repository name with a nested build
# directory, so the Git repository root differs from the working directory.
root=$workspace/srv/artifacts
repo="$workspace/Repo With Spaces"
build_dir="$repo/sub/local_artifacts/0.1.0-local.1"
mkdir -p "$build_dir/Bundle Dir" "$workspace/outside"
git -C "$repo" init -q .
printf 'apk-bytes\n' > "$build_dir/app 0.1.0.apk"
printf 'nested\n' > "$build_dir/Bundle Dir/inner file.txt"
printf '{}\n' > "$build_dir/build-info.json"

pub=(PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395 PUBLISH_ARTIFACTS_CONFIRM=1)

# 1. A non-publishing host is a successful no-op that creates nothing.
if expect 0 "other host no-op" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=devbox PUBLISH_ARTIFACTS_CONFIRM=1 \
    -- -- "$build_dir/app 0.1.0.apk" && [[ ! -e "$root" ]]; then
    pass "non-publishing host changes nothing"
else
    fail "non-publishing host changes nothing" "$(tr '\n' ' ' < "$log")"
fi

# 2. Eligibility is an exact, case-sensitive short-hostname match.
if expect 0 "case-sensitive host" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=ai395 PUBLISH_ARTIFACTS_CONFIRM=1 \
    -- -- "$build_dir/app 0.1.0.apk" &&
    expect 0 "prefix host" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395x PUBLISH_ARTIFACTS_CONFIRM=1 \
    -- -- "$build_dir/app 0.1.0.apk" && [[ ! -e "$root" ]]; then
    pass "hostname match is exact"
else
    fail "hostname match is exact" "$(tr '\n' ' ' < "$log")"
fi

# 3. The publishing host refuses without the release-step confirmation.
if expect 1 "confirmation required" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395 \
    -- -- "$build_dir/app 0.1.0.apk" && grep -q PUBLISH_ARTIFACTS_CONFIRM "$log" && [[ ! -e "$root" ]]; then
    pass "publishing refuses without confirmation"
else
    fail "publishing refuses without confirmation" "$(tr '\n' ' ' < "$log")"
fi

# 4. Publication from a nested directory uses the Git root name, preserves
#    spaced paths and directory trees, and leaves originals in place.
if (cd "$repo/sub/local_artifacts" && env "${pub[@]}" "$helper" \
    -- "$build_dir/app 0.1.0.apk" "$build_dir/Bundle Dir" "$build_dir/build-info.json") > "$log" 2>&1; then
    pass "publish from nested directory"
else
    fail "publish from nested directory" "$(tr '\n' ' ' < "$log")"
fi
dest="$root/Repo With Spaces"
if cmp -s "$dest/app 0.1.0.apk" "$build_dir/app 0.1.0.apk" &&
    cmp -s "$dest/Bundle Dir/inner file.txt" "$build_dir/Bundle Dir/inner file.txt" &&
    cmp -s "$dest/build-info.json" "$build_dir/build-info.json"; then
    pass "files and directory trees published intact"
else
    fail "files and directory trees published intact"
fi
if [[ -f "$build_dir/app 0.1.0.apk" && -d "$build_dir/Bundle Dir" ]]; then
    pass "original build outputs remain in place"
else
    fail "original build outputs remain in place"
fi

# 5. Repeating an identical publication is an idempotent success.
if env "${pub[@]}" "$helper" -C "$repo" -- "$build_dir/app 0.1.0.apk" > "$log" 2>&1 &&
    grep -q "Already published" "$log"; then
    pass "identical retry is idempotent"
else
    fail "identical retry is idempotent" "$(tr '\n' ' ' < "$log")"
fi

# 6. A missing artifact fails the whole call before anything is copied.
printf 'fresh\n' > "$repo/fresh.txt"
if expect 1 "missing artifact" "${pub[@]}" -- -C "$repo" -- "$repo/fresh.txt" "$build_dir/absent.txt" &&
    [[ ! -e "$dest/fresh.txt" ]]; then
    pass "missing artifact copies nothing"
else
    fail "missing artifact copies nothing" "$(tr '\n' ' ' < "$log")"
fi

# 7. Differing destination bytes are never silently replaced.
printf 'older\n' > "$dest/collide.txt"
printf 'newer\n' > "$repo/collide.txt"
if expect 1 "conflicting file" "${pub[@]}" -- -C "$repo" -- "$repo/collide.txt" &&
    [[ $(cat "$dest/collide.txt") == "older" ]]; then
    pass "conflicting file refused, bytes preserved"
else
    fail "conflicting file refused, bytes preserved" "$(tr '\n' ' ' < "$log")"
fi
printf 'extra\n' > "$dest/Bundle Dir/only-remote.txt"
if expect 1 "conflicting directory" "${pub[@]}" -- -C "$repo" -- "$build_dir/Bundle Dir"; then
    pass "conflicting directory refused"
else
    fail "conflicting directory refused" "$(tr '\n' ' ' < "$log")"
fi

# 8. Two artifacts sharing a destination basename are refused.
mkdir -p "$repo/other"
cp -- "$repo/fresh.txt" "$repo/other/fresh.txt"
if expect 1 "duplicate basename" "${pub[@]}" -- -C "$repo" -- "$repo/fresh.txt" "$repo/other/fresh.txt" &&
    [[ ! -e "$dest/fresh.txt" ]]; then
    pass "duplicate destination basename refused"
else
    fail "duplicate destination basename refused" "$(tr '\n' ' ' < "$log")"
fi

# 9. Usage errors: no artifacts, trailing slash, unknown option, relative -d.
if expect 2 "no artifacts" "${pub[@]}" -- -C "$repo" &&
    expect 1 "trailing slash" "${pub[@]}" -- -C "$repo" -- "$build_dir/Bundle Dir/" &&
    expect 2 "unknown option" "${pub[@]}" -- --bogus -- "$repo/fresh.txt" &&
    expect 1 "relative destination" "${pub[@]}" -- -C "$repo" -d relative/dir -- "$repo/fresh.txt"; then
    pass "usage errors refused"
else
    fail "usage errors refused" "$(tr '\n' ' ' < "$log")"
fi

# 10. An uncreatable destination reports a permissions failure.
if (( EUID == 0 )); then
    skip "uncreatable destination" "running as root"
else
    locked=$workspace/locked
    mkdir -p "$locked" && chmod 555 "$locked"
    if expect 1 "locked destination" PUBLISH_ARTIFACTS_ROOT="$locked/nested" PUBLISH_ARTIFACTS_HOST=AI395 PUBLISH_ARTIFACTS_CONFIRM=1 \
        PUBLISH_ARTIFACTS_REPO_NAME=whatever -- -- "$repo/fresh.txt" && grep -qi permission "$log"; then
        pass "permission failure reported explicitly"
    else
        fail "permission failure reported explicitly" "$(tr '\n' ' ' < "$log")"
    fi
fi

# 11. A copy failure leaves neither a staged nor a final artifact behind.
if (( EUID == 0 )); then
    skip "copy failure cleanup" "running as root"
else
    unreadable=$repo/unreadable.bin
    head -c 512 /dev/urandom > "$unreadable"
    chmod 000 "$unreadable"
    if expect 1 "unreadable source" "${pub[@]}" -- -C "$repo" -- "$unreadable"; then
        if compgen -G "$dest/unreadable.bin*" > /dev/null; then
            fail "copy failure leaves no residue" "a staged or final entry remains"
        else
            pass "copy failure leaves no residue"
        fi
    else
        fail "copy failure leaves no residue" "expected failure, got success"
    fi
    chmod 644 "$unreadable"
fi

# 12. Outside any repository the default destination is refused, not guessed;
#     an explicit single-component override is honoured.
cp -- "$repo/fresh.txt" "$workspace/outside/fresh.txt"
cwd_for=$workspace/outside
if expect 1 "no git root" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395 PUBLISH_ARTIFACTS_CONFIRM=1 \
    -- -- fresh.txt &&
    expect 0 "repo name override" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395 PUBLISH_ARTIFACTS_CONFIRM=1 \
    PUBLISH_ARTIFACTS_REPO_NAME=override-repo -- -- fresh.txt &&
    cmp -s "$root/override-repo/fresh.txt" "$workspace/outside/fresh.txt"; then
    pass "git-root refusal and override"
else
    fail "git-root refusal and override" "$(tr '\n' ' ' < "$log")"
fi
if expect 1 "override with slash" PUBLISH_ARTIFACTS_ROOT="$root" PUBLISH_ARTIFACTS_HOST=AI395 PUBLISH_ARTIFACTS_CONFIRM=1 \
    PUBLISH_ARTIFACTS_REPO_NAME=bad/name -- -- fresh.txt; then
    pass "override containing a slash refused"
else
    fail "override containing a slash refused" "$(tr '\n' ' ' < "$log")"
fi
cwd_for=""

printf '\n%s/%s checks passed, %s skipped\n' "$(( checks - failures ))" "$checks" "$skips"
(( failures == 0 ))
