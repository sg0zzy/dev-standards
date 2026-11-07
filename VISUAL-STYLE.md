# Web Visual Style

This policy covers the visual style of web surfaces: marketing/product sites, documentation sites, portfolios, landing pages and web app shells. [MOQAI.md](MOQAI.md) owns editable in-product UI wireframes, [ARCHITECTURE.md](ARCHITECTURE.md) owns stack and platform choices, [DESIGN.md](DESIGN.md) owns design-record approval and drift, and [SECURITY.md](SECURITY.md#agent-operations) owns operation permissions. Nothing here requires a framework, CSS methodology, design-tool pipeline, component library or gallery subscription.

## Applicability

| Situation | Guidance |
| --- | --- |
| No web surface, or a purely internal text/API deliverable | Not applicable. |
| New or restyled web surface with deliberate visual intent | Projects SHOULD record one short style reference for it, or record why none was written. |
| Ordinary content, copy or bug fixes on an existing styled surface | Use the existing style reference and tokens; no new style cycle. |
| Established design system or brand kit exists | Reference it. This policy does not add a competing source of visual truth. |

## Style reference

A style reference is a short, project-owned document that makes the intended look reproducible by someone who was not in the conversation. It SHOULD record, per surface:

- **Color**: named roles with values and where each role applies, plus the text/background pairs that must meet the project's contrast floor. Roles, not a raw swatch dump.
- **Typography**: type scale (size, weight, line height, tracking per role), chosen families with real fallbacks, and any mono/label treatment.
- **Space, shape, elevation**: spacing density, container widths, radii and elevation/border treatment — stated as the rules that generate them, not per-component pixel notes.
- **Components and states**: the recurring components and their required states (default, hover, focus-visible, active, disabled, loading, error, empty).
- **Constraints**: explicit do/don't rules that keep the style coherent, in the same document.
- **Motion and voice**: covered by the two sections below.

Keep it in the project's existing design-record location under [DESIGN.md](DESIGN.md) rules; a separate tool, format or parallel site is unnecessary. When a reference is derived from a third-party analysis, keep measured values separate from interpreted roles and recommendations — an exported summary is an interpretation, not a specification, and MUST be labeled as such where it drives a decision.

## Structure and style separation

The CSS Zen Garden premise is the useful engineering constraint: the same semantic markup SHOULD support a substantially different visual treatment.

- Visual redesigns SHOULD be expressible primarily as token/theme changes. Repeating literal colors, spacing or font values through page-level rules, when a named token exists, defeats that.
- Semantic HTML, content order, headings, labels and landmarks MUST NOT change to achieve an appearance. Where a required visual cannot be reached without misusing semantics, that is a design problem to report, not silently trade away.
- A project MAY use any CSS approach; the requirement is that a restyle is possible without rewriting content or behavior.

## First viewport

The first viewport is a designed surface, not an accumulation of components.

- The primary message SHOULD state what the product or person is, in the first viewport at common desktop and mobile widths; a hero that requires scrolling to learn the subject is a finding, not a style.
- One primary action per first viewport, visually distinct; secondary actions subordinate rather than competing.
- First-viewport text and the primary image/video poster MUST NOT depend on deferred or script-only loading; below-fold media and non-critical assets SHOULD be deferred per the project's performance budget.
- A campaign hero is a composition of existing components and tokens. Per-campaign component forks that duplicate the design system are a maintenance cost and SHOULD be avoided or recorded.

## Motion and delight

Motion and personality are intentional, budgeted additions, not ambient decoration.

- Each animation SHOULD have a stated purpose (spatial continuity, state change, feedback, or deliberate delight). Decorative motion that serves none of these is a candidate for removal.
- All non-essential animation MUST honor `prefers-reduced-motion: reduce` with a non-animated equivalent; motion MUST NOT be the only carrier of meaning or state, and MUST NOT block input or delay the first usable interaction.
- Loading, empty and error states are design surfaces: they SHOULD acknowledge what happened, and MAY carry personality.
- Easter eggs and occasion-driven extras are permitted. They MUST NOT change functional behavior, hide information, alter primary flows, break assistive technology or automated checks, or persist a seasonal state that confuses users; keep them additive and reversible.
- Record the motion budget (which surfaces animate, duration/easing tokens, and the accepted cost) in the style reference; otherwise it becomes invisible complexity. See [`prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion).

## Accessibility and performance floors

Visual style never lowers an existing floor.

- Text and meaningful graphics MUST meet the adopted contrast requirement; if the project states none, [WCAG 2.2 contrast minimum](https://www.w3.org/TR/WCAG22/#contrast-minimum) is the recommended reference. Color is never the only signal.
- Focus visibility is part of the design: keyboard focus MUST be visible on every interactive element and MUST NOT be removed in favor of hover-only affordances.
- Layout MUST remain usable at the project's declared breakpoints, at increased text size, and in reduced-viewport conditions; decorative effects that cause horizontal scrolling or clipped controls are defects.
- Fonts and media are budget items: declare the families/weights actually used, use a documented fallback strategy, and follow the project's media/image optimization approach. See [MDN multimedia performance](https://developer.mozilla.org/en-US/docs/Learn/Performance/Multimedia).
- Visual claims require visual evidence: verify the rendered surface at the stated widths and states, and report what was actually inspected. Code review alone does not establish appearance.

## Using external references

Galleries, screenshots, screen recordings and style exports are references, not sources of assets or authority.

- Cite the reference (link plus consulted date) in the style reference, per item where it drove a decision.
- Third-party visual material MUST NOT be vendored, scraped into the repository, or bundled as project assets or code without a license check; gallery terms may restrict reuse — for example CSS Zen Garden designs are [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/), and Design Spells asks that cited examples credit the site and link the specific item.
- Fonts, photography, illustrations, logos and brand marks are licensed assets. Recording a look derived from another site MUST NOT copy its proprietary assets, brand identity or a near-identical imitation of a specific company's trade dress.
- Imitation targets belong in the reference as an idea ("monochrome, hairline borders, mono labels"), not as an instruction to reproduce another product's identity.

## Approval and drift

A style reference is a design record: [DESIGN.md](DESIGN.md) governs its approval state, and generating a mockup, screenshot or style export is not approval to implement. Where an approved style reference is the implementation reference, deviations are reported rather than silently absorbed. A requested [drift audit](ai-skills/audit-doc-drift/SKILL.md) MAY compare the reference with implemented tokens/CSS; it reports divergence and does not choose which side changes.

See the [acceptance cases](COMPLIANCE.md#web-visual-style) and the optional [style skill](ai-skills/define-web-style/SKILL.md).
