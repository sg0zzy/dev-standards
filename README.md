# dev-standards

Shared architecture, development, build, release, and distribution contracts for independent application repositories.

**Share the contracts, not the implementations.** Adopting projects MUST remain independently buildable, testable, and releasable. This repository MUST NOT provide a mandatory shared CLI, build engine, workflow service, executable parser, or runtime dependency. Projects choose their languages, agents, tools, and packaging implementations.

This is standards edition **1.0.0**. An adoption MUST additionally pin an actual immutable repository commit; the edition label alone is insufficient. This initial workspace does not establish a release tag or commit for the standards.

## Normative language and defaults

- **MUST / MUST NOT**: mandatory behavior for compliance within the rule's stated scope.
- **SHOULD / SHOULD NOT**: recommended behavior; a project MAY depart with a recorded justification and its consequences.
- **MAY**: optional project choice.

A configurable default means projects MUST apply that value when no explicit valid override exists. Documented overrides of explicitly configurable values are compliant. For example, local retention defaults to 10 but permits a nonnegative project override. An exception to a MUST that does not allow an override MUST be reported as a compliance gap; documenting it does not make it compliant. Scope exclusions (for example, no Android target) are not exceptions. Examples and templates are informative; the linked policy documents own their rules.

## Document map

| Document | Owns |
| --- | --- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture principles, conditional technology preferences and selection flexibility |
| [VERSIONING.md](VERSIONING.md) | Declared versions, explicit bumps, generated identities, ordering and allocation constraints |
| [BUILD.md](BUILD.md) | Local/CI behavior and build matrix |
| [ARTIFACTS.md](ARTIFACTS.md) | Manifests, preservation, retention and cleanup |
| [RELEASE.md](RELEASE.md) | Beta/stable state machines, notes and recovery |
| [ANDROID.md](ANDROID.md) | Android signing, update paths and numeric versions |
| [DISTRIBUTION.md](DISTRIBUTION.md) | Destination modes, channel selection and delivery |
| [SECURITY.md](SECURITY.md) | Credentials, permissions and agent authorization |
| [CONFIGURATION.md](CONFIGURATION.md) | Declarative contract and equivalent native mappings |
| [ADOPTION.md](ADOPTION.md) | Pinning, migration and project integration |
| [COMPLIANCE.md](COMPLIANCE.md) | Technology-independent acceptance cases |
| [AGENTS.md](AGENTS.md) | Instructions for maintaining this standards repository |

Start adoption with [ADOPTION.md](ADOPTION.md), [the project template](templates/DEVELOPMENT_STANDARDS.md), and [the configuration example](examples/project-config.example.yml). See [workflow patterns](examples/github-actions-patterns.md), [release scenarios](examples/release-scenarios.md), and [Android examples](examples/android-versioning.md).

The [initial review report](REVIEW.md) records deliverables, decisions, validation limits, and an example agent adoption prompt.

Optional [AI skills](ai-skills/README.md) provide portable approaches to exploration, design, implementation, review, release preparation, and session retrospectives. They complement the policies without changing standards adoption, compliance obligations, or agent permissions.

## Separate concepts

| Term | Meaning |
| --- | --- |
| Application version | SemVer product identity; platform package fields may require a documented mapping |
| Build identity | A particular execution and its source/environment; multiple builds can share a commit |
| Official remote Git tag | Immutable official version-to-commit reservation; not proof of successful packaging |
| Actions artifact | Temporary workflow output, not an official release asset |
| Release asset | Verified file attached to a completed GitHub Release |
| External distribution | A separate delivery operation to a store, site or host |
| Build matrix | Targets, architectures and requiredness per local/CI/beta/stable context |
| Distribution matrix | Artifact destinations and modes per platform and beta/stable channel |

Building a platform MUST NOT imply distributing it. Distribution MUST consume verified artifacts without additional compilation unless a documented platform requirement demands it; see [DISTRIBUTION.md](DISTRIBUTION.md).

## Scope and maintenance

These standards cover application architecture and delivery, not a universal programming style or a requirement to support every platform. Technology preferences are SHOULD-level defaults; projects retain implementation responsibility, and existing working applications MUST NOT be rewritten merely to follow them. [ARCHITECTURE.md](ARCHITECTURE.md) distinguishes those preferences from behavioral safeguards and documents justified alternatives. Projects SHOULD document their normal development, test, review, and contribution commands alongside their delivery commands. Changes to contracts MUST include an impact assessment and updates to examples and acceptance cases. Standards edition changes follow SemVer for the contract: incompatible obligations require a major edition; compatible additions use a minor edition; clarifications use a patch. Existing adoptions remain pinned until explicitly migrated.
