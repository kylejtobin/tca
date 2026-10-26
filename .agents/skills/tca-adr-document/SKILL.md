---
name: tca-adr-document
description: Create or update docs/ADR.md with explicit human authorization, or review work for compliance with TCA's architectural decisions. Defines the single current decision register, its normative language, and its annotated schema.
---

# TCA ADR Document

## Compliance

- Agents MUST read `docs/ADR.md` in full before every compliance review.
- Agents MUST NOT use grep or search to read the register or select decisions for review.
- Agents MUST NOT substitute excerpts, summaries, or remembered content for a complete reading.
- Agents MUST assess the work against every decision and satisfy every requirement within its stated scope.
- Agents MUST NOT treat an omitted decision as permission to disregard it.

## Authoring

- Agents MUST maintain the current decision register in one file: `docs/ADR.md`.
- Agents MUST create or update documentation only when the human user explicitly authorizes that documentation change. Development and review assignments do not grant this authorization.
- Agents MUST write binding requirements using MUST and MUST NOT, with concrete subjects, actions, and boundaries.
- Agents MUST record only human-approved decisions, conditions, and exceptions.
- Agents MUST NOT use hedging or discretionary qualifiers such as "prefer," "generally," "where practical," or "unless necessary."
- Agents MUST state each approved condition precisely and specify its required behavior.
- Agents MUST surface unresolved choices for human resolution, never disguise them as flexibility.
- Agents MUST keep each WHY to one explanatory sentence. Rationale MUST NOT weaken, qualify, or add requirements.
- Agents MUST replace obsolete decision text completely when its replacement is authorized. Git preserves history.
- Agents MUST state each requirement once and keep all decisions mutually consistent.
- Agents MUST use direct engineering language without metaphors or em dashes.

## Annotated Schema

Use this structure for `docs/ADR.md`. Preserve the opening mandate. Group decisions by architectural concern; give each decision a stable identifier and a specific title.

```markdown
# Architectural Decisions

Agents MUST read this entire file before every compliance review.
Agents MUST NOT use grep, search, excerpts, summaries, or remembered content
to select or substitute for reading decisions.
Agents MUST assess work against every decision and satisfy every requirement
within its stated scope.
Changes require explicit human authorization. Git preserves prior versions.

## <Architectural concern>

### D-001: <Specific decision>
- MUST: <Required property or behavior; state scope when the section does not establish it.>
- MUST NOT: <Specific prohibited alternative; omit this line when no separate prohibition is needed.>
- WHY: <One sentence explaining the reason for the decision.>
```

## Acceptance

Before completing an authorized edit, agents MUST read the entire register and verify that every requirement is approved, conditions specify required behavior, and decisions neither conflict nor duplicate one another.

Agents MUST reject wording that lets an implementing agent justify disregarding a requirement. Rewrite it to express the approved obligation; bring any missing decision to the human for resolution.
