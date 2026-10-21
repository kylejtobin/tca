# 0042. A computed field is a producer, and a class the run needs has exactly one

Status: accepted

## Context

A fact's field names a class the run must produce. The request is given, a record comes from the one action that hears it, and `Instant` and `Identity` construct themselves. A constrained scalar derived from held values, `LargeAmount` from a price and a quantity, has none of those sources.

## Rejected

The engine searching constructed instances for a value of the needed class. The engine converting a value to the needed class by its root. A validator on the fact.

## Decision

A computed field whose return type names classes produces them. `Placed.amount -> LargeAmount | SmallAmount` returning `Priced(total).root` produces whichever member Pydantic chose. `produces(cls)` lists only the computed fields that name a class. The proof reads them as what a class produces, follows a needed class to its producer, and refuses a class with two producers as `producer`, the way it refuses a record with two hearers. After constructing a holder, the run keeps a computed field's value when `type(value)` is one of the declared classes; a fact that needs the member not produced is skipped (0003).

## Evidence

`producers(shop)` mapped `LargeAmount` and `SmallAmount` to `Placed`. For quantity 3 the run held a `SmallAmount` and constructed `FullPrice`; for quantity 50 it held a `LargeAmount` and constructed `Discounted`; each run performed `Quote` once and `Charge` once. A route whose fact needed `Amount`, which `Discounted.total` and `FullPrice.total` both return, was refused at proof time with "2 computed fields produce Amount; exactly one must".

## Consequences

A derived value with a rule is a computed field typed as a union of constrained scalars. A computed field that returns a class no fact needs is harmless until one does, and then it must be the only producer. Refuted by nothing.
