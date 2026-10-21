---
name: implement-feature
description: Implement an agreed feature or milestone when the user requests code changes. Also fits a clearly scoped small change without a separate design document. Not for discussion, design-only work, or an independent review.
---

# Implement a feature

Read project instructions, relevant code, established decisions, and acceptance criteria. Resolve applicable development standards through the project's adoption record and verified pinned source; respect higher-priority instructions. Use the project's documented commands and permissions. A clear implementation request is sufficient scope; do not require a separate planning ceremony.

- Inspect the working tree and preserve existing user changes. Implement the agreed outcome with focused, proportionate changes that fit the architecture. Avoid unrelated refactoring, speculative abstractions, or additional features.
- Resolve routine technical choices autonomously. If evidence invalidates an agreed decision, explain the consequence; seek clarification only when the resulting change materially exceeds the authorized scope. Continue independent work where possible.
- Run checks that exercise the changed behavior and applicable acceptance criteria, using existing deterministic scripts/tests. Add coverage for material new behavior or regressions where useful; avoid tests that merely mirror the implementation. Inspect the final diff for unintended changes.
- Report the result, checks actually executed and their outcomes, deviations from the design, limitations, and unresolved issues. Label unrun or unavailable checks explicitly; never report tests as passed without execution evidence.

Follow repository authorization and release policies. Feature completion does not authorize a version bump, commit, tag, push, publication, or deployment. For an explicitly requested bump, use the existing repository bump mechanism under the adopted `VERSIONING.md#explicit-version-bump`, rather than manually editing multiple version files.
