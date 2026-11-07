# Architecture principles and technology preferences

This document owns application architecture guidance. [README.md](README.md#normative-language-and-defaults) defines MUST, SHOULD and MAY. Architecture principles describe behavior and design goals; technology preferences are conditional SHOULD-level defaults. Compliance does not depend on using a particular framework.

Each application repository retains responsibility for its architecture, language, dependencies, storage, synchronization and platform integration. These standards supply no executable framework or shared runtime dependency. [BUILD.md](BUILD.md) and [DISTRIBUTION.md](DISTRIBUTION.md) independently govern delivery; choosing a cross-platform framework does not declare supported build targets or authorize any destination.

## Architecture principles

### Local operation and data ownership

Applications SHOULD prefer local-first, offline-capable behavior where feasible: core local operations should remain usable without connectivity, and pending work should survive interruption. Network-dependent features MAY require connectivity. Projects SHOULD state which functions work offline, which require a service/account, and how unavailable dependencies affect users.

Applications SHOULD avoid mandatory cloud services and accounts unless necessary for their actual requirements. Optional synchronization SHOULD NOT gate unrelated local functionality behind login. A project MAY choose a cloud-backed architecture when justified; it SHOULD document the need, affected data, availability implications and exit/export path.

Projects SHOULD prefer open standards, interoperable protocols, and local, open, portable storage formats appropriate to actual data volume, queries, durability and security needs. This does not require plain-text storage for every workload or prohibit encryption. Projects SHOULD document formats/schema versions and avoid making a proprietary service the only way to recover local data.

Applications storing valuable user data MUST provide documented export and backup/restore procedures sufficient to recover that data. These MAY use application features or supported native tools; a project need not implement a separate backup service. Disposable caches or regenerable build output are outside this requirement. Exports SHOULD use portable formats and include necessary attachments/relationships. Restoration MUST be validated against representative data; credentials or encryption keys needed for recovery MUST be handled securely. Synchronization alone MUST NOT be represented as a backup unless independent recovery of historical/deleted data is actually supported.

### Platform integration and maintainability

Projects SHOULD use native platform APIs and UI conventions where they improve integration, accessibility and usability. Cross-platform code SHOULD preserve platform-specific behavior such as permissions, lifecycle, keyboard interaction and file access where relevant. Projects MAY share logic across their own platform implementations when it reduces maintenance; they need not share UI code or force identical experiences.

Projects SHOULD minimize dependencies and architectural complexity, selecting components for demonstrated requirements rather than novelty. Dependency evaluation SHOULD consider maintenance, security, licensing, supported platforms and operational burden. Simple native storage or a small frontend MAY be preferable to a database/synchronization framework or component system.

Business logic SHOULD be separated from presentation where this meaningfully improves maintainability and testing. Projects MAY use functions, modules or another suitable boundary; no universal layered architecture, directory layout, service container or microservice system is required. Maintainability and operational simplicity SHOULD take priority over architectural novelty.

### Privacy and trust boundaries

Projects MUST apply privacy by design: request only permissions necessary for declared functionality, limit collection/transmission to its purpose, and protect sensitive data across storage, export and synchronization boundaries. Projects SHOULD prefer scoped and on-demand permissions, keep unnecessary data off remote systems, and make permission denial degrade predictably. Adding a preferred framework MUST NOT justify broader native/extension privileges or automatic telemetry. Build credentials and agent authorization remain governed by [SECURITY.md](SECURITY.md).

### Synchronization and migration integrity

When synchronization is implemented, its design MUST account for disconnected operation, interrupted/retried transfers, concurrent edits, conflicts, deletions, recovery and data integrity. Applications MAY choose automatic conflict resolution or user-assisted merging appropriate to their data; the policy MUST be documented. A connected transport or database library alone does not establish correct synchronization.

Synchronization and migrations MUST NOT silently lose valuable user data. Failures MUST preserve recoverable source data and report incomplete outcomes. Potentially destructive conflict resolution or schema/format changes MUST provide a recovery path or obtain informed user action before irreversible loss. Projects SHOULD use validated transactions, snapshots/backups or equivalent safeguards appropriate to their storage. Recovery tests MUST cover representative interruption and incompatible/corrupt-input cases for implemented synchronization/migration paths. Explicit user-requested deletion MAY remove data according to the application's disclosed behavior.

## Visual interface design

[MOQAI.md](MOQAI.md) owns the preferred optional workflow for significant UI design and redesign, including existing wireframe discovery and human review. Wireframes guide UI intent; they do not select the application stack or replace independent recovery, offline, privacy and platform-integration review.

## Web visual style

[VISUAL-STYLE.md](VISUAL-STYLE.md) owns the optional visual-style contract for web surfaces: a short project-owned style reference, semantic structure that stays independent of theme, first-viewport and motion rules, and the accessibility/performance floors a style never lowers. It does not select a CSS approach or replace the platform-integration and accessibility review above.

## Design records

[DESIGN.md](DESIGN.md) owns when a substantial change SHOULD have a reviewable design record, what makes a record usable without its original conversation, how approval state is discoverable, and how records are reconciled with implemented code. Design records capture intent; they do not replace the independent recovery, offline, privacy, platform-integration and security review above.

## Conditional technology preferences

The following defaults apply when selecting new components for a suitable new project or a justified substantive change. They are project preferences, not claims that the technology's authors prescribe this stack.

| Area | SHOULD-level default | Applicability and limits |
| --- | --- | --- |
| Cross-platform desktop | Projects SHOULD prefer **Tauri 2**, **Rust** for native/system functionality, and a **TypeScript** frontend when appropriate. | Choose the frontend complexity the product needs; React is not implied. Assess required OS integration and webview behavior. See [Tauri architecture](https://v2.tauri.app/concept/architecture/). |
| Android | Projects SHOULD prefer native **Kotlin**, **Jetpack Compose**, and direct Android platform APIs. | The desktop preference does not imply Tauri on Android or a shared web UI. See [Compose documentation](https://developer.android.com/develop/ui/compose/documentation). |
| Browser extensions | Projects SHOULD prefer **TypeScript**, standard **WebExtensions APIs**, and lightweight frontend architectures. | Validate the selected APIs on supported browsers; cross-browser APIs do not imply universal compatibility. See [Mozilla's WebExtensions documentation](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions). |
| Complex browser UIs | Projects SHOULD prefer **React with TypeScript** when component/state complexity justifies it. | Small popups, options pages and simple applications MAY remain lightweight without React. See [React's TypeScript guidance](https://react.dev/learn/typescript). |
| Local-first browser applications | Projects SHOULD **consider RxDB** when reactive local persistence, synchronization or conflict handling is required. | Consideration does not require adoption. Evaluate storage adapters, durability, schema/migration behavior, licensing and complexity against simpler options. See [RxDB](https://rxdb.info/) and its [replication/conflict handling](https://rxdb.info/replication.html). |
| Peer-to-peer synchronization | Projects SHOULD prefer **WebRTC DataChannels** when direct device-to-device synchronization is suitable. | No synchronization requirement implies no WebRTC requirement. Assess peer authentication, discovery/signaling, connectivity and any relay needs; do not promise serverless operation or universal direct connectivity. DataChannels are a transport, not a conflict-resolution/backup system. See the [WebRTC standard](https://www.w3.org/TR/webrtc/). |
| Storage | Projects SHOULD prefer **local, open, portable formats and storage systems** suited to actual requirements. | Files, embedded databases or browser storage MAY be appropriate. Evaluate durability/eviction, transactions, export and recovery rather than selecting a database by default. |

Using RxDB MUST NOT imply that synchronization or a server is mandatory. Choosing WebRTC MUST NOT implicitly authorize a hosted signaling/relay service or add a mandatory account. Any required infrastructure remains a deliberate project decision under the local-operation and privacy principles above.

## Technology selection and existing projects

Agents SHOULD follow applicable preferences when starting a new project. They MAY select alternatives for platform limitations, performance, hardware integration, security, existing codebase compatibility, long-term maintenance or a significant reduction in complexity. Preferences MUST NOT become absolute restrictions or an exclusive allowlist.

A departure SHOULD be briefly documented with the requirement, selected alternative and tradeoff, following README's recommendation-departure convention. An existing architecture note, adoption record or short decision entry is sufficient; a formal architecture decision record MAY be used but is not required. A justified alternative is not a compliance failure. An irrelevant preference is out of scope, not a missing dependency.

Existing working applications MUST NOT be rewritten merely to conform to these preferences. Agents MUST NOT introduce a preferred framework into an existing project solely for standardization. Any proposed adoption/refactor SHOULD identify a concrete product, integration, security or maintenance benefit and consider migration cost and data compatibility. Improving privacy, recovery or testability MAY be incremental within the existing stack.

Review scope SHOULD match the change. Architecture review MUST NOT require installing preferred tools, introducing a service, or building a speculative synchronization layer merely to demonstrate compliance. See architectural cases R01–R12 in [COMPLIANCE.md](COMPLIANCE.md) and the project mappings in [ADOPTION.md](ADOPTION.md).

## Illustrative selection decisions

- A new desktop utility selects Tauri 2, Rust for filesystem integration, and a small TypeScript frontend. Its UI does not justify React, and it has no synchronization requirement, so it adds neither RxDB nor WebRTC.
- An existing working C++ desktop application retains its stack. The adoption change adds documented export/restore procedures and recovery checks within that implementation; switching to Tauri solely for consistency would violate this policy.
- A browser application needing reactive replicated state evaluates RxDB against its durability, conflict and licensing requirements. It may select another store with a brief maintenance/complexity rationale. Either choice still needs tested conflict handling and recovery; a database choice does not satisfy those safeguards by itself.
