# Type Catalog for Type Construction Architecture

A type catalog is the complete construction graph of a TCA program. Every domain value, every event, every state, every foreign boundary, every composed evaluation, and every outcome dispatch is a type whose construction carries proof. The catalog is the bridge between a foundational design spec and code. Code is transcription from the catalog.

## Inputs

1. A completed Foundational Program Design spec (Scope, Strategy, Conditions, Premises, Domain Invariants)
2. Foreign API documentation (JSON schemas for every external surface the application touches)

These two inputs contain 100% of the information the catalog requires. Every name is a PascalCase transcription of the spec's language. Every constraint is declared in an invariant. Every foreign alias is documented in the API. If information appears absent, it is in the inputs.

## Governing Principles

- **Names are transcriptions.** The spec says "signal event," the type is `SignalEvent`. The spec says "NormSpread," the scalar is `NormSpread`. If a name cannot be derived from the spec's language, the spec has a gap.
- **Every domain value is a named scalar.** `Price(RootModel[Decimal])` with `Field(gt=0)`. Never bare `str`, `int`, `float`, `Decimal`. Constraints live on the scalar, not on consuming models.
- **Computed values are both scalar and derivation.** `Microprice` is a scalar type for identity and constraint. It is also a `@cached_property` on the model that owns its inputs, constructing and returning a proven `Microprice`.
- **Configuration values are domain scalars** composed into a frozen configuration model. Not a separate concept.
- **Every model is frozen.** A frozen model is a sealed proof. No mutation. No staleness.
- **States are discriminated unions.** Each state is a separate frozen model with a `Literal` discriminator. Fields on the variant define what is valid in that state. Fields absent from the variant are unrepresentable in that state.
- **The type definition IS the adapter.** `Field(alias="foreign_key")` is the translation. `model_validator(mode="before")` is the normalization. `from_attributes=True` is the surface reader. No adapter layer. No procedural mapping. Two constructions cross the boundary: `model_validate_json` absorbs, `model_validate` lifts.
- **Dispatch is declared.** `Annotated[A | B | C, Field(discriminator="kind")]` replaces branching. Construction selects the variant.
- **Derivation belongs on the model.** If a computation depends only on a model's proven fields, it is a `@property`, `@cached_property`, or `@computed_field` on that model.
- **A composed model's derivation produces the next event in the graph.** `EntryEvaluation.entry_intent` constructs and returns a `MakerBuyIntent` or `IocBuyIntent`. The model is the factory. The handler publishes what the derivation already built.
- **The irreducible seam is the only handler content.** One I/O operation: a REST call, a websocket send, a stream temporal wait. Everything before the seam is construction. Everything after is dispatch. If a handler contains a comparison, evaluation, or selection, a composed model is missing.

---

## Invariant Decomposition

This is the center of the catalog. Every invariant in the spec takes one of three shapes. The shape determines what types the invariant requires.

### Pure Construction

The invariant IS a constraint on a composed model. Construction succeeds and the invariant is satisfied. Construction fails and no output exists. No seam. No handler logic.

A composed model that embodies a pure construction invariant composes proven inputs as fields: signal snapshots, regime assessments, configuration models, state variants. Its `model_validator` enforces the conditions the invariant declares. Its `@cached_property` derivations construct and return the action events that follow from a successful evaluation.

The entry gate is pure construction. A single `EntryEvaluation` model composes signal, regime, and risk posture. Its model_validator enforces signal convergence, spread tolerance, fee-adjusted expectancy, cascade direction, and data freshness simultaneously. If `EntryEvaluation` constructs, every gate passed. Its `entry_intent` derivation constructs and returns the proven `MakerBuyIntent` or `IocBuyIntent` via dispatch on regime.entry_method. The handler's entire job: attempt `EntryEvaluation` construction. If an object comes back, publish `entry_evaluation.entry_intent`. If construction fails, publish nothing.

Every invariant that governs a decision without external I/O is pure construction. The composed model IS the invariant.

### Decision, Seam, Dispatch

The invariant governs a decision that triggers an external action with multiple possible outcomes. Three types compose this shape:

**The decision model** is a frozen composed model whose construction or derivation produces an action event. The decision model composes proven inputs. Its construction validates conditions. Its derivation constructs the action event the seam will consume. The decision IS construction. It is not handler logic.

