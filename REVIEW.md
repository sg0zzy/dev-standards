# Initial standards review

This report covers creation of the documentation set in the initially empty workspace. It is not evidence that any application complies, and no standards Git commit/tag exists yet.

## Deliverables

Created `.gitignore`; `README.md`, `AGENTS.md`, `VERSIONING.md`, `BUILD.md`, `ARTIFACTS.md`, `RELEASE.md`, `ANDROID.md`, `DISTRIBUTION.md`, `SECURITY.md`, `CONFIGURATION.md`, `ADOPTION.md`, `COMPLIANCE.md`, and this report; examples `project-config.example.yml`, `github-actions-patterns.md`, `android-versioning.md`, `release-scenarios.md`; templates `AGENTS.project.md` and `DEVELOPMENT_STANDARDS.md`.

The policies standardize observable behavior and acceptance gates while leaving native tooling independent. They separate source/build identity, temporary CI output, immutable official releases, platform signing/update rules and per-destination delivery. Adoption is explicit, pinned, verifiable and migratable.

## Decisions and consistency review

| Concern | Resolution |
| --- | --- |
| Normative flexibility | MUST is mandatory; SHOULD deviations need justification; MAY is optional. Explicit retention overrides remain compliant. Other unmet MUSTs remain visible gaps. |
| Version progression | One repository-wide official stream; full SemVer precedence, independent local IDs, permanent failed reservations and publication revalidation. Skipped cores are not backfilled. |
| Concurrency | Atomic create-only tags plus common allocation/publication coordination; no reliance on workflow-local locks or scheduling order alone. |
| Artifact preservation | Unique local output, dirty-source snapshot identity and coherent source capture; bounded retention is explicit deletion, never overwrite. |
| Cleanup safety | Completion sequence, `.keep`, locking, containment/ownership checks and skip-on-uncertainty; failure never triggers retention. |
| Build versus delivery | Independent matrices and channels. Building a target never enables a store. Distribution consumes verified outputs, with only documented platform exceptions. |
| Incomplete releases | Staging and mandatory aggregate gate; failed tags remain reserved. No public success from partial packaging. |
| Android | Durable monotonic codes per update domain; real ID/certificate and device validation; upload/app-signing keys distinguished. |
| Security/agents | Local implementation authority does not imply remote publication authority. Existing scoped authorization is honored; secrets and write privileges stay out of untrusted jobs. |
| Notes | Previous successful stable Git range, with merge/cherry-pick review and generated-entry handling. |
| Platform assumptions | Only declared targets apply. Signing profiles and destination success criteria are project-specific; no guarantee of store acceptance. |
| Shared infrastructure | Documentation, illustrative YAML and templates only; no shared executable scripts or workflows. |

## Validation performed

Relative documentation links and anchors, fenced YAML syntax, example target/signing references, acceptance-case structure/IDs and SemVer transition/code-boundary examples were checked locally. The set was reviewed against the requested scopes and scenarios, including race/failure recovery and configurable defaults. Current official SemVer, Android and GitHub documentation was consulted and linked next to platform claims. No application build, device upgrade, live publication or external delivery was performed; those remain adopting-project acceptance work.

Initial local audit: 20 files (18 Markdown documents, one YAML example, one `.gitignore`); 66 relative links/anchors resolved; six YAML documents parsed (the configuration and five fenced fragments); all 57 acceptance cases have unique IDs and all four required test fields. Matrix, artifact and signing references resolve. SemVer examples were checked using temporary audit-only tooling, with no installed project dependency. The output inventory contains no executable build scripts or active workflows.

## Architecture extension review

Added `ARCHITECTURE.md`; updated `README.md`, `AGENTS.md`, `COMPLIANCE.md`, `ADOPTION.md`, both project templates and this report. The extension separates architecture behavior from conditional SHOULD-level technology preferences, covers local/offline operation, privacy, platform integration, simplicity, portable data, export/backup and synchronization/migration recovery, and explicitly prohibits standardization-only rewrites/framework additions. Illustrative selection decisions demonstrate lightweight adoption and justified alternatives.

Impact: adopting this policy adds applicable data-recovery/privacy safeguards and architecture review cases R01–R12. Stack choices remain project-owned, unsupported features remain out of scope, and justified alternative technologies remain compliant. No architecture choice adds build targets, distribution authority, a shared implementation or a required service. Existing adoptions would remain pinned until an explicit migration. Edition 1.0.0 is retained as the initial unpublished baseline in this workspace, which still has no standards Git commit/tag; this is not a silent change to a published edition.

Extension validation: 21 files, 19 Markdown documents, 77 resolved relative links/anchors, six parsed YAML documents and 69 complete uniquely identified acceptance cases. Official Tauri, Android, Mozilla, React, RxDB and W3C documentation is linked beside relevant technology guidance. No application architecture, device behavior or synchronization implementation was tested; those checks belong in adopting repositories. No executable dependencies, frameworks, services or remote changes were introduced. No unresolved central architecture policy questions remain; feasibility, stack selection and data-specific recovery design remain project decisions.

