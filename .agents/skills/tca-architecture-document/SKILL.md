---
name: tca-architecture-document
description: Create, revise, or review TCA's architecture document using tailored arc42 and precise declarative engineering language. Use for architectural foundations, architecture.md, module boundaries, runtime contracts, or documenting an agreed architectural refinement.
---

# TCA Architecture Document

Write as a software architect responsible for a coherent, implementable design. Specify component responsibilities, relationships, contracts, and observable behavior in service of TCA's product.

## Establish the design

Read the current user direction, relevant discussion, `docs/product.md`, and the architecture at `docs/TCA_ARCHITECTURAL_FOUNDATIONS.md` (or the user's designated successor). Consult applicable decisions for rationale and obligations. Reconstruct settled choices, their reasons, corrections, and actual open questions for each section.

Treat existing documents as revisable design evidence. Distinguish a contradiction in a proposed design from a departure from an earlier design. Preserve demonstrated improvements and identify genuine architectural amendments explicitly. Do not import old implementation details simply because they exist.

Use the established TCA separation as context: independent world vocabulary, native Pydantic construction, execution declarations beside domain types, a Python interpreter separating construction from demand, independent provenance and admission, explanatory results, and a host that executes justified work. Read the current contract for exact semantics rather than duplicating them in this skill.

Resolve consequential choices before presenting a complete design. Define what each fact establishes, which boundary establishes it, and what behavior follows. Test the literal consequences across valid progress, refusal, composition, and later observations. Where library mechanics matter, verify them against the selected environment and primary documentation; label evidence accurately. Inspect code only when needed and within the user's scope.

## Document schema

Use the twelve sections of [arc42](https://arc42.org/overview/), tailored to TCA. Record owner, date/version, document status, and a product-document reference.

1. **Introduction and goals** — Architectural objectives and key quality goals; reference product intent.
2. **Constraints** — Actual limits on architectural choices.
3. **Context and scope** — Application/framework boundaries, users, interfaces, and external authorities.
4. **Solution strategy** — Core design approach and why it fulfills the product.
5. **Building block view** — Components, responsibilities, interfaces, and dependency direction.
6. **Runtime view** — Important execution scenarios, including justified progress and failure behavior.
7. **Deployment view** — Execution environments, infrastructure boundaries, and persistence responsibilities.
8. **Crosscutting concepts** — Shared construction, ownership, identity, evidence, permission, lifecycle, security, and interface rules.
9. **Architectural decisions** — Consequential choices and concise rationale; reference consistent ADRs without duplicating the specification.
10. **Quality requirements** — Concrete behavioral scenarios and observable acceptance criteria.
11. **Risks and technical debt** — Actual weaknesses, unresolved selections, and verification limits.
12. **Glossary** — Stable definitions of essential terms.

Keep sections proportionate. Mark genuinely unselected technologies without inventing a stack. Do not convert the template into a roadmap or generic engineering checklist.

## Language and precision

Use concise, literal, declarative engineering language. Name the responsible component, condition, and consequence. Prefer “Admission establishes whether an observation supplies usable evidence” to metaphors about gates or foundations.

State each rule once and reference it where needed. Use tables for exact distinctions and diagrams for dependencies or significant interaction sequences. Keep rationale distinguishable from the rule it explains.

Specify the developer-visible and internal contracts precisely while leaving incidental implementation choices open. Avoid arbitrary line limits, function counts, speculative frameworks, narrative review history, diagnostic-string policies, and repeated warnings that the target is unimplemented. One status statement establishes the document's role.

Separate target requirements, implementation claims, and executed evidence. A model's successful construction does not establish source authority; a failed admission does not erase independently established execution facts. Preserve both safety and legitimate progress when explaining a boundary.

## Review before delivery

Trace representative histories through declarations, construction, admission, evaluation, dispatch, and subsequent observations. Check both the producer and consumer of every guarantee. Resolve ambiguity that would let an implementer satisfy examples while violating the contract.

Confirm terminology, identity, conflict scope, retry permission, and component ownership agree across sections. Preserve independent work when one path is withheld. Do not call unresolved design choices implementation details or invent authority for an undefined policy.

Ensure the result explains how the product is realized without restating the PRD or recounting the conversation. Keep acceptance criteria stable; identify new requirements as amendments. Deliver or edit only the requested artifacts, and name any remaining document inconsistency rather than silently reorganizing the repository.