**The seam** is one irreducible I/O operation that consumes the action event. A REST call. A websocket send. One operation. The seam is the boundary where construction yields to the external world. It is the only content in the handler that is not construction.

**The outcome dispatch** is a discriminated union of results from the seam. Each outcome variant is a frozen model with a `Literal` discriminator. Each variant carries only the fields valid for that result. Each variant's derivations construct the next event in the graph. CANCELLED carries released balance and derivations that resume the prior evaluation. FILLED carries fill price and size and derivations that transition state. The outcome union replaces branching on the result.

An invariant governing resting order cancellation decomposes into: a `RestingOrderEvaluation` whose construction validates that conditions have degraded (decision), a REST cancel call (seam), and a `CancelOutcome = OrderCancelled | OrderFilled` union where each variant's derivations produce the appropriate next event (dispatch).

Every invariant that involves external I/O decomposes into exactly these three types. If the decision is in the handler, a composed model is missing. If the outcome handling is branching, a dispatch union is missing.

### Temporal Persistence

The invariant requires a condition to persist across multiple events over a time window measured by stream-derived timestamps.

The per-event evaluation IS a composed model. A `DrawdownEvaluation` whose construction proves the threshold is breached on this event. The evaluation uses the correct metric (BestBid for MtM, not Microprice). The evaluation is pure construction.

The persistence tracking across events is the handler's content: the breach start timestamp (from the event stream, never system clock) and the comparison on subsequent events. This is the irreducible temporal seam. It cannot be a single construction because it spans multiple events. But the evaluation on each event IS construction.

A temporal persistence invariant decomposes into: a composed evaluation model (pure construction, per event) and a temporal seam (handler tracks breach duration using event timestamps). The handler constructs the evaluation on each event. If the evaluation shows breach and the elapsed event-stream time exceeds the threshold, the handler publishes the halt event. The evaluation is construction. The temporal tracking is the seam.

---

## Catalog Contents

### Scalars

Every constrained value in any invariant is a scalar. Every configuration parameter is a scalar. Every computed signal value is a scalar (with a corresponding derivation on its parent model). The invariant names the value. The constraint declares itself on the `Field`.

### Domain Events

Every event mentioned in any invariant's Home description is a domain event. A domain event is a frozen model. Its fields are scalars. Its derivations construct further scalars or models. Each event is published by one handler and subscribed to by others. Events that share a discriminator field compose into a union for dispatch.

### State Types

Each state in the spec's state machine is a frozen model variant in a discriminated union. Fields present on a variant are required for that state. Fields absent from a variant are unrepresentable in that state. Transitions between variants are triggered by domain events.

### Composed Models

Every invariant that governs a decision IS a composed model. The model composes proven inputs as fields. Its construction validates the invariant's conditions. Its derivations construct the action events that follow. Composed models are the program. They are where invariants become construction.

Every composed model declares what invariants its construction enforces, what invariants its derivations enforce, what action event its derivation produces, and what seam consumes that action event (if any).

### Foreign Boundaries

Every external API surface IS a frozen foreign model. Field names are domain names. Aliases are the exact foreign JSON keys from the API documentation. `model_validate_json` absorbs foreign bytes. `model_validate` lifts into domain truth. Wrapper normalization is a `model_validator(mode="before")` on the foreign model. The type definition IS the complete adapter.

### Outcome Dispatches

Every seam that produces multiple possible results IS a discriminated union. Each variant carries fields valid for that outcome. Each variant's derivations construct the next event in the graph. The dispatch replaces branching on the result.

---

## Catalog Schema

