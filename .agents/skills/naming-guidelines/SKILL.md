---
name: naming-guidelines
description: "How to name a type, a field or a variant in a TCA program so the name says what the thing is. Use whenever a class, field or union variant is named or renamed, and whenever a reader's first guess at a name is wrong."
---

# Naming Guidelines

A name states what a thing is. Not what happens to it, not when it occurs, not how it is built. If the name needs the body to be understood, the name is wrong or the thing is.

## Name from the ontology

- Name a type for the one thing it means in the domain's own language. `Order`, `PricedOrder`, `OrderReply`, not `Input`, `Request1`, `Result`.
- Name every variant of a union by the fact that decides it, and give the variants' shared fact one name across all of them. `PaidOrder.charge: ChargeApproved` beside `DeclinedOrder.charge: ChargeDeclined`. Two things that differ only by a field one of them lacks are two facts, not two variants.
- Name an absence as the thing that is absent, where the holder has the slot. `NoDiscount`. Never `None`, `Empty`, `Null`, `Missing`. Do not invent a slot so that an absence has somewhere to sit; a thing without the fact is a different thing.
- Name a field for its role in the holder, and let its type say what it is. `order: Order`, `offer: DiscountOffer`, `charge: ChargeApproved`.
- A reference to what another party keeps is a domain noun with the party's identity in it. `ChargeId` is the shop's word for the payment provider's charge.
- A kind is never in a name. `Order`, not `OrderFact`; `Payments`, not `PaymentsConnection`; `Charge`, not `ChargeAction`.

## Refuse these names

- A gerund or a stage: `Answering`, `Processing`, `Pending`, `Loaded`. A stage is workflow hiding in a class, and so is a type whose only job is to pick another type.
- A position in a flow: `First`, `Next`, `Step2`, `Final`. Name the state the position implies: `Order`, `PricedOrder`.
- A mechanism: `Dispatcher`, `Handler`, `Manager`, `Helper`, `Wrapper`, `Util`.
- A synonym for a noun that already has a name. One thing, one name, in the domain, the api, the README and the tests alike.
- A noun nothing reads. Delete it; it names nothing.

## Test the name

- Say the name to someone who knows the domain and not the code. Their first guess must be right. A wrong first guess is a finding; rename at once, before the commit, and reprint the noun list.
- Read the route aloud. `checkout = Route[CheckoutRequest, OrderPaid | OrderRefused](name=RouteName("checkout"))` says what it does. If a route needs a comment, a name in it is wrong.
- Draw the line between the domain's vocabulary and a party's, and keep every name on one side of it. A `Record` carries the party's names, under aliases where they differ; every other class carries the domain's. `ChargeApproved` is what the payment provider says; `PaidOrder` is what the shop concludes.
- Check the two vocabularies agree: the domain's word, and the party's word in a `Record`. When they pull apart, the domain's word wins in a fact and the party's word wins in a record.
