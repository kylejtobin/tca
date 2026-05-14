# Type Catalog Extraction for Type Construction Architecture

A tool for translating a Foundational Program Design specification into a TCA type catalog. The output is a structured worksheet that serves as the blueprint for implementation. Every entry traces to an invariant. If it can't trace, it shouldn't exist.

Construction is proof. If the model exists, the invariant is satisfied. The goal is to move every invariant into construction constraints so that by the time a handler touches an object, the proof has already been carried by the types. Any invariant that remains in handler logic is a residual that must be explicitly justified in the enforcement map.

## Inputs Required

1. A completed Foundational Program Design spec (Scope, Strategy, Conditions, Premises, Domain Invariants)
2. Foreign API documentation (JSON schemas for every external surface the application consumes from or produces to)

These two inputs contain 100% of the information needed to complete the extraction. Every name, every constraint, every relationship is derivable from them. Do not stop to ask questions. Do not defer decisions. If information appears missing, re-read the inputs.

## Governing Principles

These are not suggestions. They govern every decision in the extraction.

- **Names derive from the spec.** Names are mechanical transcriptions from the spec's language into PascalCase. The spec says "signal event," the type is `SignalEvent`. The spec says "entry intent," the type is `EntryIntent`. The spec says "NormSpread," the scalar is `NormSpread`. If a name cannot be derived from the spec's language, the spec has a gap. Fix the spec, don't invent a name.
- **No bare primitives.** Every domain value gets a named scalar type. Never `str`, `int`, `float`, `Decimal` as a bare field type. Always `Price`, `NormSpread`, `Quantity`, etc. A field without semantic identity is a modeling failure.
- **Scalars own their own constraints.** `Price(RootModel[Decimal])` with `Field(gt=0)`. The constraint lives on the type, not on the handler that uses it. If a value appears in an invariant with a constraint, the scalar type carries that constraint.
- **Computed values are both a scalar type and a derivation.** Microprice is a type (`Microprice(RootModel[Decimal])` with `Field(gt=0)`) for semantic identity. It is also a `@cached_property` on the model that owns its inputs, returning a constructed `Microprice`. The scalar catalog gets the type. The parent model gets the derivation.
- **Configuration values are domain scalars.** `MaxSlippageTolerance(RootModel[Decimal])`. `DrawdownThreshold(RootModel[Decimal])`. The risk posture is a frozen composed model holding these scalars. "Conservative" and "aggressive" are different frozen instances with different values. Configuration is not special. It follows the same rules as every other domain value.
- **Frozen always.** Every model in the catalog is frozen. No mutation. No staleness. A frozen model is a sealed proof of the world at construction time.
- **States are discriminated unions, not enums.** Each state is a separate frozen model with a `Literal` discriminator. The state variant's fields define what is valid in that state. If `IN_POSITION` requires an entry price, the type demands it. Invalid states are unrepresentable because the wrong type literally cannot construct.
- **Foreign models mirror, then lift.** A foreign model uses `Field(alias=...)` to map foreign keys to domain field names. First `model_validate` absorbs foreign JSON into the foreign model. Second `model_validate` lifts into the domain model. Two constructions. The mapping IS the type definition.
- **Dispatch is declared, not branched.** If a handler would `if/elif` on a field to decide what type of event it's processing, that's a discriminated union. `Annotated[A | B | C, Field(discriminator="kind")]` replaces the branch. Construction selects the variant.
- **Derivation belongs on the model.** If a computation depends only on a model's proven fields, it's a `@property`, `@cached_property`, or `@computed_field` on that model. Never a service method. Never a utility function. Never computed externally.
- **Handlers are nearly empty.** They subscribe to events, attempt constructions, publish what succeeds. If a handler has significant logic, the type graph is incomplete.

---

## Process

### Step 1: Extract Domain Scalars

