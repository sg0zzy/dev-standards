# Using Moqai in a project

[MOQAI.md](../MOQAI.md) owns applicability, review and preservation rules. Moqai supports editable UI proposals: **AI generates → human edits and approves → AI rereads and implements**. A new desktop screen or a substantial navigation redesign can benefit; a backend endpoint, CLI-only tool or one-line label fix does not need a design cycle.

## Enable in an existing project

1. Choose an independent Moqai checkout and install its prerequisites as described below. Keep it outside the application's dependency/build setup.
2. In an adopting project, resolve `MOQAI.md` through its verified standards source. If the pinned revision predates this integration, follow [the migration procedure](../ADOPTION.md#migration) before changing that pin. Loading a skill alone does not migrate standards. Projects without standards adoption can use the skill under their own instructions.
3. Add the project context block below to the existing root `AGENTS.md` or OMP project instructions. Replace every placeholder with the actual location or value. Preserve other instructions; do not copy Moqai's schema into the project.
4. Load the canonical skill explicitly, or optionally enable discovery through the existing installer as described below. No global configuration change is required for explicit loading.
5. Ask the agent to prepare the first wireframe using the example request below. Existing documents should be reused. A `.moqai/` directory is needed only when saving a design; no separate initialization command exists.

Copyable project context (the angle-bracket values are placeholders):

```markdown
### Optional Moqai UI design

- Standards source, if adopted: resolve MOQAI.md through DEVELOPMENT_STANDARDS.md.
- Canonical skill: <PATH_TO_DEV_STANDARDS>/ai-skills/moqai/SKILL.md.
- Independent Moqai checkout: <PATH_TO_MOQAI_CHECKOUT>.
- Moqai source identity/version: <IMMUTABLE_REVISION_OR_SOURCE_DIGEST_AND_VERSION>.
- Format and validation references: docs/agents.md, docs/document-format.md,
  docs/components.md and docs/moqai.schema.json within that Moqai checkout.
- Project wireframe: .moqai/project.json (relative to this repository root).
- Project assets: .moqai/assets/; image references are relative to the document.
- Validation, from the Moqai checkout:
  npm run validate -- <ABSOLUTE_PROJECT_ROOT>/.moqai/project.json
- Editor, from the Moqai checkout:
  npm run dev -- --project <ABSOLUTE_PROJECT_ROOT>
- Open: http://localhost:4317/?file=.moqai/project.json
```

Use project-relative source paths where practical and document how to resolve them from the repository root; the validator/editor arguments above use the resolved absolute project path. Replace the document and asset paths if the project already uses other locations. The block records project facts; the policy and canonical skill own the workflow.

Example first request, usable in either agent without automatic skill discovery:

> Read the Moqai skill at the location recorded in this project's instructions and the matching Moqai format references. Inspect this project's existing UI and wireframes. Prepare an editable proposal for redesigning the main screen, save it at the recorded project wireframe path, and validate it. Tell me how to open it, then wait for my visual review and approval before implementing.

After opening the editor, make any visual changes and **Save**. Resume with:

> I have saved and approved the wireframe. Reread the current file from disk, validate it, and implement the approved UI in this project's existing framework. Verify the result against the saved design and report any adaptations.

Choose whether the documents/assets are shared repository design artifacts or local work, following the project's existing source-control and backup conventions. Hidden or Git-ignored documents still need to be discoverable from the recorded paths. Do not add an ignore rule automatically or commit documents without authorization.

## Install and load independently

Obtain a Moqai source checkout separately from the application. Follow its README for prerequisites and installation; the inspected version needs Node.js 24 LTS and npm. From that checkout, `npm ci` installs Moqai's own dependencies. No application package manifest or build command needs to change. Dependency installation needs package access; the installed editor operates locally and offline without accounts, cloud services or an embedded LLM.

Record the checkout/source identity and version in the target project's existing instructions or design record, together with paths to these authoritative Moqai files:

- `README.md`: prerequisites and startup.
- `docs/agents.md`: filesystem workflow and preservation.
- `docs/document-format.md` and `docs/components.md`: format invariants and component properties/defaults.
- `docs/moqai.schema.json`: formal schema; the complete validator also checks semantic invariants.

Record project-relative wireframe/asset locations and the actual installation commands. These are project-owned context, not a new configuration file format. There is no published schema package or release installer in the inspected implementation; use the files supplied by the chosen Moqai checkout. No upstream repository URL is assumed here.

Use the existing [skill installation mechanism](../ai-skills/README.md#installation-and-discovery) if desired: running `./ai-skills/install.sh` from a stable dev-standards checkout links all its skills, including `moqai`, into the user's Agent Skills directory. This is an optional user action; integration does not run it or change global configuration.

Codex uses the existing skill discovery mechanism; invoke `$moqai Redesign this desktop interface using Moqai`. For OMP (Oh My Pi), explicitly load the same `ai-skills/moqai/SKILL.md` through the harness's reusable prompt/skill mechanism or ask it to read that file. Automatic OMP discovery paths are not verified here. Other filesystem-capable agents can read the same file. Keep project-specific paths in project instructions and one canonical workflow body; no agent-specific copy or plugin is needed. The [project agent template](../templates/AGENTS.project.md) routes adopted policy through the verified standards source independently of skill installation.

## Work on a wireframe

First read the matching Moqai sources above and existing project documents. Create a proposal only when useful and authorized, conventionally at `.moqai/project.json` in the target repository. Local images belong in `.moqai/assets/` and use document-relative references. Existing alternate paths remain valid; discover them through project records and files.

Run these commands **from the separate Moqai checkout**. Replace `/absolute/path/to/target` with the actual application repository; it is an illustrative placeholder, not a literal path:

```sh
npm run validate -- /absolute/path/to/target/.moqai/project.json
npm run dev -- --project /absolute/path/to/target
```

Open [the local editor](http://localhost:4317/?file=.moqai/project.json). The developer can edit screens, geometry, properties, grouping and annotations, then **Save**. For another document, use **Open** with its project-relative path or adjust the `file` query. The implemented `--port` option changes the port; development HMR uses the next one. `npm start -- --project /absolute/path/to/target` serves an already-built production editor; follow Moqai's own build instructions when needed.

Tell the developer which file is proposed and whether validation passed. Wait for required review/approval before implementation. After approval and Save, reread the current JSON and validate it, then implement the approved UI in the project's existing stack. Verify labels, grouping, layout intent and annotations with applicable UI checks, including accessibility/platform behavior. Report any adaptations or unresolved differences.

For edits, preserve IDs and unrelated content. Coordinate with the developer, write a validated neighboring temporary file and rename it after checking the source has not changed. Preserve a recoverable original. The editor reloads clean external changes and warns on dirty conflicts; it does not lock arbitrary filesystem writers. Do not force an overwrite to clear a warning. Keep referenced assets with the document when copying or backing it up.

## Verified interface and limits

Inspected on 2026-10-30: package version **0.1.0**, document **`schemaVersion: 1`**. The source checkout had no Git HEAD; this is a local implementation inspection, not verification of a published release. Consumers should record an immutable revision when available, or source digests for an uncommitted snapshot.

- One JSON document contains project metadata and multiple fixed-size screens, with semantic elements, type-specific properties, stable identities and logical parent references. Children use screen-relative coordinates. Consult the installed schema/reference rather than copying this summary as a schema.
- `scripts/validate.ts` calls `parseDocument` in `src/model/document.ts`: the generated schema validator plus global ID uniqueness, same-screen container references and cycle checks. `src/model/registry.ts` and `src/model/schema.ts` define component properties and generate the formal schema. Unknown types/properties and unsupported format versions are rejected; migration hooks are pending the first actual format change.
- The localhost service implements project-root-confined file open/save, atomic revision-checked saves, external revision polling, image import and JSON download. Save as copies referenced assets across directories; JSON download does not bundle them. No SVG/PNG preview export or responsive auto-layout is implemented.
- There is no MCP server, installed `moqai` CLI, agent/provider integration service, runtime code generation or backend specification engine. The npm scripts above are the verified command interface. Depicted controls are inert; wireframes do not guarantee application correctness.

## Maintenance

When Moqai changes, inspect its actual README, package scripts, model registry/validator, format guide, schema, file service and examples. Update interface guidance and the skill only for implemented changes; keep applicability and approval rules in MOQAI.md. Revalidate a representative document and negative reference/version cases with the matching complete validator, and rerun the [acceptance cases](../COMPLIANCE.md#moqai-visual-ui-specifications). Do not regenerate the upstream schema during standards validation or vendor a diverging copy here.

Changes affect optional design guidance and discovery, not application dependencies, build/release/distribution contracts or existing standards pins. Adoption of a new standards revision remains explicit under [ADOPTION.md](../ADOPTION.md); this integration does not bump the standards edition or authorize commits. Future published packages, migration tools, previews or MCP interfaces require fresh implementation evidence before documentation.
