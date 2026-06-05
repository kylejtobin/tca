# Type Catalog for Type Construction Architecture

A type catalog is the complete construction graph of a TCA program. Every domain value,
every event, every state, every foreign surface, every decision, and every outcome is a
type whose construction carries proof. The catalog is the bridge from a completed
foundation spec to code: it names the concrete shapes to build, in dependency order, as
the closed set of constructs the authority allows. It is the input to `tca-architect`'s
plan, which the forge agents render and `tca-review` audits. Code is
transcription from the catalog.

## Inputs

1. A completed Foundational Program Design spec (Scope, Strategy, Conditions, Premises,
   Domain Invariants)
2. Foreign API documentation (JSON schemas for every external surface the application
   touches)

These two inputs contain 100% of the information the catalog requires. Every name is a
PascalCase transcription of the spec's language. Every constraint is declared in an
invariant. Every foreign alias is documented in the API. If information appears absent,
it is in the inputs.

## Governing Principles

- **Names are transcriptions.** The spec says "order event," the type is `OrderEvent`.
  The spec says "ItemCount," the scalar is `ItemCount`. If a name cannot be derived from
  the spec's language, the spec has a gap.
- **Every domain value is a named scalar.** `LineNumber(RootModel[int])` with
  `Field(ge=1)`. Never bare `str`, `int`, `float`, `Decimal`, `bool`. Constraints live on
  the scalar, not on consuming models.
- **Computed values are both scalar and derivation.** `Subtotal` is a scalar type for
  identity and constraint. It is also a `@cached_property` on the frozen model that owns
  its inputs, constructing and returning a proven `Subtotal`.
- **Configuration values are domain scalars** composed into a frozen config model
  (`BaseSettings`). Not a separate concept; constructed once at startup, frozen, injected.
- **Every model is frozen** except the single active model of a context. A frozen model
  is a sealed proof: no mutation, no staleness.
- **States are structural unions.** Each state is a frozen-model variant whose disjoint
  fields carry identity. Construction selects the variant a value's fields satisfy; the
  fields absent from a variant are unrepresentable in that state. There is no `Literal`
  discriminator and no stored `kind` tag. The test: delete every kind-naming field and
  still land exactly one variant.
- **The type definition IS the adapter.** `Field(alias="foreign_key")` is the rename;
  nested declared models are the nested foreign structure; `from_attributes=True` and
  `model_validate_json` are the surface readers. No adapter layer, no procedural mapping.
  Two constructions cross the boundary: `model_validate_json` absorbs serialized bytes,
  `model_validate` lifts an object into domain truth.
- **Selection is structural.** A frozen `RootModel[A | B | C]` envelope lands the one
  variant a value satisfies; raw input crosses through it. There is no discriminator and
  no routing function. Behavior is read off the selected variant's own same-named
  derivation, never matched or switched.
- **Derivation belongs on the frozen model.** If a fact depends only on a model's proven
  fields, it is a `@property`, `@cached_property`, or `@computed_field` on that model. It
  takes only `self`, returns a declared type/union/proven model (never a bare `bool`,
  `str`, or `int`), and its body is a single returned expression.
- **A frozen model's derivation produces the next event in the graph.**
  `OrderEvaluation.fulfillment_intent` constructs and returns the proven action event. The
  model is the factory; the active model emits what the derivation already built.
- **A decision is a derivation returning a result union.** Both outcomes construct:
  `Approved | Denied(reason)`, not a `bool` and not "construct or publish nothing."
  Construction failure is reserved for *malformed input only*.
- **The live edge is confined to the active model.** I/O is not a "seam" and not a
  "handler." The single unfrozen active model of a context constructs frozen facts from
  live input and emits effects only after proof; results re-enter through a boundary model
  as a union read via variant derivations. There is no "seam" construct and no "handler."

## Invariant Decomposition

This is the center of the catalog. Every invariant in the spec takes one of three shapes.
The shape determines what constructs the invariant requires. None of the three shapes
introduces a "seam" or a "handler": the live edge, where one exists, is the named active
model, route, and boundary model of the authority's closed set.

### Pure Construction

The invariant IS a constraint on a frozen model. Construction succeeds and the invariant
is satisfied. Construction fails only when the input is malformed.

A frozen model that embodies a pure-construction invariant composes proven inputs as
fields: observation snapshots, state assessments, config models, state variants. It proves
the invariant because every field is a declared type and the composition is itself a
declared type; an impossible composition is not a validator firing but a structural union
of the legal variants. Its `@cached_property` derivations construct and return the action
events and result variants that follow from a successful composition.

