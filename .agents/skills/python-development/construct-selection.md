---
type: Playbook
description: How to select among thirteen declaration forms and distinguish named shapes and sites. Read before introducing program structure.
---

# Construct Selection

For each modeled declaration, name its meaning and select one of these thirteen forms. Do not add a declaration without a matching form.

Count declaration forms, not every named pattern or execution location. A self-typed field does not add a form beyond concept model; evaluating an expression at a named site does not declare another form.

| Meaning | Construct |
|---|---|
| One atomic meaning over a primitive or closed value space | [Semantic scalar](constructs/semantic-scalar.md) |
| Descriptive or measured product whose meaning is exhausted by field equality | [Value object](constructs/value-object.md) |
| Full domain thing, refinement, or durable fact | [Concept model](constructs/concept-model.md) |
| Closed alternatives on one semantic axis | [Union](constructs/union.md) |
| Strong alternative whose sole failure means the declared fallback | [Ordered union](constructs/ordered-union.md) |
| Sequence or association with collection-level meaning | [Collection](constructs/collection.md) |
| Pure implication from proven inputs to a constructed output | [Transformation](constructs/transformation.md) |
| Another system's differing representation | [Foreign model](constructs/foreign-model.md) |
| This program's published request or reply | [Contract model](constructs/contract-model.md) |
| Environment and deployment input | [Config](constructs/config.md) |
| Transport ingress and egress | [Route](constructs/route.md) |
| Execution of a typed action through an external capability | [Effect interpreter](constructs/effect-interpreter.md) |
| Description of one intended external effect | [Action](constructs/action.md) |

## Named Shape And Site

- [State transition](constructs/state-transition.md): a concept-model shape with a self-typed `prior` field, not another declaration form.
- [Composition root](constructs/composition-root.md): the `main.py` registration and per-input terminal-expression site, not another declaration form.
- Do not manufacture a wrapper declaration to turn either the shape or the site into another counted form.

## Sorting Laws

- A uniform closed vocabulary is a semantic scalar; alternatives with different facts form a union.
- A value object is exhausted by field equality; an independently referable thing, occurrence, or durable fact is a concept model.
- A plain tuple field is not a collection unless the collection itself has meaning.
- Matching foreign and domain meaning constructs the domain type directly. Differing names and nesting use foreign annotations and aliases; an actual semantic conversion requires a foreign-to-domain transformation.
- Publishing a domain model directly does not reclassify it as a contract model; create a contract model only for a distinct published projection.
- Admit ordered fallback only when every strong-variant refusal means that fallback over the declared input space; location does not grant permission.
- Model succession as a concept, not a verb-shaped wrapper. Keep authorization on the fact, effect execution in its interpreter, and callback registration at the composition-root site.
