---
name: python-dev-tca
description: "Type Construction Architecture for Python. A program is declared as Pydantic types, and construction is the only operation. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists."
---

# Python Dev TCA

## A whole program

```mermaid
flowchart LR
    subgraph g1["1 ordered union · collection"]
        DeclineReasons["<b>DeclineReasons</b><br/>DeclineReason, else UnlistedReason"]
    end

    subgraph g2["2 foreign model"]
        ChargeRequest["<b>ChargeRequest</b><br/>amt · cur · src · ref"]
        ChargeApproved["<b>ChargeApproved</b><br/>id"]
        ChargeDeclined["<b>ChargeDeclined</b><br/>decline_codes"]
        ChargeFailed["<b>ChargeFailed</b><br/>error"]
    end

    subgraph g3["3 value object · collection"]
        Line["<b>Line</b><br/>sku · unit_price · quantity"]
        Lines["<b>Lines</b>"]
        Approval["<b>Approval</b><br/>charge"]
        Decline["<b>Decline</b><br/>reasons"]
        Failure["<b>Failure</b><br/>error"]
    end

    subgraph g4["4 concept model"]
        Order["<b>Order</b><br/>id · customer · card · currency · lines"]
        PricedOrder["<b>PricedOrder</b><br/>order · discount"]
    end

    subgraph g4u["4 union"]
        LoyaltyDiscount["<b>LoyaltyDiscount</b><br/>percent"]
        NoDiscount["<b>NoDiscount</b>"]
        PaidOrder["<b>PaidOrder</b><br/>order · payment"]
        DeclinedOrder["<b>DeclinedOrder</b><br/>order · payment"]
        UnsettledOrder["<b>UnsettledOrder</b><br/>order · payment"]
    end

    subgraph g4a["4 action"]
        ReadDiscount["<b>ReadDiscount</b><br/>order"]
        Charge["<b>Charge</b><br/>order"]
    end

    subgraph g5["5 contract model"]
        PublishedOrder["<b>PublishedOrder</b><br/>id · amount · currency · discount"]
        OrderConfirmed["<b>OrderConfirmed</b><br/>order · payment"]
        OrderRejected["<b>OrderRejected</b><br/>order · payment"]
        OrderUnsettled["<b>OrderUnsettled</b><br/>order · payment"]
    end

    subgraph g7["7 transformation"]
        ChargeAttempt["<b>ChargeAttempt</b><br/>order · payment"]
    end

    subgraph g8["8 effect interpreter"]
        ReadDiscountInterpreter["<b>ReadDiscountInterpreter</b><br/>action · client"]
        ChargeInterpreter["<b>ChargeInterpreter</b><br/>action · client"]
    end

    subgraph g9["9 route"]
        CheckoutRoute["<b>CheckoutRoute</b><br/>order"]
        ReplyRoute["<b>ReplyRoute</b><br/>outcome"]
    end

    Line --> Lines --> Order --> CheckoutRoute
    Order --> ReadDiscount --> ReadDiscountInterpreter ==> PricedOrder
    Order --> PricedOrder
    LoyaltyDiscount --> PricedOrder
    NoDiscount --> PricedOrder
    PricedOrder --> Charge --> ChargeInterpreter ==> ChargeAttempt
    PricedOrder -.-> ChargeRequest
    PricedOrder --> ChargeAttempt
    ChargeApproved --> ChargeAttempt
    ChargeDeclined --> ChargeAttempt
    ChargeFailed --> ChargeAttempt
    DeclineReasons --> ChargeDeclined
    DeclineReasons --> Decline
    ChargeAttempt -.-> PaidOrder -.-> OrderConfirmed --> ReplyRoute
    ChargeAttempt -.-> DeclinedOrder -.-> OrderRejected --> ReplyRoute
    ChargeAttempt -.-> UnsettledOrder -.-> OrderUnsettled --> ReplyRoute
    Approval --> PaidOrder
    Decline --> DeclinedOrder
    Failure --> UnsettledOrder
    PricedOrder -.-> PublishedOrder --> OrderConfirmed
    PublishedOrder --> OrderRejected
    PublishedOrder --> OrderUnsettled
```

Every box is a class in the page its group names.
A solid arrow is a field: the head holds the tail.
A dotted arrow is construction by shared names: the head is constructed from the tail.
A thick arrow is an effect: the interpreter's `execute` returns the head.
A step you are about to write is a class you have not named.
What differs between the variants of a union is one derivation, under one name, on each variant.
The text at every edge of this program is in [program.md](program.md).

## Its files, in the order they are written

```text
 1  domain/<context>/type.py               semantic-scalar.md  ordered-union.md  collection.md
 2  integration/<system>/model.py          foreign-model.md
 3  domain/<context>/value.py              value-object.md  collection.md
 4  domain/<context>/<concept>.py          union.md  concept-model.md  action.md
 5  domain/<context>/api.py                contract-model.md
 6  config.py                              config.md
 7  integration/<system>/<meaning>.py      transformation.md
 8  integration/<system>/interpreter.py    effect-interpreter.md
 9  api/<context>.py                       route.md
10  main.py                                composition-root.md
```

A file imports only files written before it. The page beside a file is read immediately before that file is written.