An order-fulfillment gate is pure construction. A single frozen `OrderEvaluation` model
composes the order, the inventory snapshot, and the customer's credit posture, each a
declared type whose own construction already proved stock availability, the credit limit,
payment validity, and address eligibility. The decision is a derivation returning a result
union: `fulfillment_intent -> Approved | Denied`, where **both variants construct** and
each carries its own next-event derivation. The customer's fulfillment preference is itself
a **union**; each preference variant carries its own fulfillment derivation, so the proven
`ReserveStock | BackorderRequest` is read off the selected preference variant with no
`match` and no `if`. The active model's job is only to construct `OrderEvaluation` from
live input and emit the event the chosen result variant already built.

Every invariant that governs a decision without external I/O is pure construction. The
frozen model IS the invariant; the result union IS the decision.

### Decision, Effect, Outcome

The invariant governs a decision that triggers an external action with multiple possible
results. Three constructs compose this shape:

**The decision** is a derivation on a frozen model returning a result union. The model
composes proven inputs; its derivation constructs and returns the variant that holds —
`Approved | Denied(reason)`, both constructing. The action event that the effect will
carry is what the chosen variant's own derivation builds. The decision is construction, not
procedure.

**The effect** is the single I/O operation the active model emits after proof: a REST call,
a websocket send, a publish. The active model constructs the action event (or reads it off
the result variant), and only then emits it. The effect is confined to the active model; it
is never a free-standing "seam," and the active model contains no comparison or selection
around it.

**The outcome** is a structural union of the results that re-enter after the effect. Each
result is a frozen-model variant told apart by disjoint fields — no `Literal`
discriminator. The raw foreign result crosses through a boundary model and a frozen
`RootModel[A | B | C]` envelope lands the one variant it satisfies. Each variant carries
its own same-named next-event derivation: `StockReleased` carries the released balance and a
derivation resuming the prior evaluation, `StockAlreadyAllocated` carries the conflicting
allocation and a derivation that transitions state. The outcome union replaces branching on
the result.

An invariant governing reservation cancellation decomposes into: a `ReservationEvaluation`
whose `release_decision` derivation returns `ReleaseAuthorized | ReleaseRejected` (decision,
both construct), the inventory-system release call the active model emits after proof
(effect), and a `ReleaseOutcome = StockReleased | StockAlreadyAllocated` union re-entered
through a boundary model where each variant's derivation produces the next event (outcome).

Every invariant that involves external I/O decomposes into exactly these three constructs.
If a decision sits in the active model body as a comparison, a frozen model and its result
union are missing. If the outcome handling branches on the result, the outcome union is
missing.

### Temporal Persistence

The invariant requires a condition to persist across multiple events over a time window
measured by stream-derived timestamps.

The per-event evaluation IS a frozen model. A `BackorderEvaluation` whose construction
proves the threshold is breached on this event, using the correct metric (current on-hand
count, not projected on-hand). The per-event evaluation is pure construction, and whether
it breaches is a derivation returning a result union (`Breached | WithinThreshold`), both
constructing.

The live, multi-event tracking lives on the **active model** — the one node of the context
that meets time. It holds the breach-start timestamp (read from the event stream, never the
system clock) as evolving state, constructs the per-event evaluation on each event, reads
the elapsed-time derivation, and emits the escalation event after proof. The active model
body contains only construct / assign / read-derivation / emit; the elapsed comparison is
itself carried as a derivation returning a result union, not an `if`. This is not a "seam";
it is the active model, the named live node.

A temporal-persistence invariant decomposes into: a frozen per-event evaluation whose breach
check is a derivation returning a result union (`Breached | WithinThreshold`), and the active
model that holds the breach-start timestamp as evolving state and emits the escalation after
proof.

## Context Assignment

Derive contexts from the invariant map's active-model groupings — each active model, with
its routes, that constructs facts from subscribed events and emits published events is a
context. Assign each type its structural address (context + file) during extraction. The
context is the directory; the file is named for the domain concept the type represents, per
the naming principle in [program-topology.md](../docs/program-topology.md). If a type
cannot be assigned to a context, the context boundaries are not yet clear.

## Catalog Contents

The categories below are exactly the authority's closed construct set. Nothing is cataloged
that is not one of these. Projection (`model_dump` / `model_dump_json`) is the exit relation
by which typed truth leaves the graph as plain data; it is a use of a frozen model, not a
category.

