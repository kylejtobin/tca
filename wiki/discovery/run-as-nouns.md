---
type: Reference
description: The run wearing nouns; a model that simulates the system running and labels each step with a construct name produces types that are the run and never the world, and the noun table is where that is caught.
---

# The Run as Nouns

A generator trained on procedure builds by simulating the system running, then labels each step of that simulation with a construct name. The types it produces are the run, not the world. Asked to state the principle, it states it correctly; asked to build, it does it again, because stating is retrieval and building is generation. The correction is an artifact that generation cannot skip, not a principle it can recite.

## The artifact

Before any class, the noun table: one row per thing, `name / is / holds / kind`, the [things](./things.md) schema with the construct kind appended. The thirteen forms are consulted only for rows in the table. A step about to be written is a noun not yet named; the row that replaces it names what exists after the step, holding the things that exist before it.

## Steps are unnamed nouns

- A duty is one action and one outcome union, nothing else. Placing an order is `PlaceOrder` and `Filled | Refused`; the interpreter that performs it carries no meaning of its own.
- A sequence of steps is a chain of fields. The later fact holds the earlier fact; "then" is an annotation, not a statement.
- A choice is a union. Which variant constructed is the answer; no second type records it.

## Signals of the run

Run on the noun table before selecting forms. A row that matches is the run wearing a noun: delete it and name what exists.

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

## The record

One session built an event-sourcing module and its NATS provider three times. Each pass produced the same shapes under new names: outcome facts named by participle, same-shaped sibling variants a union could not tell apart, meaning deferred to the interpreter, constructs serving a constraint instead of naming a thing, and removals made as compliance that re-emitted under new names on the next pass. Every advance in that session came when the output was a classification of existing nouns against Core, a sorting of a noun list into reused, refined, and new, a verb split into action and outcome, two graphs drawn as one. Every regression came when the output was a build. The table is the classification made mandatory before the build.