Read every invariant. Find every value that has a constraint or semantic identity. Each one becomes a `RootModel` scalar type. The name is the PascalCase transcription of what the spec calls this value. The spec says "momentum z-score," the scalar is `MomentumZScore`. The spec says "visible depth," the scalar is `VisibleDepth`. Do not invent names. Transcribe them.

Three sources of scalars:

**Constrained values from invariants.** INV-2 says NormSpread has a tolerance. INV-4 says position size can't exceed depth. INV-15 says MtM uses BestBid. Each constrained value is a scalar with constraints declared on the type itself.

**Configuration values.** Thresholds, tolerances, window durations, risk posture parameters. These are scalars composed into a frozen configuration model. They are not a separate concept.

**Computed values.** Microprice, OBI, ATR, momentum z-score. Each is BOTH a scalar type (for identity and constraint) AND a derivation on a parent model (for computation). Record the scalar here. Record the derivation relationship in Step 2.

For each scalar, record: name (PascalCase transcription from spec), base type, field constraints, which invariants reference it, and what it means in the domain.

### Step 2: Extract Domain Events

Read every invariant's Home description. Find every event type mentioned: what handlers subscribe to, what they publish. The name is the PascalCase transcription of the spec's language. The spec says "signal event," the type is `SignalEvent`. The spec says "halt event," the type is `HaltEvent`. The spec says "cancel intent," the type is `CancelIntent`.

For each event, record:
- Name (PascalCase transcription from spec)
- Fields (referencing scalar types from Step 1, never bare primitives)
- Which fields are derived (`@cached_property` / `@computed_field`) and what scalars they produce
- Which handler publishes it
- Which handlers subscribe to it
- Which invariants reference it

Derivations are key here. A `SignalSnapshot` event composes BestBid, BestBidSize, BestAsk, BestAskSize as proven scalar fields. Its `microprice` is a `@cached_property` that constructs and returns a `Microprice` scalar from those fields. Its `norm_spread` is a `@cached_property` that constructs and returns a `NormSpread`. The event model owns the computation. Downstream handlers receive proven derived values, not raw inputs they must compute themselves.

### Step 3: Extract State Types

Read the state machine from the spec. Each state named in the spec is a separate frozen model in a discriminated union. The discriminator value is the SCREAMING_SNAKE transcription of the spec's state name. The spec says "WATCHING," the discriminator is `"watching"`. The spec says "IN_POSITION," the discriminator is `"in_position"`. The model name is the PascalCase form.