### Scalars

Every constrained value in any invariant is a semantic scalar: a frozen `RootModel[P]` over
a single primitive, carrying a `Field(...)` constraint or a domain-meaningful name that
does real work, often both. Every configuration parameter is a scalar. Every computed value
is a scalar with a corresponding derivation on its parent model. The invariant names the
value; the constraint declares itself on the `Field`. A `RootModel[str]` with neither a
constraint nor a genuine name is primitive laundering, not a scalar.

### Collections

Every homogeneous immutable sequence that is a domain thing in its own right is a frozen
`RootModel[tuple[T, ...]]` whose element `T` is a declared type — a scalar or a model, never
a bare primitive. A sequence that carries its own constraints (non-emptiness, order, bounded
length) or a derivation it implies as a whole is the named `RootModel`; a plain sequence
field is `tuple[T, ...]` on its frozen model. A collection of primitives is the element left
unforged.

### Frozen Models

Every invariant that governs a decision IS a frozen model. The model composes proven inputs
as fields, each a declared type; its existence is the proof that every field's constraint
held together. The value object and the full domain model are this one construct at
different depths of composition. Its derivations construct the action events and result
unions that follow. There is **no validator slot**: a frozen model proves its invariant
because every field is a declared type and a forbidden composition is a structural union of
legal variants, never a `model_validator` checking conditions after the fact.

Every frozen model declares what invariants its construction enforces, what its derivations
produce (a constructed type, a result union, or a domain event), and which active-model
method emits the event a derivation builds, if any.

### Unions

Every state and every outcome is one structural-union construct. A union is a closed set of
two or more frozen-model variants, each a distinct structure, mutually disjoint under
`extra="forbid"`. The variant type is the kind: a `Filled` value is the filled case, never a
value carrying `kind="filled"`. Construction selects structurally through a frozen
`RootModel[A | B | C]` envelope that lands the one variant whose fields a value has and whose
foreign fields it lacks. There is **no discriminator field and no discriminator value**.
Fields present on a variant are required for that variant; fields absent are unrepresentable.
Transitions between state variants are triggered by domain events. Each variant carries its
own same-named derivation, read off the selected variant — never a `match`. The test: delete
every kind-naming field and still land exactly one variant.

### Boundary Models

Every external API surface IS a frozen boundary model that lifts foreign-shaped data into
domain truth in a single construction. Field names are domain names; aliases are the exact
foreign JSON keys from the API documentation. `model_validate_json` absorbs foreign bytes;
`model_validate` lifts an object into domain truth. The only procedural crossing permitted is
a `mode="before"` validator that **indexes into a transport wrapper to reach the payload
only — never renames and never computes**. It never retains a foreign handle as a field. The
same model facing outward is the API contract.

### Domain Events

Every event mentioned in any invariant's Home description is a domain event: a frozen model
whose fields are scalars and whose derivations construct further scalars or models. Each
event is published by one context's active model after proof and re-enters elsewhere through
a boundary model that proves it again. Events that form a closed set of results compose into
a structural union for variant-carried dispatch.

### Active Models

Each context has exactly one active model: the single unfrozen `BaseModel` where mutable live
state converges and the graph meets time. It holds transport clients, a database, a message
bus, and the evolving state a temporal invariant needs, as fields. It receives live input,
constructs frozen facts as proof, and emits effects only after proof, in `-> None` methods.
Its body is a sequence of single legal operations — construct a frozen fact, assign a
constructed value, read a derivation, emit an effect — with no comparison, no selection, and
no `match`. A second unfrozen node in one context is illegal.

### Config

Every configuration surface is a frozen `BaseSettings` model constructing typed scalar fields
from the environment, so configuration is proven the moment the program starts. Each field is
a declared scalar, never a bare primitive. The config root is constructed once, frozen, and
injected.

### Services, Routes, Composition Root

The thin wiring around the typed core. A **service** is a connection shim whose `connect`
binds a transport client to an active model; it owns no domain types and makes no decision. A
**route** is the ingress membrane that hands a raw request to a boundary model, dispatches
the constructed value to the active model, and projects the result back; it defines no types
and computes nothing. The **composition root** (`main.py`) is the single top of the wiring
graph: it instantiates concrete clients, hands them to services, constructs the active model,
and registers routes, holding no domain logic and no computation.

## Catalog Schema

