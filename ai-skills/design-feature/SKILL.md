---
name: design-feature
description: Turn an agreed feature direction into a scoped design with acceptance criteria and an implementation handoff. Use for design or milestone planning, not open-ended brainstorming or a routine edit that needs no design.
---

# Design a feature

Inspect the relevant architecture, conventions, existing decisions, and project instructions. Resolve applicable standards through the project's adoption record; respect higher-priority instructions. If the direction is unsettled, clarify only the decision that blocks a useful design.

- Define the outcome, scope boundaries, constraints, dependencies, and observable acceptance criteria. Distinguish verified behavior from assumptions and proposed decisions.
- Describe how the change fits the existing system, citing concrete modules or interfaces. Address significant risks and credible alternatives with rationale; prefer existing mechanisms over speculative abstractions.
- Size the plan to the work. For substantial features, define independently verifiable milestones, dependencies, and checks. A small feature may need only a short design and one milestone.
- Preserve enough context for another session or agent: chosen approach and rationale, relevant source/policy pointers, acceptance criteria, open questions, and the next milestone. Use an existing project design/decision record when saving is authorized; otherwise provide the handoff in the conversation. Avoid a parallel documentation system.

Design agreement does not authorize implementation. Do not implement or change implementation files unless explicitly requested. Save design files only within the user's authorized scope; a request for discussion alone does not authorize file writes.
