<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

**Every layer of your service has something that checks it, except the one where your logic lives. TCA is an attempt to make that layer a set of types.**

> **Status: mid-refactor.** The first runtime ran a business program inside one request. It has been removed. Its replacement runs a program across events, time and failure, and it is not built yet. The idea below is unchanged. [What exists today](#where-it-stands) is small and stated plainly.

## The idea

You describe your business in Pydantic types: the values, the facts that follow from them, and the rules that must hold. A fact can only be constructed from the things that justify it, so the model says what the business is allowed to conclude. The framework's job is to carry that model out. It works out what can be built, asks the outside world for what is missing, and does only the work the declared outcome needs.

## Why a request is the wrong container

A real business process is rarely one request. A payment is captured hours after the order. An approval arrives tomorrow. The process restarts halfway. The usual answer is to write the business twice: once as types, and again as a workflow that sequences it. The workflow is where the bugs are, and nothing checks it.

TCA's target is that the declared types are the only account of the business. An invocation pursues an outcome and outlives any request, connection or process. While it waits for evidence it holds no open request. When the evidence arrives, it continues. After a crash it recovers without forgetting an external effect that already happened and without repeating it.

## What a model looks like

Shipping an order needs a payment that covers it. That is two facts and one rule, and no step order:

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
    """The grounds to ship: the order, the payment, and that the payment covers it."""
    order: Order
    payment: PaymentCaptured
    covered: Covers
```

`Covers` is the rule. Built from a payment of 50 and a total of 50 it constructs. Built from a payment of 20 and a total of 50 it is refused, and the refusal says which rule failed. A rule is a type that cannot be constructed with the wrong value.

That is all the retained primitives establish. They do not yet bind that `Covers` to this order and this payment. As written, `ShippingAuthority` accepts a `Covers` that was built from any two amounts, and nothing checks that the payment names this order. Binding a conclusion's rule to the exact evidence it is made from is a requirement of the future engine, not something that runs today.

The rest is target. The payment record arrives later from a webhook. It is accepted only if it came from the right provider, for this tenant and this order. A duplicate delivery changes nothing. The shipment is requested under one identity, so a retry or a recovery after a crash does not issue it twice. Whether the carrier ends up shipping once still depends on the carrier's idempotency or on reconciling its status afterward. None of that is written as a workflow.

## Where it stands

- **Exists:** the value layer, in [`packages/python/type-construction-world`](packages/python/type-construction-world). Strict, frozen values, constrained scalars, records under a party's names, facts, computed values that cannot be forged, relations that refuse, and selections over finite tuples. Its tests pass. It cannot run a program.
- **Removed:** the request-based engine, command line, HTTP package and demo. They remain in Git history as reference only.
- **Not built:** evidence admission, invocations, waiting and recovery, external effects, and interfaces. The order is in [`TODO.md`](TODO.md).

The target architecture is [`docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`](docs/TCA_ARCHITECTURAL_FOUNDATIONS.md). Its proposals are not verified. The behavior a replacement must show is in [`docs/REFACTOR_ACCEPTANCE.md`](docs/REFACTOR_ACCEPTANCE.md). Those are requirements, not tests that pass.

## What it will not do

- Constructing a type shows that the declared rules hold over the evidence admitted. It does not show that the evidence is true or that the business program is right.
- It does not make an arbitrary external call exactly-once. It gives each intended operation one identity. The operation itself must be idempotent or reconcilable.
- It is not a Python sandbox, a database, or a replacement for transactions where two invocations race for the same balance.
- It is not for a service that is mostly CRUD with few decisions.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
