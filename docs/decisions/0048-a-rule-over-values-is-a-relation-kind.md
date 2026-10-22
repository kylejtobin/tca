# 0048. A rule over values is a relation kind, and its refusal is the other outcome

Status: accepted

## Context

A line over the threshold is discounted; an age is within the limits; an amount paid equals the amount due. A rule that compares values has two outcomes, and the page must declare both without a branch, a validator of its own, or an expression.

## Rejected

A `@computed_field` producing one of two constrained scalars from an expression (0002). A validator on the page. A relation whose refusal propagates as any other `ValidationError`: the run would end at the first line the rule did not hold for, instead of building the other outcome.

## Decision

`Relation` is a `Fact` every relation kind subclasses, declaring `constraints`, its meaning as `Constraint`s between its operand fields: `less - than <= by`, or `<` when `strict`. `AtMost[A, B]`, `Beyond[A, B]`, `Between[A, L, U]` and `Equal[A, B]` are relations holding `value` and `bound`, or `value`, `lower` and `upper`, bounded to `Numeric`, with one `model_validator` each, written once on the kind, that raises a `PydanticCustomError` of type `relation` when the relation does not hold, and with their constraints declared beside it: `AtMost` is `value - bound <= 0`, `Beyond` is `bound - value < 0`, `Between` is `lower - value <= 0` and `value - upper <= 0`, `Equal` is both directions non-strict. A page declares the rule as a subclass with the compared classes as the parameters, `class Small(AtMost[LineTotal, Threshold])`, and each outcome as the fact that holds the relation that makes it true. The engine reads a refusal whose every error is `missing` or `relation` as the class not existing yet, so the fact holding the relation that holds constructs and the other is never built; where the outcome is held, the union is the choice (0003). The proof reads a relation's constraints and its operands' bounds (0051), and names no kind: a relation kind written outside the world subclasses `Relation` and declares its constraints the same way, and one that declares none is refused as `undecidable`. A bound that is a business constant is a scalar with a default, given as the field's default on the subclass: `bound: Threshold = Threshold()`.

## Evidence

`Low(AtMost[Amount, Limit])` with a limit of 10: the engine's test program valued an element at 2.50 as `Cheap`, holding `Low`, and an element at 25 as `Dear`, holding `High(Beyond[Amount, Limit])`. `Allowed(value=Quantity(1), lower=Quantity(1), upper=Quantity(10))` and the same with `Quantity(10)` constructed; with `Quantity(11)` it raised one error of type `relation` with message "Quantity is over Quantity". `Same(value=Quantity(3), bound=Quantity(3))` constructed and with `Quantity(4)` raised `relation`. `Near[A, B](Relation)` declaring no constraints, subclassed as `Undecided(Near[Amount, Limit])`: `proven` raised `undecidable` at `("Undecided",)`.

## Consequences

Unwritable: a validator on a page; a comparison in a computed field. A rule the four kinds do not express is a missing relation kind, written once in the world. Refuted by a relation over values that are not numbers; that is a relation kind over another root type.