```json
{
  "scalars": [
    {
      "name": "string (PascalCase transcription from spec)",
      "base": "string (Decimal, float, str, int, datetime)",
      "root_model": true,
      "constraints": "string (Field args: gt=0, ge=0, le=1, min_length=1, etc.)",
      "source_invariants": ["INV-N"],
      "semantic_purpose": "string (what this value is in the domain)",
      "is_computed": "boolean",
      "computed_from": "string or null (parent model name if computed)"
    }
  ],

  "domain_events": [
    {
      "name": "string (PascalCase transcription from spec)",
      "frozen": true,
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (scalar or composed type name)",
          "derivation": "string or null (@cached_property, @computed_field, or null)"
        }
      ],
      "published_by": "string (handler name)",
      "subscribed_by": ["string (handler names)"],
      "source_invariants": ["INV-N"]
    }
  ],

  "state_types": {
    "union_name": "string",
    "discriminator_field": "string",
    "variants": [
      {
        "discriminator_value": "string (Literal value)",
        "model_name": "string (PascalCase)",
        "fields": [
          {
            "name": "string (snake_case)",
            "type": "string (scalar or composed type)"
          }
        ],
        "structurally_absent": ["string (fields that do not exist on this variant)"],
        "transitions": [
          {
            "to": "string (target variant)",
            "on_event": "string (domain event name)"
          }
        ],
        "source_invariants": ["INV-N"]
      }
    ]
  },

  "composed_models": [
    {
      "name": "string (PascalCase)",
      "frozen": true,
      "purpose": "string (what this model proves when it constructs)",
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (model or scalar type)"
        }
      ],
      "model_validators": [
        {
          "validates": "string (what condition the validator enforces)",
          "enforces_invariant": "INV-N"
        }
      ],
      "derivations": [
        {
          "name": "string (snake_case)",
          "returns": "string (type name of constructed output)",
          "method": "string (@cached_property, @computed_field)",
          "enforces_invariant": "INV-N",
          "produces_event": "string or null (domain event name if this derivation constructs a publishable event)"
        }
      ],
      "construction_enforces": ["INV-N"],
      "consumed_by_seam": "string or null (seam operation that consumes this model's derived event, null for pure construction)"
    }
  ],

  "foreign_boundaries": [
    {
      "source": "string (API endpoint or websocket channel)",
      "model_name": "string (PascalCase)",
      "frozen": true,
      "populate_by_name": true,
      "model_validator_before": "string or null (what the model_validator(mode='before') normalizes, null if no wrapper)",
      "fields": [
        {
          "domain_name": "string (snake_case domain field name)",
          "alias": "string (exact foreign JSON key)",
          "foreign_type": "string (type in foreign JSON)",
          "lifts_to": "string (domain scalar type)"
        }
      ],
      "lifts_to_domain_model": "string (domain model this boundary lifts into via second construction)"
    }
  ],

  "outcome_dispatches": [
    {
      "union_name": "string (PascalCase)",
      "triggered_by_seam": "string (which seam produces these outcomes)",
      "discriminator_field": "string",
      "variants": [
        {
          "discriminator_value": "string (Literal value)",
          "model_name": "string (PascalCase)",
          "fields": [
            {
              "name": "string (snake_case)",
              "type": "string (scalar or type name)"
            }
          ],
          "derivations": [
            {
              "name": "string (snake_case)",
              "returns": "string (type name)",
              "produces_event": "string (next event in the graph)"
            }
          ]
        }
      ],
      "source_invariants": ["INV-N"]
    }
  ],

  "invariant_map": [
    {
      "invariant": "INV-N",
      "shape": "string (pure_construction, decision_seam_dispatch, temporal_persistence)",
      "decision_model": "string or null (composed model whose construction embodies the decision)",
      "seam": "string or null (the single irreducible I/O operation, null for pure construction)",
      "outcome_dispatch": "string or null (discriminated union of seam results, null if no seam or single outcome)",
      "handler_residual": "string or null (ONLY the seam I/O operation. If this contains a comparison, evaluation, or selection, a composed model is missing)"
    }
  ]
}
```

---

## Validation

- Every constrained value in any invariant has a scalar with constraints on the type
- No field on any model uses a bare primitive
- Every computed value is both a scalar and a derivation on its parent model
- Every configuration value is a scalar composed into a frozen configuration model
- Every event in any invariant Home is a domain event
- Every state in the state machine is a discriminated union variant with unrepresentable invalid states
- Every foreign surface is a boundary model where aliases and model_validators are the complete adapter
- Every invariant has an entry in the invariant map
- Every invariant with a decision has a composed model whose construction embodies that decision
- Every seam is one I/O operation
- Every seam with multiple outcomes has an outcome dispatch union
- Every outcome variant has derivations that produce the next event in the graph
- Every handler residual contains only a seam operation. A residual that contains a comparison, evaluation, or selection means a composed model is missing. This is the primary failure mode. It is the thing most likely to be wrong
- Every composed model declares what invariants its construction enforces and what event its derivation produces
- Every derivation that produces an event names that event in the `produces_event` field
- All names are PascalCase transcriptions from spec language

## Output Convention

The completed catalog is saved to `spec/type_catalog.json` at the repository root unless otherwise specified.
