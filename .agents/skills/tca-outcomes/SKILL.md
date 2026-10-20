---
name: tca-outcomes
description: "How to write and keep a TCA project's outcomes document (TODO.md): one generic outcome at the root, cut into outcomes the tca-modeling loop reaches one at a time, each stated as the loop's first step states it. Use when starting a project, when an outcome lands and the rest must be rederived, or when a request has to be turned into something the loop can build."
---

# TCA outcomes

Write the plan in the loop's own units, so nothing is translated between
planning and building. The document holds outcomes and nothing else: no
tasks, no estimates, no steps, no files.

## The two kinds

A **generic outcome** is something a party outside the system can newly do.
There is one, at the root. Never build it directly; cut it.

An **outcome** is a generic outcome pinned to one chain the engine runs: the
`Request` that arrives, the `Reply` that leaves, who sends it and who reads
it; or, for a context that never rests, the arrival a connection delivers and
the fact that answers it. The loop runs only on outcomes, because that
statement is its first step. An outcome is one chain. Do not cut it further;
its rows are the loop's to write.

## The document

```
# TODO

The outcome: <what a person or program can newly do, in one sentence, with
how they know it>.

An outcome is one thing a party outside the system can newly do, reached by
the loop in the `tca-modeling` skill: the Request that arrives and the Reply
that leaves, who sends it and who reads it; then its nouns as rows, by name,
kind and what they hold; then the decisions it rests on. <keep this paragraph
verbatim>

<one paragraph: how the outcomes share one model; which outcome builds the
nouns every later one holds>

<one paragraph: the rules an earlier outcome established that bind every
later one, each cited to its decision>

## 0. <a person's act that needs nothing built, if the project begins with one>

<what the person does and learns; no Arrives, no Nouns>

## 1. <title>

Arrives: `<Request>` at <route>, sent by <who>. Answers: `<Reply>`, read by <who>.
Parties: <each party reached>, which may say `<Record>` or `<Record>`.

Nouns: `<Fact>(<what it holds>)`; `<Action>(<fact>)` says `<Record | Record>`;
`<Record>(<what it holds>)`; <a noun described where its name is not yet
settled>; ... Proved by: <`run` to each fact at rest, the route to its reply>.

Rests on D<n>, D<n>.
```

For a context that never rests, write `Arrives: <Record> from <Connection>.
Answers: <the fact that holds it>.` in place of the first line.

## Writing one outcome

- **Title**: what a party outside the system can newly do, as one sentence a
  stranger could test. Not a feature, not a component, not an activity.
- **Arrives and Answers**: the loop's first step, verbatim. Name the `Request`
  and its route, the `Reply`, who sends and who reads. For a live context,
  name the arrival, its connection, and the fact that answers it.
- **Parties**: every connection the chain reaches and every record each may
  say, read from the party's contract. A record the contract names and the
  business has no fact for is a fact you have not named yet; name it here.
- **Nouns**: every row the outcome needs, as the list will carry it: the name,
  what it holds in parentheses, and for an action the records it declares.
  Name a noun an earlier outcome built and this one changes with the change
  ("`Order`, which gains `card`"). End with how it is proved: `run` from the
  request to the fact at rest for every record each party may say, and the
  route to its reply.
- **Rests on**: the decisions, by number, whose evidence the work will cite.
  Decisions live in the project's decisions document as `## D<n>. <title>`
  with their reason and evidence. Never restate one in an outcome.

## Ordering and cutting

- Put outcomes in dependency order: each holds something the ones before it
  made exist. The first builds the nouns every later one holds.
- One outcome, one chain. If the title needs "and", write two outcomes, unless
  the second clause is how the first is proved.
- Cut the generic outcome by asking what must newly be possible, in what
  order, for the root sentence to become true. Each answer is an outcome.
- When an outcome needs a noun the document gave to a later one, move the noun
  and rewrite the later outcome. Never hold a noun in two outcomes.

## Keeping it true

After every outcome lands, rederive the outcomes below it from what the loop
learned: rows that changed name, kind or holds; decisions amended or added;
chains that split or merged. Commit that rederivation on its own, before the
next outcome starts, with the rederivation as its outcome. The document is
never ahead of the model and never behind it.

## Example, the shop

```
## 1. A customer checks out and learns whether the order was paid

Arrives: `CheckoutRequest` on `checkout`, sent by the customer. Answers:
`OrderReply`, read by the customer.
Parties: the promotions system, which says `DiscountOffer`; the payment
provider, which says `ChargeApproved` or `ChargeDeclined`.

Nouns: `Order(CheckoutRequest)`; `ReadDiscount(Order)` says `DiscountOffer`;
`PricedOrder(Order, DiscountOffer)`; `Charge(PricedOrder)` says
`ChargeApproved | ChargeDeclined`; `PaidOrder(PricedOrder, ChargeApproved)`;
`DeclinedOrder(PricedOrder, ChargeDeclined)`; `OrderReply(Outcome, Amount)`;
`Promotions(Address)`; `Payments(Address)`; `ShopConfig(Promotions,
Payments)`; the scalars and values these hold. Proved by `run` to `PaidOrder`
and to `DeclinedOrder` with each party faked, and the route answering the
reply.

Rests on D1.
```

Handed to `tca-agent` verbatim, with where the tree stands and the owner's
constraints, that text is the whole launch. Nothing else is needed, because
it is already in the loop's words.