```json
{
  "contexts": [
    {
      "name": "string (domain concept name)",
      "path": "domain/{name}/",
      "purpose": "string (what this context owns)",
      "has_type_py": "boolean",
      "has_value_py": "boolean",
      "active_model": "string or null (filename of the single active model)",
      "files": ["string (filenames in dependency order)"],
      "invariants": ["INV-N"]
    }
  ],

  "scalars": [
    {
      "name": "string (PascalCase transcription from spec)",
      "base": "string (Decimal, float, str, int, bool, bytes, datetime)",
      "root_model": true,
      "context": "string (context name)",
      "file": "type.py",
      "constraints": "string (Field args: gt=0, ge=0, le=1, min_length=1, etc.)",
      "source_invariants": ["INV-N"],
      "semantic_purpose": "string (what this value is in the domain)",
      "is_computed": "boolean",
      "computed_from": "string or null (parent model name if computed)"
    }
  ],

  "collections": [
    {
      "name": "string (PascalCase) or null (null if a plain tuple[T, ...] field)",
      "root_model": "boolean (true when named; false when a plain field)",
      "element_type": "string (declared scalar or model type, never a bare primitive)",
      "context": "string (context name)",
      "file": "string (filename, e.g. value.py)",
      "constraints": "string or null (min_length, max_length, order, etc.)",
      "derivation": "string or null (a fact the sequence implies as a whole)",
      "source_invariants": ["INV-N"]
    }
  ],

  "frozen_models": [
    {
      "name": "string (PascalCase)",
      "frozen": true,
      "context": "string (context name)",
      "file": "string (filename, e.g. value.py or evaluation.py)",
      "purpose": "string (what this model proves when it constructs)",
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (declared scalar, collection, union, or model type)"
        }
      ],
      "derivations": [
        {
          "name": "string (snake_case)",
          "returns": "string (constructed type, result union, or proven model)",
          "method": "string (@cached_property, @computed_field, @property)",
          "enforces_invariant": "INV-N",
          "produces_event": "string or null (domain event name if this derivation builds a publishable event)",
          "result_union": "string or null (result union name if this derivation is a decision)"
        }
      ],
      "construction_enforces": ["INV-N"]
    }
  ],

  "unions": [
    {
      "union_name": "string (PascalCase, e.g. ReservationState or ReleaseOutcome)",
      "envelope": "string (frozen RootModel[A | B | C] that lands the variant)",
      "context": "string (context name)",
      "file": "string (filename, e.g. state.py or outcome.py)",
      "variants": [
        {
          "model_name": "string (PascalCase; the variant type IS the kind)",
          "fields": [
            {
              "name": "string (snake_case)",
              "type": "string (declared scalar or model type)"
            }
          ],
          "structurally_absent": ["string (fields that do not exist on this variant)"],
          "transitions": [
            {
              "to": "string (target variant)",
              "on_event": "string (domain event name)"
            }
          ],
          "derivations": [
            {
              "name": "string (snake_case, shared name across variants)",
              "returns": "string (type name)",
              "produces_event": "string or null (next event in the graph)"
            }
          ]
        }
      ],
      "source_invariants": ["INV-N"]
    }
  ],

  "boundary_models": [
    {
      "source": "string (API endpoint or websocket channel)",
      "model_name": "string (PascalCase)",
      "frozen": true,
      "context": "string (context name)",
      "file": "string (filename, e.g. boundary.py)",
      "model_validator_before": "string or null (indexes into a transport wrapper to reach the payload only — never renames or computes; null if no wrapper)",
      "fields": [
        {
          "domain_name": "string (snake_case domain field name)",
          "alias": "string (exact foreign JSON key)",
          "foreign_type": "string (type in foreign JSON)",
          "lifts_to": "string (domain scalar type)"
        }
      ],
      "lifts_to_domain_model": "string (domain model or union this boundary lifts into via second construction)"
    }
  ],

  "domain_events": [
    {
      "name": "string (PascalCase transcription from spec)",
      "frozen": true,
      "context": "string (context name)",
      "file": "string (filename, e.g. event.py)",
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (scalar or composed type name)",
          "derivation": "string or null (@cached_property, @computed_field, or null)"
        }
      ],
      "published_by": "string (active model / context that emits this event after proof)",
      "subscribed_by": ["string (active model / context names)"],
      "source_invariants": ["INV-N"]
    }
  ],

  "active_models": [
    {
      "name": "string (PascalCase)",
      "frozen": false,
      "context": "string (context name, one active model per context)",
      "file": "string (filename, e.g. active.py)",
      "client_fields": [
        {
          "name": "string (snake_case)",
          "type": "string (transport client, database, bus, or model client type)"
        }
      ],
      "state_fields": [
        {
          "name": "string (snake_case evolving state, e.g. breach_start)",
          "type": "string (declared type)"
        }
      ],
      "methods": [
        {
          "name": "string (snake_case)",
          "signature": "-> None",
          "constructs": ["string (frozen fact / evaluation types built from live input)"],
          "reads_derivation": ["string (result union or next-event derivation read off a variant)"],
          "emits": ["string (effect: REST call, publish, websocket send) after proof"]
        }
      ]
    }
  ],

  "config": [
    {
      "name": "string (PascalCase, BaseSettings model)",
      "frozen": true,
      "file": "string (filename, e.g. config.py)",
      "fields": [
        {
          "name": "string (snake_case)",
          "type": "string (declared scalar type)",
          "env_source": "string (environment variable name)"
        }
      ]
    }
  ],

  "services": [
    {
      "name": "string (PascalCase connection shim)",
      "file": "string (filename, e.g. service.py)",
      "binds_client": "string (transport client type)",
      "to_active_model": "string (active model name)"
    }
  ],

  "routes": [
    {
      "name": "string (route/path identifier)",
      "file": "string (filename, e.g. route.py)",
      "boundary_model": "string (boundary model that constructs the raw request)",
      "dispatches_to": "string (active model method)",
      "projects": "string (frozen model projected back onto the transport)"
    }
  ],

  "composition_root": {
    "file": "main.py",
    "instantiates_clients": ["string (concrete client types)"],
    "constructs_active_models": ["string (active model names)"],
    "registers_routes": ["string (route names)"]
  },

  "invariant_map": [
    {
      "invariant": "INV-N",
      "carrying_construct": "string (the frozen model, union, scalar, or active model that carries this invariant)",
      "decision_derivation": "string or null (derivation that returns the result union)",
      "result_union": "string or null (e.g. Approved | Denied; both variants construct; null for inert constraints)",
      "active_model_method": "string or null (the -> None method that emits an effect for this invariant, null for pure construction with no I/O)",
      "active_model_residual": "string or null (ONLY construct / assign / read-derivation / emit. If this contains a comparison, selection, or match, a frozen model and its result union are missing)"
    }
  ]
}
```

