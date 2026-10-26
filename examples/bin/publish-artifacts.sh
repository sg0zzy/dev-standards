#!/usr/bin/env bash
# Illustrative host-local artifact publishing helper for dev-standards adopters.
#
# Contract: ARTIFACTS.md "Optional host-local publishing"; integration
# examples in ../artifact-publishing.md.
#
# On a configured publishing host - by default the short hostname AI395,
# matched exactly - copy final distributable artifacts into
# <publish-root>/<repo-name>/, where the repository name is taken from the Git
# repository root rather than the current working directory. On every other
# host this is a successful no-op that changes nothing. Original build outputs
# always stay in place; nothing is moved, renamed or deleted.
#
# This standards repository neither runs nor depends on this script. An adopting
# project vendors it into its own tooling and invokes it only from its
# documented release/publish step, after the build and its verification have
# succeeded. Any publication additionally requires PUBLISH_ARTIFACTS_CONFIRM=1
# so ordinary development and test commands cannot publish by accident.
#
# Usage:
#   publish-artifacts.sh [-C REPO_DIR] [-d DEST_DIR] -- ARTIFACT...
#     ARTIFACT     Existing final distributable file or directory; repeatable.
#                  Paths may contain spaces. Relative paths resolve against
#                  the caller's working directory.
#     -C REPO_DIR  Repository directory used to derive the repository name
#                  (default: current directory).
#     -d DEST_DIR  Explicit absolute destination; overrides the default
#                  <publish-root>/<repo-name>.
#
# Environment:
#   PUBLISH_ARTIFACTS_ROOT       Absolute publishing root. Default /srv/artifacts.
#   PUBLISH_ARTIFACTS_HOSTS      Space/comma-separated eligible short
#                                hostnames. Default AI395 (exact,
#                                case-sensitive match).
#   PUBLISH_ARTIFACTS_CONFIRM    Must be exactly 1 to copy anything.
#   PUBLISH_ARTIFACTS_REPO_NAME  Repository-name override used only when Git
#                                reports no root; a value containing / is
#                                refused.
#   PUBLISH_ARTIFACTS_HOST       Treat this short hostname as the host instead
#                                of detecting one; for isolated test fixtures
#                                only.
#
# Exit status: 0 on successful publication or intentional no-op, 1 on any
# refusal or failure, 2 on a usage error. Every artifact is validated before
# the first mutation; publication never overwrites differing destination
# bytes and never reports success for a copy that failed.
set -euo pipefail

usage() {
    printf 'Usage: %s [-C REPO_DIR] [-d DEST_DIR] -- ARTIFACT...\n' "$0" >&2
    printf 'Publish final distributable files and directories; originals remain.\n' >&2
    printf '  -C REPO_DIR  Repository directory for the name (default: cwd).\n' >&2
    printf '  -d DEST_DIR  Explicit absolute destination; default <publish-root>/<repo-name>.\n' >&2
}

publish_root=${PUBLISH_ARTIFACTS_ROOT:-/srv/artifacts}
eligible_hosts=${PUBLISH_ARTIFACTS_HOSTS:-AI395}

short_hostname() {
    local name=""
    if command -v uname >/dev/null 2>&1; then
        name=$(uname -n 2>/dev/null || true)
    fi
    if [[ -z "$name" ]] && command -v hostname >/dev/null 2>&1; then
        name=$(hostname 2>/dev/null || true)
    fi
    printf '%s' "${name%%.*}"
}

fail() {
    printf 'publish-artifacts: %s\n' "$1" >&2
    exit "${2:-1}"
}

