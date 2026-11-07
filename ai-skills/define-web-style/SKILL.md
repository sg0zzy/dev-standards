---
name: define-web-style
description: Create or update a project-owned web visual style reference (color, type, space, components, motion, first viewport), or apply an existing one to a page or surface. Not for backend work, in-product wireframes handled by Moqai, or imposing a style cycle on small edits.
---

# Define or apply a web visual style

Resolve project instructions and applicable standards through the project's verified adoption record; read the pinned VISUAL-STYLE.md and DESIGN.md there when present. Follow project instructions alone when no adoption exists. Never invent a tool, framework, or gallery subscription as a prerequisite.

Establish the mode: define a reference for a new or restyled web surface, apply an existing reference to a concrete page/state, or audit a rendered surface against its reference. Small edits to an already-styled surface use the existing reference without a new cycle.

When defining:

- Inspect existing pages, tokens, components, assets, and any brand material before proposing. Reuse what exists; record real values, not aspirations.
- Draft the reference as named roles: color roles with contrast-safe pairs, a type scale with families and fallbacks, space/shape/elevation rules, recurring components with their states, explicit do/don't constraints, the first-viewport plan (one primary action, message above the fold, no script-only first paint), and the motion budget including the reduced-motion equivalent for each effect.
- Keep inspiration external and cited: link the consulted gallery, page, or export with its date; state when a value is measured versus interpreted. Do not copy third-party assets, brand marks, or code from galleries, and honor each source's stated reuse terms.
- Deliver the draft in chat or at the project's design-record location only when saving is authorized. A proposal is not approval; wait for the developer's direction before implementing it.

When applying: use the reference's tokens and components; do not fork per-page styles when a token or state variant covers it. Keep semantics intact and express appearance through the project's existing CSS approach.

When auditing or finishing: render the surface at the project's declared widths and states, exercise keyboard focus, check `prefers-reduced-motion`, contrast pairs, text zoom, deferred media, and animation cost. Report inspected viewports/states, deviations from the reference, and anything unverifiable; never claim an unrendered appearance.

No output here authorizes commits, deployment, or asset downloads beyond the user's request.
