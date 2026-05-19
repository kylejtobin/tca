---
paths:
  - "**/domain/**"
---

# Evaluation Model — The Universal Layer 5+ Shape

An **Evaluation Model** is a frozen `BaseModel` whose role is composed proven inputs → typed result variant. Suffix: `*Evaluation`. The Evaluation Model IS the doctrinal home for every decision in the domain layer.

## Skeleton

```python
class FileEvaluation(BaseModel, frozen=True):
    # proven composed inputs
    context: FileContext
    invariants: tuple[Invariant, ...]
    config: AnalysisConfig

    @cached_property
    def result(self) -> EvaluationResult:
        # the body's shape is variant construction — possibly composing B.2 / B.3
        ...
```

## Properties

- **Frozen.** `frozen=True`. Not the active model of any bounded context.
- **Composed proven inputs as fields.** Proven scalars, value objects, frozen models, configuration models, projections. Bare primitives have no home as Evaluation Model fields. Collections of bare primitives have no home either — narrow the element type.
- **One or more `@cached_property` derivations whose return type IS a typed result variant.** DU, typed tuple, or proven model. `bool`, `int`, `str`-with-contextual-meaning are not admissible return shapes.
- **`@cached_property` alone — NOT `@computed_field` + `@cached_property`.** The Evaluation Model is internal compute substrate. The wire shape is the produced intent or event on its own frozen model with its own serialization. The Evaluation Model itself has no place in `model_dump()` output.
- **Zero decision-validators.** Construction succeeds for every well-formed input set. A `model_validator(mode="after")` comparing a proven field against a configured threshold is a decision in the wrong shape — its home is a `@cached_property` returning a `*Result` or `*Decision` variant.
- **Rare A.3 integrity-validator only — impossible variant composition.** The documented case is `StateTransition`, whose validator rejects cells where two individually-valid proven values cannot coexist as a meaningful state. Never for thresholds, never for business decisions.

## Derivation Body Shape

The `@cached_property` body composes variant construction. For the variant-owned part of the dispatch — value-local dispatch on an enum, or polymorphic dispatch through a DU discriminator — the body composes **B.2 smart enum methods** and **B.3 smart variant methods**.

The **F-Test** (CLAUDE.md) names the boundary: a method whose signature is satisfied by the variant value plus proven scalars or proven value objects, with no reference to the composed model's `self`, has its home as a variant method (B.2 or B.3). A method whose signature requires the composed model's `self` has its home as a `@cached_property` on the Evaluation Model (B.1), which may itself compose B.2 or B.3 for the variant-owned slice.

## Out of Bounds

- **Second active model in the bounded context.** The Evaluation Model is frozen by construction. A second unfrozen model in the same context has no home.
- **`model_validator` encoding a decision.** Construction failure as a decision channel. The decision's home is a `@cached_property` returning a typed result variant; construction itself succeeds.
- **Derivation returning a primitive.** `bool`, `int`, `str` carrying contextual meaning, raw `Decimal`. The variant's existence carries the answer; the primitive erases the discriminator.
- **Consumer re-branching on `.kind`.** `if result.kind == "passed"` against a discriminated union Pydantic has already narrowed. The consumer's branch point IS the variant — `match`/`case` or per-variant dispatch.
- **Function in `service/` or `api/` computing what is an Evaluation Model derivation.** The derivation's home is the Evaluation Model. A function reading proven fields and producing a result has escaped its model.

## Reference

- CLAUDE.md — Proof Hierarchies (B), Evaluation Model Template, F-Test, Two Smart-Method Patterns.
- `.claude/rules/gate-rubrics.md` — Type Integrity Gate, Construction Carries Meaning Gate.
