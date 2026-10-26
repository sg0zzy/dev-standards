# Project agent instructions

<!-- Replace every placeholder and resolve links before adopting. -->

This repository adopts dev-standards edition `<EDITION>` at immutable commit `<FULL_COMMIT>`, recorded in [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md). Read the verified local snapshot at `<SNAPSHOT_PATH>/README.md` and the applicable policy files before changing build/release infrastructure. Use the pinned revision even if a newer central revision exists. If the central source is unavailable, use the verified snapshot; if neither can be verified, report the missing source and do not guess compliance or perform policy-dependent release/deletion actions.

Resolve project paths from this repository's root, including when working in a subdirectory. Resolve policy filenames below within the verified source recorded in DEVELOPMENT_STANDARDS.md, never relative to an installed skill. The source may be a pinned central checkout outside this project, addressed by a project-relative path; keep its revision and verification method in the adoption record.

Repository-owned instructions:

- Version authority, declared development state and platform metadata: `<PATH_AND_FIELDS>`.
- Explicit version bump, dry-run and recovery: `<DOCUMENT_AND_COMMANDS>`; use this existing mechanism rather than manually editing multiple version files, following the pinned VERSIONING.md.
- Local builds, checks and host capabilities: `<DOCUMENT_AND_COMMANDS>`.
- Build matrix and package verification: `<DOCUMENT_OR_CONFIG>`.
- Local artifact cleanup dry-run and protection: `<DOCUMENT_AND_COMMANDS>`.
- Host-local publishing (adopted or declined): `<DOCUMENT_AND_COMMANDS_OR_NOT_ADOPTED>`; where adopted, invoke only the documented release/publish step under the pinned ARTIFACTS.md host-local publishing rules, never from ordinary build or test commands.
- Git exclusions: apply the pinned snapshot's ARTIFACTS.md Git exclusions in the root `.gitignore`; verify effective ignore behavior and absence of tracked files in the excluded directories.
- Beta, stable preparation and recovery: `<DOCUMENT_AND_COMMANDS>`.
- Distribution matrix, signing identities and authorization: `<DOCUMENT_OR_CONFIG>`.
- Architecture choices, data recovery and applicable technology-preference rationale: `<DOCUMENT>`; apply the pinned snapshot's ARCHITECTURE.md without introducing frameworks or rewriting working code solely for standardization.

Read the owning policies for the requested work; keep their rules in those files:

- `ARCHITECTURE.md`: design and technology choices.
- `VERSIONING.md#explicit-version-bump`: existing repository bump mechanism; `SECURITY.md#agent-operations`: explicit-request boundary and scoped authority for version, Git, and remote operations. Feature completion alone does not authorize a bump or commit; honor existing valid session authorization.
- `BUILD.md` and `ARTIFACTS.md`: build behavior, source identity, preservation and cleanup.
- `RELEASE.md`, `DISTRIBUTION.md`, and applicable platform policies: preparation, publication, delivery and recovery.
- `COMPLIANCE.md`: applicable acceptance cases; save evidence in `<EVIDENCE_PATH>` and gaps in DEVELOPMENT_STANDARDS.md. `ADOPTION.md`: policy resolution and migration.

Optional AI skills may guide the approach to a task. Load only a relevant installed skill, resolve policies through this project's verified adoption, and keep project-specific context here. Installing a skill does not change the standards pin or authorize implementation, version operations, or publication beyond the user's request.
