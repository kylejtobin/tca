---
type: Playbook
description: How to select among thirteen declaration forms and distinguish named shapes and sites. Read before introducing program structure.
---

# Construct Selection

Before any class, write the noun table: one row per thing, with `name` in the practitioner's word, `is` in one sentence a domain expert accepts, `holds` as other rows, and `kind` from the table below. Consult the thirteen forms only for rows in the noun table. Do not add a declaration without a row and a matching form.

| name | is | holds | kind |
|---|---|---|---|
| Price | the amount per unit at which an instrument trades, above zero | a Decimal | semantic scalar |
| Fill | an execution of part of an order at a price and quantity | order, account, instrument, side, price, quantity | concept model |
| Position | one account's holding in one instrument, the fold of its fills | prior position or opening position, fill | concept model, state-transition shape |
| PersistPosition | the intended recording of a position in the ledger | position | action |
| PositionRecorded | the ledger's record of a position, acknowledged with a sequence | sequence, position | concept model |

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

## Steps Are Unnamed Nouns

A step you are about to write is a noun you have not named. Name what exists after it, holding the things that exist before it.

- A duty is one action and one outcome union, nothing else. Placing an order is `PlaceOrder` and `Filled | Refused`; the interpreter that performs it carries no meaning of its own.
- A sequence of steps is a chain of fields. The later fact holds the earlier fact; "then" is an annotation, not a statement.
- A choice is a union. Which variant constructed is the answer; no second type records it.

## Signals Of The Run

Run these on the noun table before selecting forms. A row that matches is the run wearing a noun: delete it and name what exists.

| Signal | The run | The thing |
|---|---|---|
| A type made of exactly one other type | `Persisted(position)` | `PositionRecorded(sequence, position)`: the request and what came back |
| An outcome family beside an action | `Place`, `Placed`, `PlaceFailed` | `PlaceOrder` and `Filled \| Refused` |
| Two empty variants in one union | `AtVersion \| NoStream \| AnyVersion` | `AtVersion \| Expectation`, the empty cases one `StrEnum` |
| A status vocabulary of moments | `pending`, `in_progress`, `done` | the condition that exists afterward, made of the facts that make it so |
| Mirrored pairs differing by the path that produced them | `BuyFilled`, `SellFilled` | `Fill(side, ...)` |
| A field whose value might not be there yet | `limit: Price \| None` | `limit: Price \| NoLimit` |
| A verb-named class holding prior and next | `AdvancePosition(prior, next)` | `Position(prior, fill)` |
| A name for what the program did | `Gathered`, `Published`, `Parsed`, `Consulted` | the thing gathered, published, parsed, consulted |
| More declarations than rows in the noun table | the surplus | the run; delete it |

## Sorting Laws

- A uniform closed vocabulary is a semantic scalar; alternatives with different facts form a union.
- A value object is exhausted by field equality; an independently referable thing, occurrence, or durable fact is a concept model.
- A plain tuple field is not a collection unless the collection itself has meaning.
- Matching foreign and domain meaning constructs the domain type directly. Differing names and nesting use foreign annotations and aliases; an actual semantic conversion requires a foreign-to-domain transformation.
- Publishing a domain model directly does not reclassify it as a contract model; create a contract model only for a distinct published projection.
- Admit ordered fallback only when every strong-variant refusal means that fallback over the declared input space; location does not grant permission.
- Model succession as a concept, not a verb-shaped wrapper. Keep authorization on the fact, effect execution in its interpreter, and callback registration at the composition-root site.
