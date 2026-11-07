# Adopting and migrating standards

## Initial adoption

An adopting repository MUST explicitly identify its standards edition and full immutable dev-standards commit. It MUST NOT track `main`, `latest`, or a mutable URL as its adoption identity. A project SHOULD contain `AGENTS.md` and `DEVELOPMENT_STANDARDS.md` using the [agent](templates/AGENTS.project.md) and [adoption](templates/DEVELOPMENT_STANDARDS.md) templates.

1. Inventory current architecture, valuable user data/recovery paths, version authorities, history/tags, build commands, target matrices, signing identities, stores and outstanding submissions. Apply [ARCHITECTURE.md](ARCHITECTURE.md) without requiring a stack rewrite; record applicable preferences and justified alternatives. Do not change existing release identities.
2. Select an actual immutable standards revision. Vendor its policy documents as a verified local snapshot (recommended) or document a verifiable retrieval method. Record repository origin, edition, full commit and snapshot/file digests. A version label without a commit is insufficient. Populate all template placeholders before claiming adoption.
3. Document build and distribution matrices independently, mapping existing native metadata or adopting the recommended configuration. Select defaults and justified overrides explicitly. Do not activate store automation as an accidental consequence of adding a build target.
4. Implement operations in the application repository's own tools, including the explicit bump/dry-run/recovery interface under [VERSIONING.md](VERSIONING.md#explicit-version-bump). Map declared version state, local counters and official reservations separately; preserve authoritative version and signing history. Add local storage/metadata/retention, CI artifacts, then staged beta/stable publication and separately authorized destinations.
5. Execute applicable [COMPLIANCE.md](COMPLIANCE.md) cases and save evidence. Record deviations, scope exclusions and unresolved gaps with owner/remediation. A MUST gap blocks claiming full compliance in that scope; staged adoption MAY be labeled partial.
6. Review and commit the adoption and implementation together through the project's normal process. Remote operations still require authorization.

## Agent resolution and offline use

Agents MUST use the project's pinned revision over an unrelated newer central copy. They MUST verify that the policy they read matches the adoption record. If the central source is unavailable, use the verified local snapshot. If no verified policy source exists, explicitly report the missing source and refrain from guessing compliance or performing policy-dependent release/deletion operations. Independent safe inspection/work MAY continue. Never silently substitute another edition.

The snapshot MUST contain the normative documents needed for the adopted scopes and their cross-references. Projects SHOULD vendor the full documentation set for simplicity. Repository-native snapshot validation MAY use Git object identity plus file digests or an equivalent verifiable archive. No central availability dependency is required for normal builds.

## Optional visual UI workflow

For graphical UI work, include [MOQAI.md](MOQAI.md) in the verified policy source and follow the [setup guide](examples/moqai-workflow.md) when enabling Moqai. Record existing project-local documents and the independent Moqai installation/source in project instructions or design records; use the project template's optional mapping. No central configuration, application dependency, automatic initialization or global agent configuration change is needed. The [portable skill](ai-skills/moqai/SKILL.md) can be installed separately from standards adoption.

## Design records and drift

For substantial changes, apply [DESIGN.md](DESIGN.md) from the verified policy source: keep one reviewable record per substantial change in a project-chosen location, and record that location plus any index, approval convention and reconciliation practice in the adoption record or project instructions. Record the direction chosen for each reported divergence. Nothing here adds a directory requirement, tool, plugin, shared service or automatic documentation job; the [portable drift skill](ai-skills/audit-doc-drift/SKILL.md) installs independently of adoption and only reads.

## Optional web visual style

For projects with web surfaces, apply [VISUAL-STYLE.md](VISUAL-STYLE.md) from the verified policy source: keep one short style reference per styled surface beside the design records and record its location in project instructions. No framework, CSS methodology, design tool, or gallery subscription is introduced; third-party visual references stay external and cited. The [portable style skill](ai-skills/define-web-style/SKILL.md) installs independently of adoption.

## Migration

A new central edition MUST NOT change existing projects automatically. A migration MUST:

1. Compare the old and selected new immutable revisions and record changed obligations, scope and justified overrides.
2. Assess effects on version reservations, Android code/signing/update history, retention/deletion and distribution authorization. Preserve all historical identities and existing protected artifacts.
3. Prepare implementation and verified snapshot updates on a local branch or equivalent reviewable change; do not replace the pin before the required behavior is ready.
4. Run affected acceptance cases, including rollback/failure paths. Record remaining gaps and avoid claiming full compliance while they remain.
5. Adopt the new pin/snapshot, mappings and evidence atomically in the reviewed project change. Do not enable additional remote behavior without its required authorization.

If a migration is rolled back, preserve remote reservations, submitted package codes and immutable assets; reverting a standards pin cannot erase external facts. Security fixes SHOULD be assessed promptly but still require explicit adoption.

## PhoneHaul and pboard

No source for either project was inspected during creation of these standards. Their platforms, tools and signing setups MUST be discovered rather than inferred from their names.

For **PhoneHaul**, start with the version/signing inventory. If it ships Android, map existing application IDs, installed signing certificates, Play upload/app-signing identities and highest allocated/submitted versionCodes before choosing update promises. Implement its applicable local/CI/release targets, then test beta→stable without uninstalling. Store delivery remains manual/disabled until explicitly configured.

For **pboard**, start with its actual supported desktop, browser or web targets and host/toolchain requirements. Select mandatory release targets and installation checks, collect each local build independently, then add temporary CI output and staged releases. If Android is absent, mark the Android cases out of scope. Neither project needs a dependency on a common executable framework.
