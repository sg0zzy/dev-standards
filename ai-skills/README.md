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

Keep `ai-skills/` as the single content source. Merely adding it to a checkout does not make it a default discovery directory. [Codex's documented local discovery](https://developers.openai.com/codex/skills/) scans `.agents/skills` from the working directory to the repository root and supports symlinked skill folders. The user-level location is `~/.agents/skills`. Do not install the same skill at multiple scopes under the same name.

For repository-local discovery, run this from the dev-standards root, repeating the second command for each skill wanted:

```sh
mkdir -p .agents/skills
ln -s ../../ai-skills/explore-idea .agents/skills/
```

For an adopting project with a sibling checkout at `../dev-standards`, run from that project's root instead:

```sh
mkdir -p .agents/skills
ln -s ../../../dev-standards/ai-skills/implement-feature .agents/skills/
```

These are optional POSIX shell examples, not commands performed by loading a skill. Adjust the relative target for the actual checkout layout. `ln` intentionally refuses an existing destination; inspect name collisions instead of overwriting them. For user-level discovery, create individual links in `~/.agents/skills` pointing to the chosen checkout. Use native symlink/junction tooling where appropriate on other systems; moving or removing the source checkout can break links.

Verify selected skills appear in `/skills`; restart Codex if changes are not visible. Other Agent Skills hosts can register the same canonical folders using their documented discovery mechanism. If folder links are unsupported, point the agent at the canonical `SKILL.md` explicitly; manual loading is not automatic discovery. For example: “Read `../dev-standards/ai-skills/review-change/SKILL.md` and review this diff.” No second maintained copy or host-specific frontmatter is needed.

Use a checkout at a chosen immutable revision for reproducible distribution and update it deliberately. Skill selection/versioning is independent of a project's standards adoption pin: always resolve policies through that project's adoption record, even when the skills checkout differs. In this standards repository, the root policies apply directly. In a project without an adoption record, follow its own instructions without assuming dev-standards adoption or claiming compliance; missing verified policies block policy-dependent release decisions.

## Design basis and compatibility

- The [Agent Skills specification](https://agentskills.io/specification) defines the folder/frontmatter format and progressive loading. We use only its required metadata; no experimental tool permissions or host-specific invocation fields.
- Matt Pocock's [writing-for-agents guidance](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL.md) informed conditional context pointers, explicit completion outcomes, and pruning repeated or discoverable information. Its [skill mechanics](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/writing-for-agents/SKILL-MECHANICS.md) are host-specific where they prescribe invocation fields; those fields are not copied here.
- [Official OpenAI documentation](https://developers.openai.com/codex/skills/) confirms instruction-only skills, description-based selection, progressive disclosure, and symlink discovery. Optional OpenAI UI metadata and plugin packaging are unnecessary for this local folder distribution.

Only metadata is needed for selection; load a selected body and applicable project context on demand. No supporting references or scripts are needed for these short workflows. Prefer existing deterministic checks for mechanical work. Natural-language boundaries guide behavior; they are not a tool sandbox or an enforcement mechanism. Discovery, link support, and implicit selection remain host/version dependent.

## Validation

Use the optional [skill acceptance cases](../COMPLIANCE.md#optional-ai-skills) when changing this collection. Validate every folder with the specification's `skills-ref validate PATH` or an available skill-authoring validator; no validator is required by adopting projects. Check relative links, YAML examples, and source references with temporary tooling. Review each positive/negative invocation above and the authorization cases; a schema check alone does not prove behavior.

Local validation on 2026-10-21:

- All six skills passed `skills-ref` at revision `69ef37e9424c0a7ea9dd2293b559e43ec8176379` and the available Codex skill-authoring validator. A six-entry discovery manifest was generated successfully. Validators were temporary tools, not repository dependencies.
- Repository checks resolved 110 relative links/anchors, parsed 12 YAML documents (including all six frontmatters), and checked the structure/unique IDs of 92 acceptance cases, including K01–K07. Both documented POSIX discovery examples ran in isolated fixtures; linked content matched, and repeated installation failed without changing source files. `git diff --check` passed.
- Manual instruction walkthroughs covered the six positive and six unrelated prompts above, expected outputs, discussion agreement, design/review/retro-only requests, release readiness without mutation authority, older/missing pinned policies, and unavailable tests. These are instruction reviews, not executed model evaluations.
- Full skill files measured 252–470 tokens each; combined names/descriptions measured 244 tokens using `cl100k_base`. Actual host/model tokenization and discovery overhead vary.

Actual Codex `/skills` discovery, behavioral selection in fresh agent sessions, and Windows link tooling were not exercised. Format validation and filesystem discovery fixtures do not establish cross-agent behavioral guarantees or application compliance.
