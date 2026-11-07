# Design Records and Document Drift

A design record states intended behavior, material decisions and verification for a substantial change so that a later reader can act on it without the original conversation. This policy owns a record's audience, approval state and reconciliation with implemented code. [ARCHITECTURE.md](ARCHITECTURE.md) continues to govern technology choices, [MOQAI.md](MOQAI.md) the optional visual UI workflow, [SECURITY.md](SECURITY.md#agent-operations) operation permissions, and [AI skills](ai-skills/README.md) how an agent approaches the work.

Directory, filename, tooling and agent plugin are project choices. This policy requires no particular layout, plugin, executable, service, shared workflow or rewrite.

## Applicability

| Situation | Guidance |
| --- | --- |
| Bug fix, label or copy change, dependency update, or another small change with no material decision | No design record is required; the normal commit description carries intent. A design cycle MUST NOT be imposed on trivial work. |
| Substantial feature, new interface/protocol, data-format or migration change, or a decision later maintainers must honor | Projects SHOULD keep one reviewable design record for the change in an existing project documentation location, or record why none was written. |
| Many records in one project | An index of design records is OPTIONAL. It MUST NOT become a second authority that competes with the records it lists. |
| Exploratory notes, chat transcripts, generated drafts, review reports | Working material, not the record. Promote agreed content into the record instead of pointing later work at raw material. |

## Self-containment

A record for a substantial change SHOULD be usable without the conversation that produced it: a reader holding only the record and its linked sources can restate the intended behavior, locate the affected system, and check the next milestone. Agents SHOULD perform that check before handing a design off, and repair what is missing.

- Material decisions MUST be explicit: observable behavior at affected interfaces or state, failure and recovery paths, compatibility, data formats and migration, and security-relevant choices. These are not left to inference because a later implementer would otherwise make them silently.
- Routine implementation choices MAY be left to the implementer. A record is not required to enumerate files or prescribe a step-by-step script, and demanding one for small or medium work is a compliance-review failure, not a quality signal. This is a deliberate, recorded departure from stricter conventions that require a plan to leave no decision to the implementer; such detail remains reasonable for large or high-risk work, and beyond a point it duplicates the code without adding a verifiable check.
- Distinguish verified behavior, assumptions, proposed decisions and agreed decisions. Label unresolved choices that block implementation rather than settling them quietly.
- Links from a record to source or policy documents are its evidence chain. Resolve them from the repository root and state when a referenced artifact does not exist, rather than silently filling the gap from memory.

Typical content for a substantial record, used or omitted as relevant: the problem and intended outcome; goals and explicit non-goals; the proposed approach with concrete affected interfaces; alternatives considered with concrete trade-offs and rejection reasons; risks and mitigations; open questions that remain; observable acceptance scenarios in Given/When/Then form; and the verification command or check for the next milestone. Non-goals and rejected alternatives are the parts a later reader most often needs in order not to relitigate a decision, and open questions carried forward prevent a later session from re-asking settled ones. This list is not a required template, header set, or heading order.

## Approval and implementation

A record's approval state MUST be discoverable from the record itself, the project's stated convention, or a project record: for example a status line, an approval entry, or an explicit instruction. Generating, saving or reviewing a draft MUST NOT be treated as design approval, and design approval MUST NOT be treated as authorization to implement, bump, commit, tag, push or publish beyond the user's request.

Where an approved record is the implementation reference:

1. Implement the agreed behavior. Evidence that invalidates an agreed decision is reported with its consequence; reconcile with the developer and update the record when the decision changes instead of silently diverging.
2. Report deviations from the record in the implementation result, whether or not they were chosen deliberately.
3. Leave the record's historical claims intact. Amend with an explicit change entry, or mark it superseded with a pointer to the successor; do not rewrite history so that the record appears to have always said what the code does.

An optional independent check of a record before implementation is described by the [review skill](ai-skills/review-change/SKILL.md). A review returns findings only and grants no edit authority.

## Reconciling records with code

A checked-in record describes intended behavior; the code describes what is implemented. When they diverge, neither side is automatically authoritative.

- An agent that finds a divergence MUST report it concretely: record location, code location, how they differ, and which side the evidence suggests is newer. It MUST NOT silently rewrite the record to match the code, or implement the record, unless the requested work authorizes that change.
- Where the request already establishes which side is correct — for example "the code does not match the approved spec, fix it" — correct that side and bring the record along in the same authorized change; report both.
- The developer chooses the reconciliation direction. Agents apply the chosen direction within existing authorization and preserve unrelated records and history.

A drift check compares one record, a directory of records, or the records touched by a change against current source. It MUST be nonmutating and MUST report only divergences plus its own limits: records whose implementation could not be located, unread files, and areas not inspected. "No drift detected" is valid only for the inspected scope. Typical divergence classes are behavior described but absent, behavior changed without a record update, incomplete data models or fields, hardcoded shortcuts where dynamic behavior was specified, architectural divergence, and implemented behavior with no corresponding record statement.

Cadence is a project choice: change-scoped, before release, periodic, or ad hoc. A project that adopts a practice records it in its own instructions or design records; no automation, scheduled job or tool is required, and a drift check is not evidence of correctness — it compares documents with code, not code with requirements. See the acceptance cases in [COMPLIANCE.md](COMPLIANCE.md#design-records-and-document-drift).

The [portable drift skill](ai-skills/audit-doc-drift/SKILL.md) performs this check with ordinary repository read/search tools, and installs independently of standards adoption.
