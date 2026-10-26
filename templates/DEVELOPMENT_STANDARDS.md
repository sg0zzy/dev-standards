# Development standards adoption

<!-- Copy into a project and replace all placeholders. This template is not an adoption. -->

| Field | Adopted value |
| --- | --- |
| Standards origin | `<REPOSITORY_URL>` |
| Edition | `<EDITION>` |
| Immutable commit | `<FULL_COMMIT>` |
| Verified local snapshot | `<PATH>` |
| Snapshot inventory/digest verification | `<PATH_AND_METHOD>` |
| Adoption date and developer approval | `<DATE_AND_RECORD>` |
| Scope/status | `<FULL_OR_PARTIAL_AND_APPLICABLE_PLATFORMS>` |
| Configuration/native mapping | `<PATH>` |
| Compliance evidence | `<PATH>` |

## Project mapping

| Policy concept | Native implementation and authoritative location |
| --- | --- |
| Architecture, stack rationale, offline/privacy behavior and data export/backup/sync recovery | `<DOCUMENT_AND_APPLICABLE_SCOPE>` |
| Application version, declared development state and generated mirrors | `<PATH_FIELDS_AND_MAPPING>` |
| Explicit version bump, dry-run, selective commit and recovery | `<DOCUMENT_AND_COMMANDS>` |
| Compatibility surface and version-zero promises | `<DOCUMENT>` |
| Build matrix by local/CI/beta/stable | `<CONFIG_OR_TABLE>` |
| Local prerequisites, commands and dirty-source identity | `<DOCUMENT>` |
| Artifact manifest, local counter scope/recovery, retention limit, dry-run/protection | `<DOCUMENT>` |
| Host-local publishing (adopted or declined; host condition, root, integrated step) | `<DOCUMENT_OR_NOT_ADOPTED>` |
| Git exclusions under the pinned ARTIFACTS.md policy | `<ROOT_GITIGNORE_AND_VALIDATION_EVIDENCE>` |
| CI checks, PR revision and temporary retention | `<DOCUMENT>` |
| Shared beta/stable reservation and publication coordination | `<DOCUMENT>` |
| Release preparation, publication, notes and recovery | `<DOCUMENT>` |
| Per-platform package versions, signing and verification | `<DOCUMENT>` |
| Android update edges and numeric history, if applicable | `<DOCUMENT_OR_NOT_APPLICABLE>` |
| Distribution matrix, approvals, success evidence, retries | `<DOCUMENT>` |

## Overrides, recommendations and gaps

Record each explicitly configurable override and each SHOULD departure with policy link, value, rationale and consequences. Record each unmet MUST separately with affected scope, risk, owner and remediation; it blocks full compliance in that scope. List scope exclusions explicitly. Do not label an unimplemented mandatory target optional merely to bypass an existing release gate.

| Type | Policy | Decision/rationale | Owner/evidence |
| --- | --- | --- | --- |
| `<DEFAULT_OVERRIDE/SHOULD_DEPARTURE/MUST_GAP/SCOPE_EXCLUSION>` | `<LINK>` | `<DETAILS>` | `<RECORD>` |

## Authorized automation

Record only developer-approved authority: operation, channel, destination, eligible sources, required checks/approvals, and approval evidence. Default external destinations to disabled/manual until explicitly configured. Mode declarations alone are not agent authorization. If no standing authority is adopted, state that remote actions require specific authorization.

## Acceptance evidence and migration history

Record acceptance case ID, source/config revision, date, result, evidence and scope. Simulations must be labeled; do not claim a live store result from a mock. Record the previous/new standards commits, changed obligations, tests and developer review for every migration. Preserve historical tags, codes and artifacts across rollback. New central revisions do not update this adoption automatically.
