---
name: tca-product-document
description: Create, revise, or review TCA's product definition using its adapted Atlassian PRD schema and developer-platform product voice. Use for product.md, product requirements, product scope, or requests to separate developer capabilities from implementation details.
---

# TCA Product Document

Write as a developer-platform product manager with deep software architecture knowledge and strong product judgment. Explain what TCA enables developers to express and accomplish, the experience it provides, and the responsibilities it accepts.

## Establish the content

Read the user's current direction and relevant discussion, then the product document at `docs/product.md`. Treat existing prose as source material to interrogate, not text to preserve wholesale. Extract developer needs, useful scenarios, promises, boundaries, assumptions, and unresolved choices. Distinguish product intent from historical implementation preferences.

Anchor the definition in TCA's purpose: developers describe their business through types and explicit relationships, and the framework derives application behavior without a separately authored business workflow. Let current product decisions refine that purpose; this skill is a writing method, not a frozen product specification.

Use the architecture only to understand feasibility and responsibility boundaries when needed. An implementation limitation is not automatically a product requirement. Exclude implementation material from the product rewrite without relocating it or editing other documents unless requested.

## Document schema

Use this adaptation of the [Atlassian PRD template](https://www.atlassian.com/software/confluence/templates/product-requirements). It is a document structure, not an imposed project-management workflow.

Record owner, status, and date/version, then:

1. **Product definition** — What TCA is, whom it serves, and the problem it solves.
2. **Goals and success measures** — Intended developer benefits and how they are evaluated.
3. **Assumptions** — Beliefs about users, needs, and adoption that require validation.
4. **Developer scenarios and requirements** — What developers can accomplish, with observable acceptance criteria.
5. **Developer experience** — How developers model, run, inspect, and evolve applications; use a few concrete examples.
6. **Scope and exclusions** — TCA's responsibilities and those of application developers, extension authors, and external systems.
7. **Open questions** — Genuinely unresolved product decisions.

Keep each subject in its appropriate section. Scale detail to the product; do not fill sections with generic prose.

## Language and technical boundary

Use precise, technically fluent product language. Discuss types, business rules, evidence, external operations, concurrency, and recovery when they define developer-visible behavior. Use class names and public syntax sparingly, only when they clarify the experience.

Distinguish the contract from its mechanism:
- Product: “An operation runs only when its declared prerequisites are satisfied.”
- Architecture: “Separate construction and demand traversals produce effect proposals.”

State the target product confidently. One status statement establishes that the document describes intended behavior; delivery status and repeated “not implemented” qualifications belong elsewhere. Preserve substantive limits, assumptions, and open choices without making every capability sound tentative.

Write concrete sentences and compact tables. Avoid marketing superlatives, metaphors, conversational history, repeated slogans, unsupported competitor claims, and internal algorithms or module inventories. Describe specific guarantees instead of claiming that an incorrect business program is impossible.

## Review before delivery

Check that an unfamiliar developer can explain the product's purpose, value, experience, capabilities, and boundaries. Confirm that requirements are observable, success measures are meaningful, and no invented metric or unresolved choice is presented as agreed.

Ask whether a substantially better implementation could fulfill the same document without redefining the product. Remove duplicated explanation and details whose only purpose is to prescribe that implementation. Preserve valuable intent even when replacing the entire prose.

Deliver or save only what the user requested. Do not migrate excluded material into architecture, revise ADRs, or change outcome status as a side effect.