## Validation

- Every constrained value in any invariant has a scalar with constraints on the type
- No field on any model uses a bare primitive; no collection holds bare-primitive elements
- Every computed value is both a scalar and a derivation on its parent frozen model
- Every configuration value is a scalar composed into a frozen `BaseSettings` config model
- Every event in any invariant Home is a domain event
- Every state and every outcome is a structural union: variants told apart by disjoint
  fields, selected through a frozen `RootModel[...]` envelope, with no discriminator field
  and no stored `kind` tag (delete every kind-naming field and one variant still lands)
- Every foreign surface is a boundary model whose aliases are the complete adapter and
  whose only procedural crossing indexes a transport wrapper to reach the payload (it never
  renames or computes)
- No frozen model carries a validator slot to prove its invariant; the composition is the
  proof and an impossible composition is a structural union of legal variants
- Every decision is a derivation returning a result union where both outcomes construct;
  construction failure is reserved for malformed input only
- Every invariant has an entry in the invariant map with a `carrying_construct`
- Every invariant with external I/O has an active-model method that emits the effect after
  proof
- Every active-model method body contains only construct / assign / read-derivation / emit.
  A body that contains a comparison, selection, or `match` means a frozen model and its
  result union are missing. This is the primary failure mode; it is the thing most likely
  to be wrong
- Every frozen model declares what invariants its construction enforces and what its
  derivations produce
- Every derivation that produces an event names that event in `produces_event`
- Every variant of a union carries its own same-named derivation; behavior is read off the
  selected variant, never switched
- Each context has exactly one active model; no second unfrozen node exists in a context
- Every type maps to a construct in the closed set (semantic scalar, frozen model,
  structural union, collection, boundary model, domain event, active model, service, route,
  config, composition root) and has a context and file assignment
- Every context's files list matches the types assigned to it; every scalar's file is
  `type.py`
- All names are PascalCase transcriptions from spec language

## Output Convention

The completed catalog is saved to `spec/type_catalog.json` at the repository root unless
otherwise specified. From there it feeds `tca-architect`'s ordered, reference-resolved
construction plan, which the forge agents render one construct each, and which
`tca-review` audits for procedure that should have been typed construction.
