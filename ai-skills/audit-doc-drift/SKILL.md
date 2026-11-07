---
name: audit-doc-drift
description: Compare checked-in design documents, specs, or generated READMEs with current source on request and report where they diverge. Not for implementing either side, code review, or keeping documentation silently in sync.
---

# Report document drift

Read the project instructions and resolve applicable standards through the project's verified adoption record; respect higher-priority instructions. Read the pinned `DESIGN.md` from that source when present for reconciliation rules. This skill needs only ordinary read, search, and diff tools; no plugin, service, or specific agent runtime is required.

Establish the target scope: one document, a directory, or the records touched by a change. Confirm the path when it is ambiguous, and state the inspected scope in the report.

For each document:

- Read it and identify the intended behavior, material decisions, and the named files, symbols, fields, endpoints, or commands it depends on.
- Locate the current implementation from those references, resolving paths from the repository root. When a reference cannot be located, report it as unresolved instead of guessing; suggest the author add a link so a later check is cheaper.
- Read the current source rather than relying on memory or the document's own claims.
- Report divergences only: described behavior absent from the code, behavior or formats changed without a document update, incomplete data models or missing fields, hardcoded shortcuts where dynamic behavior was specified, architectural divergence, and implemented behavior with no corresponding document statement. Do not summarize what still matches.

Cite the document location and the code location for each divergence, note the evidence for which side appears newer when the evidence exists, and record limits: unread files, unresolved references, and areas not inspected. "No drift detected" applies only to the inspected scope.

Stay read-only. Choosing the direction is the developer's decision: update the document, change the code, or record an accepted divergence. Where the request already establishes which side is correct, say so and note that the other side needs the matching change; do not perform it without authorization. Apply an approved direction only as its own authorized change, preserving unrelated documents and history rather than rewriting them to match current code.

Report in chat by default. Save a report file, or a dated report alongside the documents, only when saving is requested; do not add an ignore rule or commit anything. A drift report shows document-to-code mismatch, not correctness against requirements.