## Explicit version workflow and coherence review

The versioning extension defines the repository-owned bump interface, declared `-dev.0` state, generated local/beta identities and separate stable finalization. The cross-policy audit clarified beta tags versus source declarations, publication without branch mutation, later explicit stable preparation, local counter recovery after cleanup, and provisional local tags versus durable official reservations. Metadata manifests, configuration, adoption instructions, examples and acceptance cases were aligned.

Impact: adopting projects must supply and validate their own bump implementation and metadata mapping; local identifiers use the prescribed counter form and new beta reservations use committed development declarations. Existing pinned adoptions require explicit migration. Historical official reservations remain consumed, while local build identity, Android production-code allocation, cleanup safety and separate distribution authorization remain intact. No shared executable implementation or application compliance claim is introduced.

Local audit: 85 acceptance cases with unique IDs and complete table fields, 99 relative links/anchors, six YAML files/fragments and placeholder labels checked. Temporary audit tooling verified all four bump examples, eight precedence comparisons, nine generated lifecycle identities and fifteen Android version/code pairs. These are documentation/example checks; adopting-project behavior, device updates and live publication remain untested here. No commits, tags, releases or external repository changes were made during this extension/review.

## Host-local publishing extension

This extension adds the optional host-local publishing contract in `ARTIFACTS.md`: on an explicitly eligible build host (default short hostname `AI395`), a project's documented release/publish step MAY additionally copy that build's final distributable artifacts to `/srv/artifacts/<git-root-name>/`. Other hosts are a successful no-op with unchanged behavior. It is deliberately a copy destination, not a distribution mode: version/tag/release/distribution policies and existing build output paths are untouched, and `local_artifacts/` preservation remains mandatory.

Added `examples/artifact-publishing.md` (Rust, Android/Gradle, Tauri and Node.js integration examples plus limits), `examples/bin/publish-artifacts.sh` (one illustrative reusable Bash helper) and `examples/bin/publish-artifacts.test.sh` (focused fixture checks). Updated `README.md`, `ARTIFACTS.md`, `CONFIGURATION.md`, `COMPLIANCE.md` (new cases H01–H07; 101 uniquely identified cases total), `templates/AGENTS.project.md`, `templates/DEVELOPMENT_STANDARDS.md` and the configuration example. The helper is illustrative: adopting projects vendor or reimplement it, so the no-shared-executable rule remains intact and the helper is explicitly not required or executed by these standards.

Impact: adoption is optional (MAY); a non-adopting project is unchanged and records the mapping as not adopted. Where adopted, ordinary development/test/CI commands MUST NOT publish, publication NEVER replaces differing destination bytes, failures (missing artifact, permissions, copy) NEVER surface as success, and the repository name comes from the Git root. No new authorization is implied; secrets remain excluded. Migration is additive.

Validation: the test suite executes all 16 helper behaviors in disposable fixtures without `/srv` or root (host condition, Git-root naming from a nested directory, spaced files/directories, originals preserved, pre-copy existence checks, conflict refusal, permission and copy-failure reporting, idempotent identical republish, no-Git-root refusal and override); all pass. All relative links/anchors across the 31 Markdown/YAML/Bash files resolve, the extended configuration example and fenced YAML fragments parse, and the acceptance-case table keeps 101 uniquely identified cases. No real `/srv` directory, publishing host, or application repository was involved; H01–H07 execution against a real adopted project remains adopting-project work.

## Adoption decisions still needed

There are no deferred central policy choices required to use the contracts. Before claiming adoption, a project must select the real immutable standards commit and fill its own version authority, supported targets, mandatory gates, credentials/certificate inventories, Android domain/history if relevant, overrides, distribution modes and developer-approved remote authority. The standards repository's canonical remote URL and immutable commit remain unspecified in this workspace; template placeholders intentionally require them. Multi-stream maintenance releases are outside the chosen single-stream policy and need an explicit future policy change if required.

## PhoneHaul and pboard

Neither external repository was inspected or changed. [ADOPTION.md](ADOPTION.md#phonehaul-and-pboard) describes conditional onboarding. PhoneHaul should first inventory its actual platforms and, if applicable, Android IDs/keys/codes and update promises. pboard should first identify its actual packaging targets and host constraints. Both can pin a verified snapshot, map native tooling, implement local preservation/CI/staged releases and test applicable cases. Neither needs a shared executable dependency, and store delivery starts disabled/manual until configured.

## Example agent prompt

> Bring this repository into compliance with dev-standards edition 1.0.0 at `<FULL_IMMUTABLE_COMMIT>`. Inspect existing version/signing history and native tooling; create a verified local policy snapshot and explicit adoption record. Implement applicable local builds, artifact metadata/retention, CI, staged beta/stable release gates and independent distribution configuration using this repository's tools. Run applicable COMPLIANCE.md cases and report evidence, justified overrides and remaining gaps. Preserve existing user work, tags, package-code history and signing identities. Do not push, create remote tags, upload secrets, publish or deploy; leave remote changes reviewable for authorization.
