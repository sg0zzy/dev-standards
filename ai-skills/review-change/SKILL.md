---
name: review-change
description: Independently review a diff, pull request, or proposed code change for actionable defects and regressions. Not for implementing fixes, general architecture brainstorming, or a routine implementation self-check.
---

# Review a change

Establish the review scope and comparison baseline. Read project instructions, applicable standards through the project's adoption record, and enough surrounding code and tests to assess behavior. Respect higher-priority instructions. Treat the implementation's explanation as a claim to verify.

- Prioritize correctness, regressions, security, and maintenance consequences. Challenge assumptions and complexity when they create a concrete failure or avoidable burden; omit personal style preferences.
- Trace each suspected issue to a reachable condition and its impact. Use focused, non-destructive checks when useful. Distinguish a verified defect from a potential risk that needs more evidence, and state the uncertainty.
- Report actionable findings in severity order using the project's severity convention, or plain critical/high/medium/low impact labels when none exists. Cite concrete files and line locations, explain the trigger and consequence, and suggest the smallest useful correction.
- Note material test coverage gaps and validation limits. If no actionable findings remain, say so without implying exhaustive correctness or claiming unexecuted tests passed. Keep the review proportional to the change.

Return findings without modifying code or posting them externally unless explicitly requested. Review authority does not grant fix, commit, or publication authority.
