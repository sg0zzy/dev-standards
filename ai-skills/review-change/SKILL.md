---
name: review-change
description: Review a diff, pull request, proposed code change, or feature design for actionable defects, regressions, and implementation blockers. Not for implementing fixes, general architecture brainstorming, or a routine implementation self-check.
---

# Review a change

Establish whether the target is code or a design, its scope, and the comparison baseline where applicable. Read project instructions, applicable standards through the project's adoption record, and enough surrounding code and tests to assess behavior. Respect higher-priority instructions. Treat the implementation's explanation as a claim to verify.

- Prioritize correctness, regressions, security, and maintenance consequences. Challenge assumptions and complexity when they create a concrete failure or avoidable burden; omit personal style preferences.
- For a design, briefly restate the proposed behavior from the document and linked sources before evaluating it. Check fit with the existing system, material decisions, failure/recovery paths, and verifiable acceptance criteria. Flag missing context that changes implementation or prevents understanding; do not demand code-level detail or definitions of common engineering terms.
- Trace each suspected issue to a reachable condition and its impact. Use focused, non-destructive checks when useful. Distinguish a verified defect from a potential risk that needs more evidence, and state the uncertainty.
- Report actionable findings in severity order using the project's severity convention, or plain critical/high/medium/low impact labels when none exists. Cite concrete files and line locations, explain the trigger and consequence, and suggest the smallest useful correction.
- Note material test coverage gaps and validation limits. If no actionable findings remain, say so without implying exhaustive correctness or claiming unexecuted tests passed. Keep the review proportional to the change.

For an explicitly requested fresh-context review, use a separate reviewer only when delegation is permitted and available. Supply the target, scope, project instructions, and source/policy pointers without the author's conversation or preferred verdict. Verify and deduplicate returned findings against evidence. If isolation is unavailable, report that limitation; an in-context check is not an independent fresh-context review.

After authorized fixes, recheck affected findings and behavior; stop when they are resolved or remaining blockers need user input, rather than looping for cosmetic improvements.

Return findings without modifying code or design files or posting them externally unless explicitly requested. Review authority does not grant fix, commit, or publication authority.
