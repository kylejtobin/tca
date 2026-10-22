# 0042. A computed field is a producer, and a class the run needs has exactly one

Status: accepted

## Context

A fact's field names a class the run must produce. The request is given, a record comes from the one action that hears it, and `Instant` and `Identity` construct themselves. A constrained scalar derived from held values, `LargeAmount` from a price and a quantity, has none of those sources.

## Rejected

The engine searching constructed instances for a value of the needed class. The engine converting a value to the needed class by its root. A validator on the fact. `Priced(total).root` on the page: basedpyright refuses a `Decimal` for a root typed as the union of two scalars.

## Decision

A computed field whose return type names classes produces them. `LinePriced.amount -> LargeAmount | SmallAmount` returning `Priced.model_validate(total).root` produces whichever member Pydantic chose: `model_validate` takes the value, the union chooses, and `.root` is typed as the union. After constructing a holder, the run keeps a computed field's value under `type(value)` when it is one of the declared classes, so the fact that holds that member becomes constructible and the fact that holds the other stays `missing` and is never built. The proof reads the return classes as what a class brings with it, and `proven` refuses a class two computed fields produce as `producer`, the way it refuses a record with two hearers.

## Evidence

`produced(Picked)`, for a fact with one computed field `which -> Amount | Limit`, returned `{"which": (Amount, Limit)}`, read from `model_computed_fields`. The proof's descent read follows a produced class to its producer, so a class a computed field returns belongs to the run its producer belongs to.

## Consequences

A derived value is a derivation kind (0047) and a rule over values is a relation kind (0048); a computed field that produces a class is a reply's word, or a value no kind derives. A computed field that returns a class no fact needs is harmless until one does, and then it must be the only producer. Refuted by nothing.
