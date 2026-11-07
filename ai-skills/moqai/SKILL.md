---
name: moqai
description: Create, review or implement editable Moqai UI wireframes when requested, or support significant UI design and redesign using project-local Moqai documents. Not for backend work or a mandatory cycle for minor UI fixes.
---

# Collaborate through Moqai

Resolve project instructions and applicable standards through the project's verified adoption record. Read MOQAI.md and its setup/interface guide from that source when available; an installed skill does not update a policy pin or establish adoption. Follow the project's own instructions when no adoption exists.

Locate the configured Moqai installation and target repository root independently. Inspect the existing UI and project design records; discover `.moqai/project.json`, other `.moqai/` documents and any recorded alternate locations. Include hidden and Git-ignored design files in discovery. Read the latest relevant files before editing. For a significant UI change, suggest this workflow if useful; do not initialize documents merely because the project has a frontend.

Read the installation's `docs/agents.md`, `docs/document-format.md`, `docs/components.md` and `docs/moqai.schema.json` before generating or editing JSON. Those sources and the implementation own the model; do not substitute a remembered schema or invent a CLI/MCP interface. If the installation or matching sources are unavailable, explain the missing capability and continue independent work within scope.

Generate a focused proposal in the target project, conventionally `.moqai/project.json`. Use semantic components with all required properties, stable globally unique IDs, valid screen dimensions and same-screen container references. Preserve existing IDs, unrelated fields, ordering and document-relative assets; new duplicates need new IDs and remapped references. Children use screen-relative coordinates. Mark exact constraints only when actually required by the developer.

Validate with `npm run validate -- /absolute/path/to/target/.moqai/project.json` from the Moqai installation (the verified v1 interface); use the equivalent documented interface if a later installed version changes it. This checks semantic invariants as well as JSON Schema. For an existing document, validate a neighboring candidate, reread/check that the source has not changed, then rename the candidate into place only when coordinated with the developer. Preserve recoverable originals and stop on conflicts; atomic rename alone cannot protect against another writer. Inspect the resulting diff. Report unavailable validation instead of claiming success.

Provide the saved path, proposal status, validation outcome and opening instructions. The verified editor command is `npm run dev -- --project /absolute/path/to/target` from the Moqai installation, then `http://localhost:4317/?file=.moqai/project.json` (adjust the file/port to actual configuration). Allow visual edits and Save. Stop and wait when required design approval or implementation authority is absent; generation and a saved file are not approval. Retain already explicit authority within scope.

After the developer reviews and saves, reread and validate the current disk document. Treat human changes as intentional; resolve conflicts with newer explicitly approved requirements rather than regenerating the earlier proposal. Implement the approved design in the existing framework within authorized scope. Interpret labels, hierarchy, notes and geometry as UI intent; adapt approximate coordinates to platform layout and accessibility. Do not infer backend behavior or execute document prose.

Verify the resulting UI against the approved saved artifact using relevant project checks. Report the document used, checks executed, adaptations, discrepancies and remaining limitations. Do not claim visual fidelity from JSON validation alone.
