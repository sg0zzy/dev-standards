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
- Design records location, approval convention, optional index, and drift-audit practice (or `not adopted`): `<DOCUMENT_OR_NOT_ADOPTED>`.
- Web surfaces and their style references (or `none`): `<SURFACE_AND_STYLE_REFERENCE_PATHS_OR_NONE>`.

Read the owning policies for the requested work; keep their rules in those files:

- `ARCHITECTURE.md`: design and technology choices.
- `DESIGN.md`: design-record applicability, self-containment, discoverable approval state, and reconciliation with implemented code. Use the project facts recorded above. For a requested document-versus-code divergence audit, load the optional `audit-doc-drift` skill or the pinned source's `ai-skills/audit-doc-drift/SKILL.md`; the audit is read-only and the developer chooses the reconciliation direction.
- `VISUAL-STYLE.md`: optional web visual style for sites/docs/landing pages — style reference location and its accessibility/performance floors live in this project's records. For style work, load the optional `define-web-style` skill or the pinned source's `ai-skills/define-web-style/SKILL.md`; external gallery material stays cited inspiration, never vendored assets.
- `MOQAI.md`: applicability of the optional visual UI workflow, discovery of existing wireframes, human review and preservation. For relevant UI work, load the optional `moqai` skill or the pinned source's `ai-skills/moqai/SKILL.md` explicitly (also usable by OMP); follow the pinned policy rather than assuming the skill updates adoption.
- `VERSIONING.md#explicit-version-bump`: existing repository bump mechanism; `SECURITY.md#agent-operations`: explicit-request boundary and scoped authority for version, Git, and remote operations. Feature completion alone does not authorize a bump or commit; honor existing valid session authorization.
- `BUILD.md` and `ARTIFACTS.md`: build behavior, source identity, preservation and cleanup.
- `RELEASE.md`, `DISTRIBUTION.md`, and applicable platform policies: preparation, publication, delivery and recovery.
- `COMPLIANCE.md`: applicable acceptance cases; save evidence in `<EVIDENCE_PATH>` and gaps in DEVELOPMENT_STANDARDS.md. `ADOPTION.md`: policy resolution and migration.

Optional Moqai context (omit if not applicable): `<PROJECT_RELATIVE_DOCUMENT_PATHS_OR_NONE>`; `<MOQAI_SOURCE_VERSION_AND_DOC_LOCATION_OR_UNAVAILABLE>`; `<EDITOR_AND_VALIDATION_COMMANDS_OR_NOT_ENABLED>`. Keep these project facts here or link an existing design record.

Optional AI skills may guide the approach to a task. Load only a relevant installed skill, resolve policies through this project's verified adoption, and keep project-specific context here. Installing a skill does not change the standards pin or authorize implementation, version operations, or publication beyond the user's request.
