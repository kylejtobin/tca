# 0047. A derived value is a derivation kind declared with its operands

Status: accepted

## Context

A line's total is its unit price times its quantity; an order's total is the sum of its lines. The business has these values, and a page must say them without writing arithmetic the checker cannot verify and the proof cannot read.

## Rejected

A `@computed_field` on a fact returning the arithmetic, `self.price.amount.root * self.line.quantity.root`: an expression on the page, typed by the checker and verified by nothing. A derivation kind whose computed field is typed by a type variable and returns the produced class: the bound class is not reachable at run time without a cast, and the produced value would enter the run under a second class.

## Decision

`Measure` is a fact whose `root` the framework computes from what it holds, read as `.root` like a scalar's. `Times[A, B]` holds `left: A` and `right: B` and its `root` is their product; `Sum[E]` holds `of: tuple[E, ...]` and its `root` is the sum of the elements' roots, zero for none. `A`, `B` and `E` are bounded to `Numeric`, a scalar over `Decimal` or `int` or another `Measure`, so a wrong operand is a checker error. A page declares the value as a subclass with its own classes as the parameters, `class LineTotal(Times[UnitPrice, Quantity])`, and the engine constructs it when its operands are in the run (0050), like any fact. A constant factor is a scalar with a default, given as the field's default on the subclass: `class Reduced(Times[LineTotal, Rate])` with `right: Rate = Rate()`. The result is read as a `Decimal`; the computation lives once, on the kind, and the page contains no expression.

## Evidence

`LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3)).root` is `Decimal("7.50")`. `Lines(of=(LineTotal 7.50, LineTotal 125.00)).root` is `Decimal("132.50")` and `Lines(of=()).root` is `Decimal(0)` for `class Lines(Sum[LineTotal])`. In the engine's shop, `LineTotal` was constructed once per line from the `UnitPrice` the catalog's record carried and the `Quantity` the line carried, and `Reduced` from `LineTotal` and its defaulted `Rate`; a one-line order of fifty gold dumped `{"total":"112.500","charges":["ch_1"],"cheapest":"125.00"}`.

## Consequences

Unwritable: arithmetic in a computed field on a page. A derivation the kinds do not express is a missing derivation kind, written once in the world. Refuted by a derived value that is not a `Decimal`; that is a derivation kind over another root type.
