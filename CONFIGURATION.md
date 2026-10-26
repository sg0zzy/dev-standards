# Project configuration contract

Projects SHOULD describe their adoption in declarative configuration such as [project-config.example.yml](examples/project-config.example.yml). No shared executable parser is required or supplied. A project MAY use existing native metadata instead if its adoption document maps every applicable concept below to an authoritative location and defines equivalent validation.

## Required information

| Area | Contract |
| --- | --- |
| Identity | Project name/ID and repository location |
| Standards | Edition, exact immutable commit, verified snapshot location/integrity |
| Application version | One authoritative native source and read/update mapping; no duplicated editable version |
| Development state | Declared version and derived core under [VERSIONING.md](VERSIONING.md#forms); local and beta counter scopes/storage mapped separately |
| Build matrix | Target definitions and per-context mandatory/optional selections; host capabilities |
| Validation | Required checks, documented exclusions, package verification gates |
| Local storage | Root, retention override/default, manager/schema, cleanup/protection interface, local counter scope/durable recovery mapping, and host-local publishing mapping (eligible host, root, integrated step) or explicit non-adoption per [ARTIFACTS.md](ARTIFACTS.md#optional-host-local-publishing) |
| CI | Branch, PR revision policy, artifacts and retention |
| Releases | Beta dispatch, stable tag pattern, common allocation/publication coordination, notes baseline |
| Signing | Per-target profile, requiredness, nonsecret certificate/credential references |
| Android | Application IDs, update edges, numeric allocation domain/ledger and bounds if applicable |
| Distribution | Per-destination/platform/channel/artifact modes and success/retry criteria |
| Authorization | Explicit adopted automation scope and approval conditions |
| Operations | Repository-owned bump/dry-run/build/check/release/cleanup instructions and recovery procedures |

Configuration MUST NOT contain secret values or duplicate the editable application version unnecessarily. Derived package versions, generated mirrors and authoritative version metadata MUST be labeled as such. Example schema versions describe project document shape, not application versions or standards editions.

## Validation and override rules

Projects MUST validate their effective mapping before using it for release or deletion. Unknown target references, duplicate IDs, contradictory requiredness, negative retention limits, unknown distribution modes, unconfigured signing profiles, unresolved production placeholders or missing mandatory outputs MUST fail the affected operation. An explicit empty list is a deliberate exclusion, not a successful build.

Overrides MUST state their value, policy scope and rationale. Local retention is explicitly configurable with fallback 10; ordinary CI artifact retention is recommended 14 days. Exclusions of unsupported platforms need no invented build results. A configured external destination does not grant credentials or authorization; [SECURITY.md](SECURITY.md) controls those separately.

Each build/release record MUST identify the configuration revision or digest used. Conflicting configuration and adoption instructions MUST be reconciled before release; a tool MUST NOT silently choose the more permissive interpretation. The pinned standards remain authoritative unless a rule explicitly permits an override. See [ADOPTION.md](ADOPTION.md).
