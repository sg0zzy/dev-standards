#!/usr/bin/env bash
# Link the canonical skills into the current user's Agent Skills directory.
set -euo pipefail

if (( $# != 0 )); then
    printf 'Usage: %s (installs into $HOME/.agents/skills)\n' "$0" >&2
    exit 2
fi

: "${HOME:?Set HOME to the destination home directory}"
script_path=$(readlink -f -- "${BASH_SOURCE[0]}")
skills_dir=$(dirname -- "$script_path")
destination="$HOME/.agents/skills"
shopt -s nullglob
skill_files=("$skills_dir"/*/SKILL.md)
if (( ${#skill_files[@]} == 0 )); then
    printf 'No skills found under %s\n' "$skills_dir" >&2
    exit 1
fi

mkdir -p -- "$destination"
status=0
for skill_file in "${skill_files[@]}"; do
    source_dir=${skill_file%/SKILL.md}
    name=${source_dir##*/}
    link="$destination/$name"

    if [[ -L "$link" ]] && [[ $(readlink -f -- "$link") == "$source_dir" ]]; then
        printf 'Already installed: %s\n' "$name"
    elif [[ -e "$link" || -L "$link" ]]; then
        printf 'Conflict: %s (left unchanged)\n' "$link" >&2
        status=1
    # Target the containing directory so ln never follows an existing skill link.
    elif ln -s -- "$source_dir" "$destination/"; then
        printf 'Installed: %s\n' "$name"
    else
        printf 'Could not install: %s (no replacement attempted)\n' "$link" >&2
        status=1
    fi
done
exit "$status"
