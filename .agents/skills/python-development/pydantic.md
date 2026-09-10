---
type: reference
---

# Pydantic execution substrate

## Governing reading

In TCA, Pydantic is the runtime that executes the declared construction graph. Annotations declare dependencies, models declare constructed facts, fields declare construction edges, and a constructor call evaluates the reachable graph. Success returns a graph of proven domain values. Failure returns no domain value.

Pydantic calls this process validation, but it guarantees the constructed output, not the input. Read `model_validate`, `model_validate_json`, `validate_python`, and `validate_json` as constructors. Their API names do not determine their architectural meaning.

Pydantic is not a preliminary validator in front of the program. The constructed models are the program's values, and constructing them is domain execution.

## The executable graph

At model declaration, Pydantic turns annotations, `Field` metadata, model configuration, collection shapes, and union metadata into a core schema. At construction, `pydantic-core` executes that schema recursively:

- a `RootModel` constructs one atomic meaning
- a `BaseModel` constructs a product from its declared dependencies
- a nested annotation creates a construction edge to another declared type
- a tuple or dict annotation constructs its members
- a discriminated union selects the constructor named by the input's identity
- a left-to-right union attempts constructors in declared order
- an alias or `AliasPath` declares how foreign structure reaches a field
- a default settles the declared meaning of omission
- `frozen=True` preserves the proof after construction

The outer value exists only after every required constituent has constructed. No intermediate primitive, dict, partial model, or failed case moves forward.

## One outer call

Given the [foreign model](foreign-model.md) declarations for `VenueFillMessage`, `VenueFill`, and their semantic-scalar fields:

```python
message = VenueFillMessage.model_validate_json(raw)
```

Read the call as this graph execution:

```text
raw transport bytes
└── VenueFillMessage
    └── data.payload
        └── VenueFill
            ├── ordId → OrderId
            ├── acct  → AccountId
            ├── px    → Price
            └── qty   → Quantity
```

One construction decodes the transport representation, traverses its wrappers, resolves its aliases, constructs every semantic scalar, proves every scalar constraint, constructs the nested foreign model, and freezes the completed graph. It does not validate a payload and then require a parser, mapper, normalizer, or domain constructor to finish the work.

Where the foreign shape already matches the domain shape, the domain model itself is the outer constructor and no foreign model exists.

## Construction is execution

Construction does more than admit data at ingress. A newly constructed model can be the next fact in an execution:

```python
self.latest = Position(prior=self.latest, fill=report)
```

`Position` is not a record emitted by a procedure. It is the successor fact. Its `prior` field carries the previous proven state, its `fill` field constructs the declared `Fill` from the venue fact, and its existence proves that the transition's dependencies were present. Repeating this construction produces an immutable recursive history.

Model-owned [derivations](derivation.md) execute the rest of the frozen graph on demand. A `@property` derives a cheap fact each time it is read; a `@cached_property` derives a costly or recursive fact once from the proven fields. A recursive derivation reaches the full history through its declared dependencies, without a runner loop walking states or a pipeline accumulating intermediate values.

The constructor graph is eager: constituents must construct before the outer value exists. The derivation graph is demand-driven: a fact is computed when read from its owner. Both are domain execution because both are determined by the structure of declared types.

## Construction selects

Selection belongs to construction, not to a consumer after construction:

- a [union](union.md) discriminator selects and constructs the identified variant
- an [ordered union](ordered-union.md) attempts the stronger constructor first and constructs the first inhabitable variant
- a closed semantic scalar constructs one member of its declared value space
- a declared default settles omission without admitting `None`

The resulting value carries the selected case. A later `match`, `if` ladder, `isinstance` ladder, routing validator, or handler re-decides what construction already proved.

`TypeAdapter` is the constructor for a union alias when raw data arrives without a containing model. It defines no domain structure and makes no decision beyond executing the alias's declared schema.

## Whole foreign lifts

The graph consumes foreign input whole:

- `model_validate_json` constructs from serialized bytes or text
- `model_validate` constructs from an arrived Python shape
- `from_attributes=True` constructs from an object's declared attributes
- `Field(alias=...)` declares a foreign key rename
- `validation_alias` declares a transport wrapper
- `AliasPath` declares a path through nested wrappers
- nested foreign models declare nested foreign structure

If this declarative inventory can reach the value, no parser, mapper, adapter, translator, field-copying function, or before-validator exists. Nothing reads the foreign object after its declared model has constructed.

At other boundaries the same substrate constructs environment facts through [config](config.md), constructs bare aliases through `TypeAdapter`, and serializes contract values at a [route](route.md) or binding. `@computed_field` includes an owned derivation in a contract's serialized shape; it does not make serialization a domain operation.

## Refusal is not a domain result

A successful construction returns the witness that its constraints held. A `ValidationError` means no witness was constructed. It is never caught to manufacture a default, flag, partial object, retry value, or domain refusal.

A domain no is itself a constructible fact: a union variant or ordered-union outcome carrying what that refusal means. Construction failure proves nothing and propagates.

The following APIs bypass proof and are forbidden:

- `model_construct`, which allocates a model without executing its construction schema
- `model_copy(update=...)`, whose update is not constructed or checked
- `Any`, `SkipValidation`, or another annotation that removes a domain edge from the executable schema
- mutation of a frozen value after its construction

State evolves by constructing a successor and re-pointing the [consistency model](consistency-model.md) to it, never by copying a model with unchecked updates.

## The substrate boundary

Pydantic executes declared construction. It does not own time, clients, effects, or arbitrary workflow.

- frozen models construct and derive facts
- the single consistency model holds live clients and current proven state
- a [verb](verb.md) admits an arrived fact, constructs at most one successor, re-points state, and emits the proven fact
- routes and bindings perform transport construction and serialization

The Pydantic API is larger than TCA's legal vocabulary. A custom validator being possible does not give escaped meaning a structural home. Reparameterize cross-field relations, use aliases and unions for structural selection, and report an invariant the construct set cannot prove.

## Mandatory vocabulary

- Not “validate the payload”; **construct the declared fact from transport input**.
- Not “coerce nested data”; **construct the declared constituent**.
- Not “map into the domain model”; **lift the foreign shape whole**.
- Not “run validators”; **execute the construction graph**.
- Not “handle validation failure”; **no domain value was constructed**.
- Not “parse and then construct”; **the outer construction consumes the foreign representation**.
- Not “process the next step”; **construct the fact whose dependencies are already proven**.

## Reader protocol

Before writing or reviewing Pydantic code:

1. Name the outer fact whose existence is required.
2. Trace its annotated fields, collection members, and variants down to semantic-scalar leaves.
3. Identify the one outer construction call that can receive the available input.
4. Let annotations construct every reachable constituent inside that call.
5. Before proposing a mapper or validator, identify the missing structural node or edge.
6. Before proposing a branch, identify the union whose construction should select the case.
7. Pass only the completed constructed value onward.
8. Put facts implied by proven fields in derivations on their owner.
9. Keep time and effects at the one live boundary.
10. Run a substrate probe for every behavioral assumption.

## Substrate claims

Probe the installed Pydantic version before relying on construction behavior. A probe constructs the smallest declared shape, observes the resulting runtime types and serialized identity, and records refusal where construction must fail. Probe nested construction, aliases, discriminators, ordered-union order, defaults, freezing, and round trips at the exact substrate surface the design uses.

The probe establishes what Pydantic executes. The domain model decides what that execution means.
