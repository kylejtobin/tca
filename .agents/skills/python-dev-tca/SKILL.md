---
name: python-dev-tca
description: "Type Construction Architecture for Python. A program is declared as Pydantic types, and construction is the only operation. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists."
---

# Python Dev TCA

A program is a set of Pydantic types, and constructing them is the only operation. Each step you picture the program taking is a thing you declare: what exists after the step, holding what existed before it.

## Before any class

Write the noun table. One row for each thing.

| name | is | holds | kind |
|---|---|---|---|
| Fill | An execution of part of an order at a price and quantity. | OrderId, AccountId, InstrumentId, Side, Price, Quantity | concept model |
| Position | One account's holding in one instrument, the fold of its fills. | PositionState, Fill | concept model, state-transition shape |
| PersistPosition | The intended recording of a position in the clearing house. | Position | action |
| RecordedPosition | A position the clearing house recorded, with the sequence it assigned. | ClearingSequence, Position | concept model |

- `name`: the practitioner's noun. It becomes the class name.
- `is`: one sentence a domain expert accepts. It becomes the docstring.
- `holds`: other rows. They become the fields.
- `kind`: one of the forms under "For each row's kind". It gives the class shape.

Every meaning the program has is one row, and every row is one meaning.

The whole table for the example world, with its unions and derivations: [world/venue.md](world/venue.md).

## At each moment

Read the page, then write the classes it shows.

| You are about to… | Read | You declare |
|---|---|---|
| name a thing | [moments/naming.md](moments/naming.md) | the practitioner's noun for what exists |
| do this, then that | [moments/sequence.md](moments/sequence.md) | a later fact holding the earlier fact as a field |
| check whether | [moments/choice.md](moments/choice.md) | a union; construction picks the variant |
| handle it failing | [moments/refusal.md](moments/refusal.md) | a refusal variant in the reply and in the outcome |
| handle there being none | [moments/absence.md](moments/absence.md) | a named thing for the empty case |
| handle several | [moments/many.md](moments/many.md) | a tuple held whole, or one construction for each arrival |
| read what another system sent | [moments/ingress.md](moments/ingress.md) | a route or foreign model given the raw input |
| ask another system for something | [moments/effect.md](moments/effect.md) | an action, one interpreter, and the raw reply given to a union |
| get an id, a time, a random value | [moments/origin.md](moments/origin.md) | a field carried by what another system sent, or a derivation |
| keep something between arrivals | [moments/arrival.md](moments/arrival.md) | a prior read on each arrival, and a successor constructed from it |
| do what no form covers | [moments/missing-thing.md](moments/missing-thing.md) | the noun missing from the table |

## For each row's kind

| kind | The row is | Class shape |
|---|---|---|
| semantic scalar | one atomic meaning over a primitive or a closed vocabulary | [constructs/semantic-scalar.md](constructs/semantic-scalar.md) |
| value object | a product with no identity, equal when its fields are equal | [constructs/value-object.md](constructs/value-object.md) |
| concept model | a full domain thing, a refinement, or a durable fact | [constructs/concept-model.md](constructs/concept-model.md) |
| union | closed alternatives, each holding its own facts | [constructs/union.md](constructs/union.md) |
| ordered union | a strong alternative whose only failure means the fallback | [constructs/ordered-union.md](constructs/ordered-union.md) |
| collection | several with a meaning of their own | [constructs/collection.md](constructs/collection.md) |
| transformation | a derivation on the thing that holds its inputs | [constructs/transformation.md](constructs/transformation.md) |
| action | one intended external effect | [constructs/action.md](constructs/action.md) |
| foreign model | another system's thing, under its names | [constructs/foreign-model.md](constructs/foreign-model.md) |
| contract model | this program's published request or reply | [constructs/contract-model.md](constructs/contract-model.md) |
| config | deployment input | [constructs/config.md](constructs/config.md) |
| route | one transport crossing, in or out | [constructs/route.md](constructs/route.md) |
| effect interpreter | the one place an action's external call is made | [constructs/effect-interpreter.md](constructs/effect-interpreter.md) |

`main.py` is a site, with one page: [constructs/composition-root.md](constructs/composition-root.md).

## For every class

- Its `model_config`: [constructs/configuration.md](constructs/configuration.md).
- Its file: [constructs/placement.md](constructs/placement.md).

## Before reporting done

- Every row of the noun table has a declaration, and every declaration has a row.
- Every "In the file" line of every moment page you read is true of the file. [signals.md](signals.md) gives, for each line, the signal that it is false.
- The `smell-check` skill exits 0.
