---
type: Program
description: "The checkout program of SKILL.md, traced once: the exact text at every edge, and what each text constructs, for every lane."
---

# The program, traced

## What arrives

```text
{"order": {"id": "O1", "customer": "C1", "card": "tok_1", "currency": "usd", "lines": [{"sku": "MUG", "unit_price": 1200, "quantity": 2}, {"sku": "TEE", "unit_price": 1800, "quantity": 1}]}}
```

`CheckoutRoute.model_validate_json(body).order` is an `Order`.
Its `lines` is a `Lines` holding two `Line`s, and `lines.amount` is `Amount(4200)`.
Its `pricing` is a `ReadDiscount` holding that `Order`.

## What is asked of the promotions system

`ReadDiscountInterpreter.execute` requests `/discounts/C1`. The promotions system answers:

```text
{"percent": 10}
```

`DiscountStateConstructor.validate_json` gives a `LoyaltyDiscount`.
`execute` returns a `PricedOrder` whose `amount` is `Amount(3780)`.
Its `charge` is a `Charge` holding that `PricedOrder`.

## What is sent to the payment provider

`ChargeRequest.model_validate(priced_order, from_attributes=True).model_dump_json(by_alias=True)` is:

```text
{"amt":3780,"cur":"usd","src":"tok_1","ref":"O1"}
```

## The approved lane

The provider answers:

```text
{"id": "ch_9"}
```

`ChargeReplyConstructor.validate_json` gives a `ChargeApproved`.
`ChargeInterpreter.execute` returns a `ChargeAttempt` whose `outcome` is a `PaidOrder` whose `payment` is `Approval(charge=ChargeId("ch_9"))`.
The response body is:

```text
{"outcome":{"order":{"id":"O1","amount":3780,"currency":"usd","discount":{"percent":10}},"payment":{"charge":"ch_9"}}}
```

## The declined lane

The provider answers:

```text
{"decline_codes": ["insufficient_funds", "do_not_honor"]}
```

`ChargeReplyConstructor.validate_json` gives a `ChargeDeclined` whose `reasons` holds `DeclineReason.INSUFFICIENT_FUNDS` then `UnlistedReason("do_not_honor")`.
`ChargeInterpreter.execute` returns a `ChargeAttempt` whose `outcome` is a `DeclinedOrder` whose `payment` is a `Decline` holding those `reasons`.
The response body is:

```text
{"outcome":{"order":{"id":"O1","amount":3780,"currency":"usd","discount":{"percent":10}},"payment":{"reasons":["insufficient_funds","do_not_honor"]}}}
```

## The failed lane

The provider answers:

```text
{"error": "rate_limited"}
```

`ChargeReplyConstructor.validate_json` gives a `ChargeFailed`.
`ChargeInterpreter.execute` returns a `ChargeAttempt` whose `outcome` is an `UnsettledOrder` whose `payment` is `Failure(error=ProviderError.RATE_LIMITED)`.
The response body is:

```text
{"outcome":{"order":{"id":"O1","amount":3780,"currency":"usd","discount":{"percent":10}},"payment":{"error":"rate_limited"}}}
```

## No discount

The promotions system answers:

```text
{}
```

`DiscountStateConstructor.validate_json` gives a `NoDiscount`.
`execute` returns a `PricedOrder` whose `amount` is `Amount(4200)`, and what is sent to the payment provider is:

```text
{"amt":4200,"cur":"usd","src":"tok_1","ref":"O1"}
```

On the approved lane the response body is:

```text
{"outcome":{"order":{"id":"O1","amount":4200,"currency":"usd","discount":{}},"payment":{"charge":"ch_9"}}}
```