repo_dir=""
dest_dir=""
declare -a artifacts=()
while (( $# )); do
    case $1 in
        -C)
            (( $# >= 2 )) || { usage; exit 2; }
            repo_dir=$2
            shift 2
            ;;
        -d)
            (( $# >= 2 )) || { usage; exit 2; }
            dest_dir=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            while (( $# )); do
                artifacts+=("$1")
                shift
            done
            ;;
        -*)
            printf 'publish-artifacts: unknown option: %s\n' "$1" >&2
            usage
            exit 2
            ;;
        *)
            artifacts+=("$1")
            shift
            ;;
    esac
done

(( ${#artifacts[@]} > 0 )) || { usage; exit 2; }
for artifact in "${artifacts[@]}"; do
    if [[ -z "$artifact" ]]; then
        fail "empty artifact path"
    fi
    if [[ "$artifact" == */ ]]; then
        fail "artifact path has a trailing slash; pass the directory itself: $artifact"
    fi
    name=${artifact##*/}
    if [[ "$name" == "." || "$name" == ".." ]]; then
        fail "artifact path has no usable basename: $artifact"
    fi
done
if [[ -n "$dest_dir" && ${dest_dir:0:1} != / ]]; then
    fail "destination must be absolute: $dest_dir"
fi
if [[ ${publish_root:0:1} != / ]]; then
    fail "PUBLISH_ARTIFACTS_ROOT must be absolute: $publish_root"
fi

host=${PUBLISH_ARTIFACTS_HOST:-$(short_hostname)}
eligible=false
for wanted in ${eligible_hosts//,/ }; do
    if [[ -n "$wanted" && "$host" == "$wanted" ]]; then
        eligible=true
        break
    fi
done
if [[ "$eligible" != true ]]; then
    printf 'publish-artifacts: host %s is not a publishing host; originals unchanged.\n' "$host"
    exit 0
fi
if [[ ${PUBLISH_ARTIFACTS_CONFIRM:-} != 1 ]]; then
    fail "publishing on host $host requires PUBLISH_ARTIFACTS_CONFIRM=1. Invoke only from the documented release/publish step; ordinary development and test commands MUST NOT publish. Nothing was copied."
fi

if [[ -z "$dest_dir" ]]; then
    if [[ -n "$repo_dir" && ! -d "$repo_dir" ]]; then
        fail "repository directory does not exist: $repo_dir"
    fi
    lookup_dir=${repo_dir:-.}
    if repo_root=$(git -C "$lookup_dir" rev-parse --show-toplevel 2>/dev/null) && [[ -n "$repo_root" ]]; then
        repo_name=${repo_root%/}
        repo_name=${repo_name##*/}
    elif [[ -n "${PUBLISH_ARTIFACTS_REPO_NAME:-}" ]]; then
        if [[ "$PUBLISH_ARTIFACTS_REPO_NAME" == */* ]]; then
            fail "PUBLISH_ARTIFACTS_REPO_NAME must be a single path component: $PUBLISH_ARTIFACTS_REPO_NAME"
        fi
        repo_name=$PUBLISH_ARTIFACTS_REPO_NAME
        printf 'publish-artifacts: no Git repository root; using PUBLISH_ARTIFACTS_REPO_NAME=%s\n' "$repo_name" >&2
    else
        fail "could not determine the Git repository root from $lookup_dir. Run inside the repository, pass -C REPO_DIR, or set PUBLISH_ARTIFACTS_REPO_NAME; refusing to guess a destination. Nothing was copied."
    fi
    case $repo_name in
        "" | . | ..) fail "invalid repository name derived from the Git root: $repo_name" ;;
    esac
    dest_dir="$publish_root/$repo_name"
fi
case $dest_dir in
    */) fail "invalid destination path: $dest_dir" ;;
    */.. | */../*) fail "destination path must not contain parent references: $dest_dir" ;;
esac

# Plan every artifact - existence and destination conflicts - before creating
# or copying anything, so a late bad argument cannot publish a partial set.
declare -a dest_paths=()
declare -A seen_dest=()
for artifact in "${artifacts[@]}"; do
    if [[ ! -e "$artifact" && ! -L "$artifact" ]]; then
        fail "artifact does not exist: $artifact. Nothing was copied."
    fi
    dest="$dest_dir/${artifact##*/}"
    if [[ -n "${seen_dest[$dest]:-}" && "${seen_dest[$dest]}" != "$artifact" ]]; then
        fail "two artifacts share the destination name ${artifact##*/}: ${seen_dest[$dest]} and $artifact. Nothing was copied."
    fi
    seen_dest[$dest]=$artifact
    dest_paths+=("$dest")
done

for index in "${!artifacts[@]}"; do
    artifact=${artifacts[$index]}
    dest=${dest_paths[$index]}
    if [[ -d "$artifact" ]]; then
        if [[ -e "$dest" ]] && ! diff -rq -- "$artifact" "$dest" >/dev/null 2>&1; then
            fail "refusing to overwrite differing existing directory contents: $dest. Publish a distinct artifact name or remove the existing copy deliberately. Nothing was copied."
        fi
    elif [[ -e "$dest" ]] && ! cmp -s -- "$artifact" "$dest"; then
        fail "refusing to overwrite differing existing file: $dest. Publish a distinct artifact name or remove the existing copy deliberately. Nothing was copied."
    fi
done

if ! mkdir -p -- "$dest_dir" 2>/dev/null; then
    fail "cannot create destination directory $dest_dir (permissions?). Nothing was copied."
fi
if [[ ! -w "$dest_dir" ]]; then
    fail "destination directory is not writable: $dest_dir (permissions?). Nothing was copied."
fi

# Copy through a same-filesystem temporary name, then rename, so an interrupted
# publication cannot leave a partial artifact under its final name.
staged=""
cleanup() {
    if [[ -n "$staged" && ( -e "$staged" || -L "$staged" ) ]]; then
        rm -rf --one-file-system -- "$staged" 2>/dev/null || true
    fi
}
trap cleanup EXIT

for index in "${!artifacts[@]}"; do
    artifact=${artifacts[$index]}
    dest=${dest_paths[$index]}
    if [[ -e "$dest" ]]; then
        printf 'Already published (identical): %s\n' "$dest"
        continue
    fi
    if [[ -d "$artifact" ]]; then
        if ! staged=$(mktemp -d "${dest}.publishing.$$.XXXXXX" 2>/dev/null); then
            fail "cannot create a staging directory in $dest_dir (permissions?); $artifact was not published."
        fi
        if ! cp -a -- "$artifact/." "$staged/"; then
            fail "copy failed for $artifact; $dest was not published."
        fi
    else
        if ! staged=$(mktemp "${dest}.publishing.$$.XXXXXX" 2>/dev/null); then
            fail "cannot create a staging file in $dest_dir (permissions?); $artifact was not published."
        fi
        if ! cp -a -- "$artifact" "$staged"; then
            fail "copy failed for $artifact; $dest was not published."
        fi
    fi
    if ! mv -T -- "$staged" "$dest"; then
        printf 'publish-artifacts: install failed for %s; the staged copy remains at %s.\n' "$dest" "$staged" >&2
        staged=""
        exit 1
    fi
    staged=""
    if [[ ! -e "$dest" ]]; then
        fail "publication verification failed; $dest is absent after the copy."
    fi
    printf 'Published %s\n' "$dest"
done
