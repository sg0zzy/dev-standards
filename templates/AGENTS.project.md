# Project agent instructions

<!-- Replace every placeholder and resolve links before adopting. -->

This repository adopts dev-standards edition `<EDITION>` at immutable commit `<FULL_COMMIT>`, recorded in [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md). Read the verified local snapshot at `<SNAPSHOT_PATH>/README.md` and the applicable policy files before changing build/release infrastructure. Use the pinned revision even if a newer central revision exists. If the central source is unavailable, use the verified snapshot; if neither can be verified, report the missing source and do not guess compliance or perform policy-dependent release/deletion actions.

Repository-owned instructions:

- Version authority, declared development state and platform metadata: `<PATH_AND_FIELDS>`.
- Explicit version bump, dry-run and recovery: `<DOCUMENT_AND_COMMANDS>`; use this existing mechanism rather than manually editing multiple version files, following the pinned VERSIONING.md.
- Local builds, checks and host capabilities: `<DOCUMENT_AND_COMMANDS>`.
- Build matrix and package verification: `<DOCUMENT_OR_CONFIG>`.
- Local artifact cleanup dry-run and protection: `<DOCUMENT_AND_COMMANDS>`.
- Git exclusions: apply the pinned snapshot's ARTIFACTS.md Git exclusions in the root `.gitignore`; verify effective ignore behavior and absence of tracked files in the excluded directories.
- Beta, stable preparation and recovery: `<DOCUMENT_AND_COMMANDS>`.
- Distribution matrix, signing identities and authorization: `<DOCUMENT_OR_CONFIG>`.
- Architecture choices, data recovery and applicable technology-preference rationale: `<DOCUMENT>`; apply the pinned snapshot's ARCHITECTURE.md without introducing frameworks or rewriting working code solely for standardization.

Keep all implementations in this repository's own tooling. Local builds must accept dirty sources, preserve distinct artifacts and remain local. Ordinary CI must not release or deploy. Build selection must not imply destination selection. Apply MUST/SHOULD/MAY and configurable defaults from the adopted policies; record justified SHOULD departures and report MUST gaps.

Agents may inspect, edit and locally validate requested infrastructure work. Do not push, create remote tags, upload secrets, publish or deploy without explicit authorization covering the operation. Bumps and their metadata-only local commits require an explicit developer request under the pinned VERSIONING.md and SECURITY.md; feature/bug-fix completion or a local build does not authorize them. Bump-and-commit authorization does not authorize tags, pushes or releases. Local release commits/tags require release preparation to be in task scope. Existing authorized instructions remain effective; do not request authorization again unnecessarily. A configuration mode or available credential is not by itself authorization. Never move a published tag, silently replace official assets, generate replacement production keys, or expose secrets.

Before declaring compliance, run applicable acceptance cases and record evidence in `<EVIDENCE_PATH>`. Exceptions and partial adoption status are recorded in DEVELOPMENT_STANDARDS.md. Do not upgrade the standards pin or enable additional destinations silently.

Optional AI skills may guide the approach to a task. Load only a relevant installed skill, resolve policies through this project's verified adoption, and keep project-specific context here. Installing a skill does not change the standards pin or authorize implementation, version operations, or publication beyond the user's request.
