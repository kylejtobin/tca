---
name: tca-architecture-document
description: Write or review TCA's architecture document using tailored arc42 and precise declarative engineering language. Documentation edits require explicit human authorization.
---

# TCA Architecture Document

## Authorization

Create or modify documentation only when the human user explicitly requests or authorizes that documentation change. Development, refactoring, bug fixes, passing tests, discovered inconsistencies, and this skill's invocation do not grant permission to edit documentation. Report discrepancies to the human; do not change requirements, add exceptions, or rewrite the design to accommodate implementation. Apply authorization only to the documents and changes it covers.

## Purpose and preparation

Write as an architect specifying a coherent, implementable design. Read the human's current direction, relevant discussion, `docs/product.md`, and `docs/architecture/DESIGN.md`. Ground each section in established decisions and their reasoning. Separate agreed design from genuinely open choices and implementation evidence.

Use current authorized architectural refinements rather than preserving historical mechanisms by default. A proposed design change requires explicit human authorization before it becomes documented policy.

## Schema

Use [arc42](https://arc42.org/overview/), tailored to TCA. Record owner, status, date/version, and a reference to the product document.

1. **Introduction and goals:** Architectural objectives and key quality goals.
2. **Constraints:** Actual limits on architectural choices.
3. **Context and scope:** System boundaries, users, interfaces, and external authorities.
4. **Solution strategy:** Fundamental approach and rationale.
5. **Building block view:** Components, responsibilities, contracts, and dependencies.
6. **Runtime view:** Important execution scenarios and their interactions.
7. **Deployment view:** Execution environments, infrastructure, and persistence boundaries.
8. **Crosscutting concepts:** Shared construction, identity, ownership, evidence, permission, lifecycle, and security rules.
9. **Architectural decisions:** Consequential choices and rationale; reference consistent ADRs.
10. **Quality requirements:** Concrete scenarios and observable acceptance criteria.
11. **Risks and technical debt:** Explicit weaknesses, uncertainties, and verification limits.
12. **Glossary:** Stable definitions of essential terms.

## Language

Use concise, literal, declarative engineering language. Name the responsible component, condition, and consequence. State each rule once. Separate the rule from its rationale.

Use tables for exact distinctions and diagrams for dependencies or meaningful execution sequences. Avoid em dashes, metaphors, slogans, conversation history, generic filler, and arbitrary function counts or line limits.

Specify contracts precisely without inventing mechanisms or technology choices. State target requirements confidently; distinguish them from demonstrated implementation and executed checks. One document-status statement is sufficient.

## Review

Check responsibilities and terminology across all sections. Follow important scenarios through the producer and consumer of each guarantee, including later observations. Preserve both safety and legitimate progress.

Make unresolved decisions visible. Never hide deviations in risks, caveats, unsupported-case lists, or new exceptions. Do not weaken acceptance criteria or convert implementation defects into architectural decisions. Keep the document focused on how the approved product is realized.
