# Portable AI skills

These optional skills describe **how an agent approaches work**. The [development standards](../README.md) remain authoritative about **what rules apply** within their adopted scope, subject to higher-priority agent, system, and safety instructions. Installing skills does not adopt standards, change a project's pin, grant permissions, or establish compliance.

Each directory is a standalone Agent Skill with only `name` and `description` YAML metadata and a Markdown body. There is no required agent, executable service, shared workflow, or sequence of skills. Use only the skill relevant to the current task; trivial work needs no planning ceremony. Skills route to project instructions and the project's verified standards source rather than carrying copies of policies. Keep commands, architecture decisions, project facts, and handoff records in individual project repositories.

## Choose and invoke

Explicitly name a skill and the intended outcome. Codex CLI/IDE supports `$skill-name` and `/skills`; compatible agents may select skills from their descriptions or provide another invocation syntax. A skill selection never authorizes actions beyond the user's request.

| Skill | Practical invocation | Should not activate for |
| --- | --- | --- |
| [explore-idea](explore-idea/SKILL.md) | `$explore-idea Would a local cache solve our slow search? Compare simpler options; keep this a discussion.` | An already agreed code change |
| [design-feature](design-feature/SKILL.md) | `$design-feature Design the agreed CSV import, with acceptance criteria and a handoff here in chat.` | A one-line label edit |
| [implement-feature](implement-feature/SKILL.md) | `$implement-feature Implement the agreed import validation milestone and run relevant checks.` | A request to compare design options |
| [review-change](review-change/SKILL.md) | `$review-change Review the working diff for regressions; return findings only.` | A routine implementation self-check |
| [prepare-release](prepare-release/SKILL.md) | `$prepare-release Assess stable 1.4.0 readiness using our pinned policies. Do not bump, commit, tag, push, or publish.` | A local build or completed feature |
| [session-retro](session-retro/SKILL.md) | `$session-retro Identify recurring wasted tool calls in this session and propose one measurable improvement.` | An isolated typo or ordinary coding task |

Discussion can end with a recommendation, design with a handoff, implementation with verified changes, review with findings, release preparation with readiness evidence, and a retrospective with a small proposal. There is no automatic transition between them. Facts, assumptions, proposed decisions, and agreed decisions should remain distinguishable in these outputs.

## Installation and discovery

Keep `ai-skills/` as the single content source. On Linux, run the [installer](install.sh) from this checkout:

```bash
./ai-skills/install.sh
```

The installer needs Bash and standard Linux utilities (`readlink -f`, `dirname`, `mkdir`, and `ln`). It locates the source relative to its own file, so it also works from another directory or when invoked through a symlink. It exposes every skill folder containing `SKILL.md` through an individual symlink in `~/.agents/skills/`. No project-local installation or copied skill content is needed.

Repeated runs leave links to the same canonical folders untouched. Existing files, directories, dangling links, and links to other sources with matching skill names are reported as conflicts and preserved. Nonconflicting skills are still installed; any conflict or installation error returns a nonzero status. Resolve conflicts yourself and rerun; the script never removes or replaces existing entries. Unrelated skills are untouched. Moving the checkout breaks installed links, so keep it in a stable location. Link targets are computed locally at installation time, with no machine-specific paths in versioned configuration.

