# 0047. A derived value is a derivation kind that declares one operation, computed at construction and read by the proof

Status: accepted

## Context

A line's total is its unit price times its quantity; an order's total is the sum of its lines. The business has these values, and a page must say them without writing arithmetic the checker cannot verify and the proof cannot read. The proof must also know what a derived value can be, or every relation over a derived value is one it cannot decide.

## Rejected

A `@computed_field` on a fact returning the arithmetic, `self.price.amount.root * self.line.quantity.root`: an expression on the page, typed by the checker and verified by nothing. A derivation kind whose computed field is typed by a type variable and returns the produced class: the bound class is not reachable at run time without a cast, and the produced value would enter the run under a second class. `root` as a `@property` on each kind with the arithmetic in its body: recomputed at every read, validated by nothing, and unreadable to the proof, which treated every derived value as unbounded and so could decide no relation over one. `root` declared as a field on `Measure` and redeclared on each kind: Pydantic keeps a redeclared field in the base class's position and validates it first, before the operands, so the operation was called with no operands (`KeyError: 'of'`).

## Decision

`Derived(operands, value, interval)` is a `NamedTuple`: the operand fields it reads, the function from their roots to the root, and the function from their intervals to the root's interval. It is the `default_factory` of a derivation kind's `root: Decimal` field, declared on the kind after its operands: Pydantic calls it with the validated operands and validates the result as a finite `Decimal`, so the root is computed once, at construction, and a non-finite result is refused. `Times[A, B]` holds `left: A` and `right: B` and `root` with `Derived(("left", "right"), multiplied, product_interval)`; `Sum[E]` holds `of: tuple[E, ...]` and `root` with `Derived(("of",), summed, sum_interval)`, zero for no element. `Measure` is the fieldless base every derivation kind subclasses, and declares `root: Decimal` for the checker only, under `TYPE_CHECKING`, so that `Numeric`, a scalar over `Decimal` or `int` or a `Measure`, has a root everywhere it is read. A page declares the value as a subclass with its own classes as the parameters, `class LineTotal(Times[UnitPrice, Quantity])`, and the engine constructs it when its operands are in the scope, like any fact. The proof reads the same `Derived` from `model_fields["root"].default_factory`: `interval(cls)` applies its `interval` to the operands' intervals, so a product of two non-negative values is bounded below by the product of their lower bounds, and a sum of non-negative elements by zero (0051).

## Evidence

On Pydantic 2.13.5: `LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3)).root` was `Decimal("7.50")` and its `model_dump()` was `{'left': Decimal('2.50'), 'right': 3}`, the root excluded. `Reduced(Times[LineTotal, Rate])` with `Rate` a constant of 0.9 gave `112.500` for a total of 125.00, and its required fields were `left` and `right`, so the engine seeds the constant (0057). `Lines(Sum[LineTotal])` over 7.50 and 125.00 was `132.50`, and over nothing `0`. `LineTotal.model_fields["root"].default_factory.operands` was `("left", "right")` and `Lines`'s `("of",)`. `Amount(Decimal("Infinity"))` was refused with `finite_number`. In the engine's test program, `Portion(Times[Share, Amount])` was `1.250` per part, `Portions(Sum[Portion])` was `2.500` per element, `Total(Sum[Amount])` over two elements was `5.00` and over none `0`; `interval(Portion)` was `Interval(low=Decimal(0))` from `Share` in (0, 1] and `Amount` above 0, and `interval(Total)` was `Interval(low=Decimal(0))`.

## Consequences

Unwritable: arithmetic in a computed field on a page; a derivation whose root the proof cannot bound. A derivation the kinds do not express is a missing derivation kind, written once in the world as a `Derived` with its value and its interval. Refuted by a derived value that is not a `Decimal`; that is a derivation kind over another root type.
