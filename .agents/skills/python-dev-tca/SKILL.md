---
name: python-dev-tca
description: "Type Construction Architecture for Python. A program is declared as Pydantic types, and construction is the only operation. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists."
---

# Python Dev TCA

Whenever you do development, always ask these three questions:

1. Remove every body. Do the types alone still specify the domain? If what remains is a pipeline, there is no model.
2. Which types are named for a stage of the run? Each is workflow inhabiting a class, and the domain thing under it has no type. Delete it.
3. Are the inhabitants of the types in bijection with the states of the domain? If not, the model is wrong. Remodel from the domain; do not patch the type.

Every type you write sits on one of these levels, and its fields hold only types from the levels above it; a type you cannot place by its fields is procedure.

```text
Scalar
↓
Value
↓
Thing
↓
Alternative
↓
Crossing
```

Every class you write is a `BaseModel`, a `RootModel` or a `StrEnum`. Every field is typed as one of your own classes, a union of them, or a tuple of them; a primitive appears only as the root of a `RootModel`. There is no `dict`, `list`, `set`, `Any`, `None` or `Optional` anywhere: not in a field, a root, an argument or an expression. The only functions are one `interpret` on each interpreter and the callback in `main.py`, each a single returned expression, and the reading and writing of a format in `parser/`; anything else a class knows is a property with a single returned expression. An interpreter also holds its client, and config is a `BaseSettings`; nothing else is held that is not one of your classes. Construction is the only operation: a step you are about to write is a class you have not named.

What arrives is a dictionary or JSON and constructs a model by `model_validate` or `model_validate_json`; what leaves is `model_dump` or `model_dump_json`.
A format that is neither is read by a maintained library that yields a dictionary or JSON, and is then the line above.
Only a format no library yields a dictionary or JSON from is read by a format type in `parser/`, and nothing outside `parser/` reads a format.

## A whole program

```mermaid
flowchart LR
    subgraph g1["1 ordered union · collection"]
        StatedReason["<b>StatedReason</b><br/>DeclineReason, else UnlistedReason"]
        StatedError["<b>StatedError</b><br/>ProviderError, else UnlistedError"]
        DeclineReasons["<b>DeclineReasons</b>"]
    end

    subgraph g2["3 foreign model"]
        CustomerDiscount["<b>CustomerDiscount</b><br/>customer"]
        DiscountOffer["<b>DiscountOffer</b><br/>percent"]
        CardCharge["<b>CardCharge</b><br/>amt · cur · src · ref"]
        ChargeApproved["<b>ChargeApproved</b><br/>id"]
        ChargeDeclined["<b>ChargeDeclined</b><br/>decline_codes"]
        ChargeFailed["<b>ChargeFailed</b><br/>error"]
        ChargeReply["<b>ChargeReply</b>"]
    end

    subgraph g3["4 value object · collection"]
        Line["<b>Line</b><br/>sku · unit_price · quantity"]
        Lines["<b>Lines</b>"]
        Discount["<b>Discount</b><br/>percent"]
        Approval["<b>Approval</b><br/>charge"]
        Decline["<b>Decline</b><br/>reasons"]
        Failure["<b>Failure</b><br/>error"]
    end

    subgraph g4["5 concept model"]
        Order["<b>Order</b><br/>id · customer · card · currency · lines"]
        PricedOrder["<b>PricedOrder</b><br/>order · discount"]
    end

    subgraph g4u["5 union"]
        PaidOrder["<b>PaidOrder</b><br/>order · payment"]
        DeclinedOrder["<b>DeclinedOrder</b><br/>order · payment"]
        UnsettledOrder["<b>UnsettledOrder</b><br/>order · payment"]
        OrderOutcome["<b>OrderOutcome</b>"]
    end

    subgraph g4a["5 action"]
        ReadDiscount["<b>ReadDiscount</b><br/>order"]
        Charge["<b>Charge</b><br/>order"]
    end

    subgraph g5["6 contract model"]
        PublishedOrder["<b>PublishedOrder</b><br/>id · amount · currency · discount"]
        OrderConfirmed["<b>OrderConfirmed</b><br/>order · payment"]
        OrderRejected["<b>OrderRejected</b><br/>order · payment"]
        OrderUnsettled["<b>OrderUnsettled</b><br/>order · payment"]
        OrderReply["<b>OrderReply</b>"]
    end

    subgraph g7["8 transformation"]
        ChargeAttempt["<b>ChargeAttempt</b><br/>order · reply"]
    end

    subgraph g8["9 effect interpreter"]
        ReadDiscountInterpreter["<b>ReadDiscountInterpreter</b><br/>action · client"]
        ChargeInterpreter["<b>ChargeInterpreter</b><br/>action · client"]
    end

    subgraph g9["10 route"]
        CheckoutRoute["<b>CheckoutRoute</b><br/>order"]
        ReplyRoute["<b>ReplyRoute</b><br/>outcome"]
    end

    StatedReason --> DeclineReasons
    Line --> Lines --> Order --> CheckoutRoute
    Order --> ReadDiscount --> ReadDiscountInterpreter ==> PricedOrder
    Order -.-> CustomerDiscount
    DiscountOffer -.-> Discount
    Order --> PricedOrder
    Discount --> PricedOrder
    PricedOrder --> Charge --> ChargeInterpreter ==> ChargeAttempt
    PricedOrder -.-> CardCharge
    StatedError --> ChargeFailed
    StatedError --> Failure
    PricedOrder --> ChargeAttempt
    ChargeApproved --> ChargeReply
    ChargeDeclined --> ChargeReply
    ChargeFailed --> ChargeReply
    ChargeReply --> ChargeAttempt
    DeclineReasons --> ChargeDeclined
    DeclineReasons --> Decline
    ChargeAttempt -.-> OrderOutcome
    PaidOrder --> OrderOutcome
    DeclinedOrder --> OrderOutcome
    UnsettledOrder --> OrderOutcome
    Approval --> PaidOrder
    Decline --> DeclinedOrder
    Failure --> UnsettledOrder
    PaidOrder -.-> OrderConfirmed
    DeclinedOrder -.-> OrderRejected
    UnsettledOrder -.-> OrderUnsettled
    PricedOrder -.-> PublishedOrder
    Discount --> PublishedOrder
    PublishedOrder --> OrderConfirmed
    PublishedOrder --> OrderRejected
    PublishedOrder --> OrderUnsettled
    OrderConfirmed --> OrderReply
    OrderRejected --> OrderReply
    OrderUnsettled --> OrderReply
    OrderOutcome -.-> OrderReply --> ReplyRoute
```

Every box is a class in the page its group names.
A solid arrow is a field: the head holds the tail.
A dotted arrow is construction by shared names: the head is constructed from the tail.
A thick arrow is an effect: the interpreter's `interpret` returns the head.
What differs between the variants of a union is one derivation, under one name, on each variant.

## Its files, in dependency order

```text
 1  domain/<context>/type.py               semantic-scalar.md  ordered-union.md  collection.md
 2  parser/<format>.py                     parser.md
 3  integration/<system>/model.py          foreign-model.md
 4  domain/<context>/value.py              value-object.md  collection.md
 5  domain/<context>/<concept>.py          union.md  concept-model.md  action.md
 6  domain/<context>/api.py                contract-model.md
 7  config.py                              config.md
 8  integration/<system>/<meaning>.py      transformation.md
 9  integration/<system>/interpreter.py    effect-interpreter.md
10  api/<context>.py                       route.md
11  main.py                                composition-root.md
```

A file imports only the files above it. Its constructs are on the pages beside it.
