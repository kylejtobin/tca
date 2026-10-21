# 0048. A rule over values is a relation kind, and its refusal is the other outcome

Status: accepted

## Context

A line over the threshold is discounted; an age is within the limits; an amount paid equals the amount due. A rule that compares values has two outcomes, and the page must declare both without a branch, a validator of its own, or an expression.

## Rejected

A `@computed_field` producing one of two constrained scalars from an expression (0002). A validator on the page. A relation whose refusal propagates as any other `ValidationError`: the run would end at the first line the rule did not hold for, instead of building the other outcome.

## Decision

`AtMost[A, B]`, `Beyond[A, B]`, `Between[A, L, U]` and `Equal[A, B]` are facts holding `value` and `bound`, or `value`, `lower` and `upper`, bounded to `Numeric`, with one `model_validator` each, written once on the kind, that raises a `PydanticCustomError` of type `relation` when the relation does not hold. A page declares the rule as a subclass with the compared classes as the parameters, `class Small(AtMost[LineTotal, Threshold])`, and each outcome as the fact that holds the relation that makes it true. The engine reads a refusal whose every error is `missing` or `relation` as the class not existing yet, so the fact holding the relation that holds constructs and the other is never built; where the outcome is held, the union is the choice (0003). `AtMost` and `Beyond` over the same operands are complements, which the proof reads as disjoint (0051); `Between`'s complement is `Beyond` on each side. A bound that is a business constant is a scalar with a default, given as the field's default on the subclass: `bound: Threshold = Threshold()`. `Only[E]` refuses the same way when its tuple does not hold exactly one element, so how many came back is a choice too (0049).

## Evidence

In the engine's shop, a line of three teas at 2.50 constructed `Small` and `FullPrice`; a line of fifty gold constructed `Large` and `Discounted`; a two-line order of both answered `{"total":"120.000","charges":["ch_1","ch_1"],"cheapest":"7.50"}` with the lines holding `FullPrice`, `Discounted`. `Allowed(value=Quantity(1), lower=Quantity(1), upper=Quantity(10))` and the same with `Quantity(10)` constructed; with `Quantity(11)` it raised one error of type `relation` with message "Quantity is over Quantity". `Same(value=Quantity(3), bound=Quantity(3))` constructed and with `Quantity(4)` raised `relation`.

## Consequences

Unwritable: a validator on a page; a comparison in a computed field. A rule the four kinds do not express is a missing relation kind, written once in the world. Refuted by a relation over values that are not numbers; that is a relation kind over another root type.
