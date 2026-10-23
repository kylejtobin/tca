# type-construction-world

Retained declarative value and computation primitives, written as Pydantic classes. This package is a reusable component. It is not a complete application framework, and it does not commit the repository to the engine or public API that previously surrounded it.

## What is here

- **Values.** `Scalar` is one primitive with an invariant. `Setting` is a lenient scalar for a value supplied as text. `Value` is a composite part. `Record` is what an external party says, under that party's names. `Fact` is a conclusion made of the values it holds. `Duration` is a positive `timedelta`. A constant is a `Scalar` with a default root.
- **Derivations.** `Times` and `Sum` hold a value computed from their operands at construction. A value given for a computed field is refused.
- **Relations.** `Under`, `AtMost`, `Equal`, `AtLeast`, `Beyond` and `Differs` compare two values, and `Between` relates three. Each admits some orderings and refuses the others with the error type `REFUTED`.
- **Selections.** `Least`, `Greatest`, `First` and `Only` choose among the elements of a supplied finite tuple. They do not establish that the tuple is the complete content of an external source.
- **Supporting machinery.** `Computation`, `Derived`, `Comparison`, `Shape`, `Condition`, `Interval`, `Refusals`, `Refutable`, `Relation`, `Compare`, `Measure`, `Selection`, `COMPUTED` and `REFUTED`.

Every class is strict, frozen and refuses undeclared fields, except `Setting`, which accepts text.

## A small model

A payment that covers an order, using only the retained primitives:

```python
class Order(Value):
    id: OrderId
    total: Total


class PaymentCaptured(Record):
    """What the provider says, under the provider's names."""

    order: OrderId = Field(alias="order_id")
    amount: Paid


class Covers(AtLeast[Paid, Total]):
    """The payment is at least the total."""


class ShippingAuthority(Fact):
    order: Order
    payment: PaymentCaptured
    covered: Covers
```

`Covers` built from a payment of 50 and a total of 50 constructs. Built from 20 and 50 it is refused with `REFUTED`. Nothing here binds that `Covers` to the `order` and `payment` held by `ShippingAuthority`, or checks that the payment names that order. Those bindings are a requirement of the future engine.

## What is not here

Invocation execution, evidence admission, persistence, external-system capabilities and interface projection are not implemented in this tree. The previous request-based engine, command line, HTTP package and demo were removed and remain in Git history as reference material only. The target architecture is in [`docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`](../../../docs/TCA_ARCHITECTURAL_FOUNDATIONS.md), and the behavior a replacement must meet is in [`docs/REFACTOR_ACCEPTANCE.md`](../../../docs/REFACTOR_ACCEPTANCE.md).

The package needs no runtime configuration.
