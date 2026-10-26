# Host-local artifact publishing

Informative examples for the normative contract in [ARTIFACTS.md — Optional host-local publishing](../ARTIFACTS.md#optional-host-local-publishing). Publishing copies the final distributable artifacts of a successful build to a host-configured directory; it is not external distribution and adds no build target or release step.

## Convention

- Eligible host: the build host's short hostname is exactly `AI395` (overridable). On every other host the publish operation is a successful no-op that creates nothing, so existing build behavior is unchanged.
- Destination: `/srv/artifacts/<repo-name>/` (overridable root), created when missing. `<repo-name>` is the basename of the **Git repository root**, never the current working directory.
- Only final distributable artifacts of a completed, verified build are published; originals remain in place. Temporary files, caches, and intermediate build directories (`target/`, `.gradle/`, `node_modules/`, staging trees) are never published.
- Existence of every artifact is checked before copying; permission and copy failures fail visibly with a nonzero status and are never reported as success. Differing existing destination bytes are refused, not silently replaced.
- Publishing runs only where the project's existing release/publish step explicitly invokes it — never from ordinary development, test, or CI commands.

## Reusable helper

[`bin/publish-artifacts.sh`](bin/publish-artifacts.sh) is one portable Bash helper implementing the contract. It is illustrative: vendor it into the project (for example `tools/publish-artifacts.sh`) or reimplement it in the project's own tooling; the policies stay authoritative. It needs no dependency beyond Bash, Git, coreutils, and `diff`/`cmp`.

```text
publish-artifacts.sh [-C REPO_DIR] [-d DEST_DIR] -- ARTIFACT...
```

Arguments are final artifact files or directories, any number, paths with spaces included. Defaults come from `PUBLISH_ARTIFACTS_ROOT` (default `/srv/artifacts`), `PUBLISH_ARTIFACTS_HOSTS` (default `AI395`), and the Git root; `PUBLISH_ARTIFACTS_REPO_NAME` overrides the name only when Git reports no root. Publication additionally requires `PUBLISH_ARTIFACTS_CONFIRM=1`, which the project's publish wrapper sets so accidental direct invocation cannot publish. Exit status: 0 published or intentional no-op, 1 refusal/failure, 2 usage error. [`bin/publish-artifacts.test.sh`](bin/publish-artifacts.test.sh) runs focused fixture checks without touching `/srv`.

Each example below assumes the helper was vendored as `tools/publish-artifacts.sh` and shows a project publish wrapper (`tools/publish.sh` or equivalent) that a human or existing release workflow invokes after a successful build — never as part of the ordinary build command itself.

## Rust

`cargo` writes under `target/`, an intermediate directory. Collect the binary (and any tarball) into the build's `local_artifacts/` directory first, then publish from there:

```sh
# tools/publish.sh - release/publish step only; not `cargo build`.
set -euo pipefail
local_dir=${1:?pass the completed local_artifacts/<id> directory}
cargo build --release --target x86_64-unknown-linux-gnu
mkdir -p "$local_dir"
cp -a "target/x86_64-unknown-linux-gnu/release/my-tool" "$local_dir/"
tar -C "$local_dir" -czf "$local_dir/my-tool-0.9.5-x86_64.tar.gz" my-tool
PUBLISH_ARTIFACTS_CONFIRM=1 tools/publish-artifacts.sh -- \
    "$local_dir/my-tool" \
    "$local_dir/my-tool-0.9.5-x86_64.tar.gz"
```

## Android / Gradle

Gradle release outputs live under `app/build/outputs/`; publish the signed APK/AAB themselves:

```sh
# tools/publish.sh - after ./gradlew assembleRelease bundleRelease succeeded.
set -euo pipefail
local_dir=${1:?pass the completed local_artifacts/<id> directory}
cp -a app/build/outputs/apk/release/app-release.apk "$local_dir/"
cp -a app/build/outputs/bundle/release/app-release.aab "$local_dir/"
PUBLISH_ARTIFACTS_CONFIRM=1 tools/publish-artifacts.sh -- \
    "$local_dir/app-release.apk" \
    "$local_dir/app-release.aab"
```

Publish debug/test packages only if the project's documentation explicitly lists them as distributable; otherwise they are test output, not final artifacts.

## Tauri

Tauri bundles land under `src-tauri/target/release/bundle/`. Publish the final packages (and signatures), not the bundle tree:

```sh
# tools/publish.sh - after `npm run tauri build` succeeded.
set -euo pipefail
local_dir=${1:?pass the completed local_artifacts/<id> directory}
bundle=src-tauri/target/release/bundle
cp -a "$bundle"/deb/*.deb "$bundle"/appimage/*.AppImage "$local_dir/"
cp -a "$bundle"/appimage/*.AppImage.sig "$local_dir/" 2>/dev/null || true
PUBLISH_ARTIFACTS_CONFIRM=1 tools/publish-artifacts.sh -- \
    "$local_dir"/sample-app_0.9.5_amd64.deb \
    "$local_dir"/sample-app_0.9.5_amd64.AppImage
```

## Node.js

Publish the pack tarball and/or the built distributable directory; never `node_modules/` or caches:

```jsonc
// package.json
{
  "scripts": {
    "build": "npm run compile && npm run test",
    "publish:local": "node tools/publish-local.mjs"
  }
}
```

```sh
# tools/publish-local.mjs runs the existing publish step only, e.g. via sh:
local_dir=${1:?pass the completed local_artifacts/<id> directory}
tarball=$(npm pack --pack-destination "$local_dir")
PUBLISH_ARTIFACTS_CONFIRM=1 tools/publish-artifacts.sh -- \
    "$local_dir/$(basename -- "$tarball")" \
    "$local_dir/web-bundle"
```

`dist/` may be published as a directory argument, but only its final distributable contents belong there; keep source maps or intermediates out when they are not distributable.

## Notes

- Publishing to `/srv/artifacts` requires the build user to be able to create that path; the helper reports permission failures explicitly. The shared destination is host-local: it grants no distribution authority, and secrets never belong in published artifacts ([SECURITY.md](../SECURITY.md)).
- On a conflict the helper fails rather than choosing for you: publish a distinct artifact name (versions normally differ) or remove the existing copy deliberately.
- The helper targets POSIX Bash hosts. Windows build hosts need an equivalent project-native implementation of the same contract, or publishing simply stays unconfigured there.
