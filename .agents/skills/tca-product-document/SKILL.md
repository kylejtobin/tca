---
name: tca-product-document
description: Write or review TCA's product document using an adapted Atlassian PRD schema and developer-platform product language. Documentation edits require explicit human authorization.
---

# TCA Product Document

## Authorization

Create or modify documentation only when the human user explicitly requests or authorizes that documentation change. Development, refactoring, bug fixes, passing tests, discovered inconsistencies, and this skill's invocation do not grant permission to edit documentation. Report discrepancies to the human; do not change requirements, add exceptions, or rewrite the design to accommodate implementation. Apply authorization only to the documents and changes it covers.

## Purpose and preparation

Write as a developer-platform product manager with deep engineering understanding. Explain what TCA enables developers to express and accomplish, its value, experience, and responsibilities.

Read the human's current direction and relevant discussion, then `docs/product.md`. Extract product intent from existing material rather than copying its structure or implementation assumptions. Keep the approved product distinct from current implementation.

## Schema

Use this adaptation of the [Atlassian PRD template](https://www.atlassian.com/software/confluence/templates/product-requirements). Record owner, status, and date/version.

1. **Product definition:** What TCA is, whom it serves, and the problem it solves.
2. **Goals and success measures:** Developer benefits and how success is evaluated.
3. **Assumptions:** Beliefs about users, needs, and adoption requiring validation.
4. **Developer scenarios and requirements:** Capabilities and observable acceptance criteria.
5. **Developer experience:** How developers model, run, inspect, and evolve applications.
6. **Scope and exclusions:** Responsibilities of TCA, applications, extensions, and external systems.
7. **Open questions:** Genuinely unresolved product decisions, clearly identified.

## Language

Use precise, confident, technically fluent product language. Describe developer-visible contracts, not internal machinery. For example: “An operation runs only when its declared prerequisites are satisfied,” rather than explaining graph traversal.

Use class names and public syntax only when essential to explaining the developer experience. Keep algorithms, module inventories, and execution bookkeeping out of the product document. Excluding material does not authorize relocating it elsewhere.

Use concrete sentences and compact tables. Avoid em dashes, metaphors, slogans, conversational history, promotional claims, and repeated qualifications. One status statement establishes that this is the target product. Preserve substantive boundaries without hedging every capability.

## Review

Ensure an unfamiliar developer can explain the purpose, value, experience, capabilities, and boundaries. Make requirements observable and success measures meaningful. Keep each idea in one place.

Confirm that a better architecture could fulfill the same product definition. Never present an implementation shortcoming as a product exclusion, hide it in assumptions or open questions, or weaken a commitment to match existing code.
