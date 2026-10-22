# 0049. A choice among elements is a selection kind

Status: accepted

## Context

The cheapest quote, the latest reading, the first match, the one result: a business chooses among several of one thing, and the page must name the chosen one without a loop, a comprehension or `min` in a computed field.

## Rejected

A `@computed_field` on the collecting fact with `min(self.of, key=...)`: an expression on the page. A selection whose chosen element enters the run under the element's class: the element's class exists once per element in a child run, and a second instance of it in the parent run is the same class in two scopes.

## Decision

`Selection[E]` is a `Fact` every selection kind subclasses, holding `of: tuple[E, ...]`, with one `model_validator` on the base that refuses with `relation`, "no element to choose from", when there is none: a choice among nothing has no witness, so the selection does not exist, and a fact that holds it does not either; a program declares the outcome for none or refuses an empty collection at the request. `Least[E]` and `Greatest[E]`, bounded to `Numeric`, choose the element whose root is least or greatest, ties to the earliest; `First[E]` chooses the first; `Only[E]` adds its own validator and refuses with `relation` unless there is exactly one. `chosen` is a property, not a computed field: the selection is read through the subclass that holds it, and nothing enters the run under the element's class. A page declares the choice as a subclass with the element class as the parameter, `class Cheapest(Least[LineTotal])`; the engine collects the elements from the child runs and constructs the selection once per run, like any collecting fact (0044). The proof reads `Selection`, like `Relation` and `Record`, as a class that can be absent from a run that holds its parts.

## Evidence

`Least[Amount](of=())`, `Greatest[Amount](of=())`, `First[Element](of=())` and `Only[Element](of=())` each raised one error of type `relation`. With `cheap`, `dear` and `cheap_again` of totals 1, 2, 1, `Dearest(Greatest[LineTotal])(of=...).chosen is dear` and `Cheapest(of=...).chosen is cheap`. `Opening(First[Line])(of=(tea, jam)).chosen is tea`. `Sole(Only[Line])(of=(tea,)).chosen is tea`; with two elements it raised one error of type `relation`.

## Consequences

Unwritable: `min`, `max`, a comprehension or an index in a computed field on a page. A selection the four kinds do not express is a missing selection kind, written once in the world. Refuted by nothing.
