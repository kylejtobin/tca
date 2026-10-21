# 0049. A choice among elements is a selection kind

Status: accepted

## Context

The cheapest quote, the latest reading, the first match, the one result: a business chooses among several of one thing, and the page must name the chosen one without a loop, a comprehension or `min` in a computed field.

## Rejected

A `@computed_field` on the collecting fact with `min(self.of, key=...)`: an expression on the page. A selection whose chosen element enters the run under the element's class: the element's class exists once per element in a child run, and a second instance of it in the parent run is the same class in two scopes.

## Decision

`Least[E]` and `Greatest[E]` hold `of: tuple[E, ...]`, at least one, bounded to `Numeric`, and `chosen` is the element whose root is least or greatest, ties to the earliest. `First[E]` holds any elements and `chosen` is the first. `Only[E]` holds any elements, and refuses with `relation` unless there is exactly one, so `chosen` is the one. `chosen` is a property, not a computed field: the selection is read through the subclass that holds it, `self.of.cheapest.chosen`, and nothing enters the run under the element's class. A page declares the choice as a subclass with the element class as the parameter, `class Cheapest(Least[LineTotal])`; the engine collects the elements from the child runs and constructs the selection once per run, like any collecting fact (0044).

## Evidence

In the engine's shop, `Cheapest(Least[LineTotal])` was placed once per run by the proof and, for lines of tea 3, gold 50 and jam 2, chose the jam line's total: the reply dumped `"cheapest":"5.00"`. With `cheap`, `dear` and `cheap_again` of totals 1, 2, 1, `Dearest(Greatest[LineTotal])(of=...).chosen is dear` and `Cheapest(of=...).chosen is cheap`. `Opening(First[Line])(of=(tea, jam)).chosen is tea`. `Sole(Only[Line])(of=(tea,)).chosen is tea`; with two elements, and with none, it raised one error of type `relation`.

## Consequences

Unwritable: `min`, `max`, a comprehension or an index in a computed field on a page. A selection the four kinds do not express is a missing selection kind, written once in the world. Refuted by nothing.
