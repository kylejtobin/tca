# 0049. A choice among elements is a selection kind, and its shape is its tuple annotation

Status: accepted

## Context

The cheapest quote, the latest reading, the first match, the one result: a business chooses among several of one thing, and the page must name the chosen one without a loop, a comprehension or `min` in a computed field. How many elements a selection admits is part of what it is, and the proof must read it.

## Rejected

A `@computed_field` on the collecting fact with `min(self.of, key=...)`: an expression on the page. A selection whose chosen element enters the run under the element's class: the element's class exists once per element in a child scope, and a second instance of it in the parent scope is the same class in two scopes. A `model_validator` on `Selection` refusing an empty tuple with a custom `relation` error, and a second on `Only` refusing any count but one: rules written in Python the proof could not read, when the tuple annotation already says them.

## Decision

`Selection[E]` is a `Fact` every selection kind subclasses, holding `of: tuple[E, ...] = Field(min_length=1)`: Pydantic refuses an empty tuple with `too_short`, since a choice among nothing has no witness, so the selection does not exist and a fact that holds it does not either; a program declares the outcome for none or refuses an empty collection at the request. `Least[E]` and `Greatest[E]`, bounded to `Numeric`, choose the element whose root is least or greatest, ties to the earliest; `First[E]` chooses the first. `Only[E]` declares `of: tuple[E]`, the fixed-length tuple of one, and Pydantic refuses none with `missing` at `("of", 0)` and more with `too_long`. `chosen` is a property, not a computed field: the selection is read through the subclass that holds it, and nothing enters the run under the element's class. A page declares the choice as a subclass with the element class as the parameter, `class Cheapest(Least[LineTotal])`; the engine collects the elements from the child scopes and constructs the selection once per scope, like any collecting fact (0044), and reads a refusal of a selection as the fact not holding in that scope. The proof reads the shape from the annotation, `counts(cls)`: a fixed tuple's length, else `MinLen` and `MaxLen`, and reads two selections over one element class with disjoint counts as exclusive (0051).

## Evidence

On Pydantic 2.13.5: `Cheapest.model_validate({"of": ()})`, `Dearest` and `Opening(First[Line])` each raised one error, `too_short` at `("of",)`, "Tuple should have at least 1 item after validation, not 0"; `Sole(Only[Line]).model_validate({"of": ()})` raised `missing` at `("of", 0)`, "Field required"; `Sole` with two lines raised `too_long` at `("of",)`, "Tuple should have at most 1 item after validation, not 2". `Sole.model_fields["of"].annotation` was `tuple[Line]`; `Opening.model_fields["of"].metadata` was `[MinLen(min_length=1)]`. With `cheap`, `dear` and `cheap_again` of totals 1, 2, 1, `Cheapest(of=...).chosen is cheap` and `Dearest(of=...).chosen is dear`; `Opening(of=(tea, jam)).chosen is tea`; `Sole(of=(tea,)).chosen is tea`; `Cheapest(of=(cheap, dear)).model_dump()` had the one key `of`. In the engine's test program, `Largest(Greatest[Portion])` chose the part worth 1.250 of each element's two; with a party saying no parts, the run stalled naming `Largest`, "Largest did not hold: Tuple should have at least 1 item after validation, not 0", and the complement-less `High` that also refused was not named, since `Low` held (0053).

## Consequences

Unwritable: `min`, `max`, a comprehension or an index in a computed field on a page; a validator on a selection kind. A selection the four kinds do not express is a missing selection kind, written once in the world as a tuple shape and a `chosen`. Refuted by nothing.