[Codex's documented discovery](https://developers.openai.com/codex/skills/) supports these user-level symlinks. Verify the skills appear in `/skills`; restart if changes are not visible. Avoid duplicate installations at project and user scope. Other Agent Skills-compatible tools can use `~/.agents/skills` if supported, register this checkout's `ai-skills/` as a search root, or link its individual folders into their documented discovery location. The standard file format does not prescribe a shared discovery directory. Use native link tooling on other systems; if a host cannot follow links or register external folders, explicitly ask it to read the canonical `SKILL.md` instead. Manual loading is not automatic discovery.

## Project access to standards

Global skill discovery does not load this repository's AGENTS.md into other projects. Use the [project AGENTS.md template](../templates/AGENTS.project.md) and [adoption record](../templates/DEVELOPMENT_STANDARDS.md) to point to a verified policy source at the project's pinned revision, following [ADOPTION.md](../ADOPTION.md#agent-resolution-and-offline-use). Resolve project paths from the project root and policy filenames from that verified source, independently of the installed skill path or current working directory.

The policy source can be a verified snapshot or a pinned central checkout reachable through a project-relative path, for example `../dev-standards-pinned`. Fill the existing snapshot/source fields with that path and its verification method. Keep only pointers and project-owned commands/context in AGENTS.md; the policy files own the rules. A shared checkout must remain available at the recorded revision; use the verified offline source/failure behavior in ADOPTION.md when it is unavailable. This does not require copying any skill into a project.

Use a chosen immutable skills revision for reproducibility and update deliberately. Skills and standards pins are independent: an updated skills checkout never changes a project's adopted policies. This standards repository uses its root policies directly. Projects without an adoption record use their own instructions without assuming adoption or compliance.

## Design basis and compatibility

- The [Agent Skills specification](https://agentskills.io/specification) defines the folder/frontmatter format and progressive loading. We use only its required metadata; no experimental tool permissions or host-specific invocation fields.
- Matt Pocock's [writing-for-agents guidance](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL.md) informed conditional context pointers, explicit completion outcomes, and pruning repeated or discoverable information. Its [skill mechanics](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL-MECHANICS.md) are host-specific where they prescribe invocation fields; those fields are not copied here.
- [Official OpenAI documentation](https://developers.openai.com/codex/skills/) confirms instruction-only skills, description-based selection, progressive disclosure, and symlink discovery. Optional OpenAI UI metadata and plugin packaging are unnecessary for this local folder distribution.

Only metadata is needed for selection; load a selected body and applicable project context on demand. The installer only creates local links; skill workflows need no executable dependency. Prefer existing deterministic checks for mechanical work. Natural-language boundaries guide behavior; they are not a tool sandbox or an enforcement mechanism. Discovery, link support, and implicit selection remain host/version dependent.

## Validation

Use the optional [skill acceptance cases](../COMPLIANCE.md#optional-ai-skills) when changing this collection. Validate every folder with the specification's `skills-ref validate PATH` or an available skill-authoring validator; no validator is required by adopting projects. Check relative links, YAML examples, and source references with temporary tooling. Review each positive/negative invocation above and the authorization cases; a schema check alone does not prove behavior.

Local validation on 2026-10-21:

- All six skills passed `skills-ref` at revision `69ef37e9424c0a7ea9dd2293b559e43ec8176379` and the available Codex skill-authoring validator. A six-entry discovery manifest was generated successfully. Validators were temporary tools, not repository dependencies.
- Integration checks resolved 114 relative links/anchors, parsed 12 YAML documents (including all six frontmatters), and checked the structure/unique IDs of 94 acceptance cases, including K01–K09. `bash -n` and `git diff --check` passed.
- Installer fixtures exercised fresh/repeat installs, unrelated skills, equivalent relative links, file/directory/wrong/dangling/looping link conflicts, source/home paths with spaces, invocation from another directory and through a symlink, missing skills/HOME, invalid arguments, and blocked destinations. Conflicts returned nonzero without changing existing entries or source contents; nonconflicting skills installed. A nested-project fixture resolved the centralized policy pointers without project skill copies; this checked paths, not an application's policy pin or compliance.
- Running the installer against the actual user directory found all six links already correct and left them and the unrelated skill unchanged. All six skills are present in this session's available-skills catalog.
- Manual instruction walkthroughs covered the six positive and six unrelated prompts above, expected outputs, discussion agreement, design/review/retro-only requests, release readiness without mutation authority, older/missing pinned policies, and unavailable tests. These are instruction reviews, not executed model evaluations.
- Full skill files measured 252–470 tokens each; combined names/descriptions measured 244 tokens using `cl100k_base`. Actual host/model tokenization and discovery overhead vary.

Interactive Codex `/skills`, behavioral selection in fresh agent sessions, other hosts, and Windows link tooling were not exercised. Format validation and filesystem discovery fixtures do not establish cross-agent behavioral guarantees or application compliance.