For each state variant, record:
- Literal discriminator value (from spec's state name)
- Model name (PascalCase form of the state name)
- Fields that are required in this state (referencing scalar and event types)
- Fields that are structurally absent (not `Optional`, literally not on the type)
- Valid transitions: which event triggers transition to which other state variant

Test each variant: can an invalid state be represented? If `InPosition` can exist without an entry price, the type is wrong. If `Watching` can hold a position reference, the type is wrong. Unrepresentable invalid states are the goal.

### Step 4: Extract Composed Domain Models

Read every invariant that describes multiple conditions that must be true simultaneously for an action to occur. Each such invariant cluster implies a composed model whose construction enforces all conditions at once. The name describes the evaluation or context being composed, transcribed from the spec's language.

Identify these by reading the invariant Home descriptions. When a handler checks multiple conditions from multiple sources (signal values, regime assessment, configuration thresholds) before producing output, those conditions belong in a composed model whose construction IS the check. The handler attempts construction. If it succeeds, all conditions passed. If it fails, the handler produces nothing.

For each composed model, record:
- Name (PascalCase, derived from what the spec calls this evaluation or context)
- Composed fields (referencing other models: events, configuration, state)
- Derivations (what it computes, what scalar type each derivation returns)
- Which invariants its construction enforces (construction succeeds = invariant satisfied)
- Which invariants its derivations enforce

### Step 5: Map Foreign Boundary Types

Read the foreign API documentation. For every endpoint and channel listed in Input 2, create a frozen foreign model.

Each foreign model has:
- Field names matching domain scalar names from Step 1
- `Field(alias="foreign_key")` mapping to the exact foreign JSON key as documented
- `populate_by_name=True` on the model
- `@model_validator(mode="before")` if the foreign JSON has wrappers to unwrap

Record for each foreign model:
- Source endpoint or channel name
- Each field: domain name, foreign alias (exact key from docs), foreign type, which domain scalar it lifts to
- Wrapper unwrapping if needed

The foreign model is NOT the domain model. It owns the foreign shape. A second `model_validate` lifts it into domain truth. Two constructions, one boundary.

### Step 6: Map Construction Paths

Trace the full path from foreign JSON to domain truth to event publication:

1. Raw JSON bytes arrive (websocket or REST response)
2. `model_validate_json` → foreign boundary model (aliases absorb foreign keys)
3. `model_validate` → domain event model (scalars apply constraints, derivations compute)
4. Domain event publishes to event store
5. Handler receives domain event, composes into evaluation/context model
6. Evaluation model's construction enforces invariants
7. Derivations on evaluation model produce further domain events
8. Further domain events publish to event store

Record each path: source type, target type, construction method, what the construction proves, which invariants are satisfied at each step.

### Step 7: Map Enforcement

For every invariant in the spec (not some, every), determine how it is enforced:

**TYPE-ENFORCED (construction):** The invariant is satisfied if a specific model constructs. The constraint lives in the type definition, the field constraints, or the model validator. No handler logic needed.

**TYPE-ENFORCED (derivation):** The invariant is satisfied by a derivation on a model. The model owns the computation. The handler accesses the derived value but does not compute it.

**TYPE-ENFORCED (schema):** The invariant is enforced because the Pydantic model's schema makes invalid events unconstructable. An entry intent without a Microprice-derived price cannot exist because the schema requires it.

**TYPE-ENFORCED (union dispatch):** The invariant is enforced because a discriminated union routes to the correct variant structurally. No branching in handler code.

**HANDLER-ENFORCED:** The invariant requires logic that cannot be expressed as construction. Typically: temporal checks (freshness, confirmation windows), external side effects (REST calls, websocket operations), or cross-stream projections that span multiple event types. Each HANDLER-ENFORCED entry must state exactly what residual logic the handler performs and why it cannot be expressed as construction.

If HANDLER-ENFORCED entries outnumber TYPE-ENFORCED entries, the type graph is incomplete. Return to Steps 1-4 and look for missing scalars, compositions, or derivations.

---

## Worksheet Schema

```json
{
  "scalars": [
    {
      "name": "string (PascalCase, e.g. Price, NormSpread, MaxSlippageTolerance)",
      "base": "string (Decimal, float, str, int, datetime)",
      "root_model": true,
      "constraints": "string (Field args: gt=0, ge=0, le=1, min_length=1, pattern, etc.)",
      "source_invariants": ["INV-N"],
      "semantic_purpose": "string (what this value means in the domain)",
      "is_computed": "boolean (true if this scalar is also derived on a parent model)",
      "computed_from": "string or null (parent model name if is_computed, null otherwise)"
    }
  ],

  "domain_events": [
    {
      "name": "string (PascalCase event name)",
      "frozen": true,
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (scalar or composed type name, never bare primitive)",
          "derivation": "string or null (null if direct field, '@cached_property' or '@computed_field' if derived)"
        }
      ],
      "published_by": "string (handler name)",
      "subscribed_by": ["string (handler names)"],
      "source_invariants": ["INV-N"]
    }
  ],

  "state_types": {
    "union_name": "string (e.g. TradingState)",
    "discriminator_field": "string (e.g. 'status')",
    "variants": [
      {
        "discriminator_value": "string (Literal value)",
        "model_name": "string (PascalCase)",
        "fields": [
          {
            "name": "string (snake_case)",
            "type": "string (scalar or composed type name)"
          }
        ],
        "structurally_absent": ["string (field names that must NOT exist on this variant)"],
        "valid_transitions": [
          {
            "to": "string (target variant discriminator)",
            "trigger_event": "string (domain event name)"
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
      "purpose": "string (what semantic world this model represents)",
      "composed_fields": [
        {
          "name": "string (snake_case)",
          "type": "string (model name being composed)"
        }
      ],
      "derivations": [
        {
          "name": "string (snake_case)",
          "returns": "string (scalar or domain type name)",
          "method": "string (@property, @cached_property, @computed_field)",
          "enforces_invariants": ["INV-N"]
        }
      ],
      "construction_enforces": ["INV-N (invariants satisfied by successful construction)"]
    }
  ],

  "foreign_boundaries": [
    {
      "source": "string (API endpoint or websocket channel)",
      "model_name": "string (PascalCase, e.g. CoinbaseL2Update)",
      "frozen": true,
      "populate_by_name": true,
      "wrapper_unwrap": "string or null (model_validator description if wrapper exists, null if no wrapper)",
      "fields": [
        {
          "domain_name": "string (snake_case, matches domain field name)",
          "foreign_alias": "string (exact key from foreign JSON)",
          "foreign_type": "string (type in foreign JSON)",
          "lifts_to": "string (domain scalar type name)"
        }
      ],
      "lifts_to_domain_model": "string (domain event model this foreign model lifts into)"
    }
  ],

  "construction_paths": [
    {
      "step": "integer (order in the path)",
      "from_type": "string (source: 'raw JSON bytes', or a model name)",
      "to_type": "string (target model name)",
      "method": "string (model_validate_json, model_validate, @cached_property, etc.)",
      "proves": "string (what validity is established)",
      "source_invariants": ["INV-N"]
    }
  ],

  "enforcement_map": [
    {
      "invariant": "INV-N",
      "enforcement": "string (TYPE-ENFORCED:construction, TYPE-ENFORCED:derivation, TYPE-ENFORCED:schema, TYPE-ENFORCED:dispatch, HANDLER-ENFORCED)",
      "enforced_by": "string (type name or handler name)",
      "mechanism": "string (field constraint, model_validator, @cached_property, Literal discriminator, handler logic, etc.)",
      "residual_logic": "string or null (what the handler must still do and why it cannot be construction, null if fully type-enforced)"
    }
  ]
}
```

---

## Validation Checklist

- [ ] Every constrained value in any invariant has a scalar entry with constraints on the type
- [ ] No scalar uses a bare primitive (str, int, float, Decimal) without a named RootModel wrapper
- [ ] Every computed value appears both as a scalar AND as a derivation on its parent model
- [ ] Every configuration value is a scalar composed into a frozen configuration model
- [ ] Every event mentioned in any invariant Home has a domain event entry
- [ ] Every event field references a named type, never a bare primitive
- [ ] Every state in the state machine has a variant in the discriminated union
- [ ] Invalid states are unrepresentable (structurally_absent fields verified)
- [ ] Every foreign endpoint/channel has a boundary model with aliases
- [ ] Foreign models lift to domain models via a second construction, not procedural mapping
- [ ] Every construction path traces to at least one invariant
- [ ] Every invariant has an entry in the enforcement map
- [ ] TYPE-ENFORCED entries outnumber HANDLER-ENFORCED entries
- [ ] Every HANDLER-ENFORCED entry states why it cannot be construction
- [ ] No type exists that cannot trace to an invariant (no accidental types)
- [ ] No invariant exists without representation in the type graph (no gaps)
- [ ] Handlers contain minimal logic: subscribe, attempt construction, publish results
- [ ] All names are PascalCase transcriptions from spec language, none invented

## Output Convention

Save the completed worksheet to `spec/type_catalog.json` at the repository root unless otherwise specified. This file is the bridge between the foundational design spec and the implementation. Code is transcription from this worksheet.
