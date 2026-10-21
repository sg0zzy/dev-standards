---
name: prepare-release
description: Prepare or assess readiness for a specified beta or stable release using the project's adopted versioning and release procedures. Not for ordinary builds, feature completion, or publication merely implied by preparation.
---

# Prepare a release

Resolve the project's instructions, adoption record, and verified pinned policies before policy-dependent operations. Respect higher-priority instructions. Read the adopted `VERSIONING.md` and `RELEASE.md`; use `SECURITY.md#agent-operations` for authority, `BUILD.md` and `ARTIFACTS.md` for readiness, and `ANDROID.md` or `DISTRIBUTION.md` only for applicable targets/destinations. Do not substitute a newer central policy. If the verified source is missing, report it and continue only independent safe inspection.

- Identify the requested channel, selected version/source, and authorized operations. Distinguish readiness assessment, local preparation, validation, GitHub publication, and external distribution. Preparation alone does not authorize a bump, commit, tag, push, or publication; honor explicit existing authorization without asking again.
- Inspect working-tree state and relevant local history. Verify current remote official tags, releases, and durable reservation history through read-only queries and the repository's documented validation procedure. Report incomplete/shallow or unavailable history as a blocker to confirming release eligibility, not evidence of an unused version.
- Use existing repository release tooling and nonmutating dry-runs first. Check version authority/mirrors, historical reservations, ordering/concurrent allocation, source identity, recovery behavior, required checks, artifacts/manifests, and applicable signing evidence against the owning policies. For an explicitly requested development bump, use the repository bump mechanism under `VERSIONING.md#explicit-version-bump`; stable finalization follows `RELEASE.md` instead.
- Run authorized local readiness checks; inspect command effects before invoking a workflow that can mutate refs or contact publication/signing services. Report actual results and blockers, with source/history evidence and any unverified gates. Reuse existing release records/notes rather than inventing a new process.

Leave a reviewable preparation result and the exact next authorized step. Never commit, tag, push, publish, or deploy without explicit authorization covering that operation. Use the adopted policies for reservation, cleanup, and recovery decisions; this skill defines no release rules of its own.
