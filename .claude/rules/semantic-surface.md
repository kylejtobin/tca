---
paths:
  - "**/domain/**"
---

# Semantic Surface Types — Models Whose Schema IS A Prompt

A **semantic surface type** is any model whose `model_json_schema()` is part of an LLM context — agent output schemas (structured outputs), tool parameter schemas, agent input schemas, evaluation rubric schemas. The schema IS the prompt. Field names ARE instructions. DU variant names ARE the output classifications the LLM selects between. Docstrings on fields and variants ARE structured-output schema content the LLM consumes.

## Properties

- **Declared surface status.** A semantic surface type is marked as such in the project's type catalog (or equivalent registry). Documentation-only — doctrine carries the discipline.
- **Naming stability.** A rename IS a retraining event. Schema drift silently degrades agent output. Renames have a migration plan as a precondition for their existence — what was the old shape, what is the new shape, how is downstream consumption updated, when is the cutover.
- **Schema minimalism.** Smaller surfaces are more stable. Unused fields are prompt noise. Every field on a semantic surface earns its place by being load-bearing for the LLM's output.
- **Docstring discipline.** Docstrings on semantic surface fields and variants are part of the LLM's input. Their audience IS the LLM. Reviewer-facing notes have a home outside the model body — module-level comments, design docs, the catalog entry.
- **No internal-only fields on the surface.** Internal computation has its home on a separate non-surface model. The semantic surface contains only what the LLM produces or consumes.

## Out of Bounds

- **Rename without a migration plan.** Field rename, variant rename, model rename absent a documented agent-output migration plan. The rename's blast radius IS the agent's output quality, invisible until production drift.
- **In-process field on the surface.** A field whose population, transformation, or consumption is internal-only, mixed into the same model as the LLM-facing fields. Its home is a separate non-surface composed model.
- **Docstring written for code reviewers.** A docstring whose audience is the human reviewer rather than the LLM. Reviewer notes have a home outside the model body.
- **Multi-purpose surface.** One semantic surface type serving more than one agent's input or output schema. Each agent surface has its own type.

## Reference

- CLAUDE.md — naming conventions, failure modes.
- Project type catalog — entries marked as semantic surface.
