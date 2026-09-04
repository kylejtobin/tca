---
type: Reference
description: A good construct is the shape of something in the world; a bad one is the shape of an obstacle the modeler hit while typing.
---

# Shape of a Thing

Put two sets of constructs for the same domain side by side and the difference is not skill. It is what each type is the shape of.

## The shape of an obstacle

Built fast, from the wire inward, before the world was decided, one domain came out as: `NoLimit`, a scalar over `Literal[None]` because a balance key arrived null; `Given` and `Unreported`, a generic pair because a value might be absent; `Outgoing` and `Incoming`, two sums because the wire sends a sign; `Mask` beside `AccountMask`, a second vocabulary for the vendor's side; `PlaidText`; subtype code scalars with lookup tables to translate between the modeler's own two vocabularies; a `kind` pin on positions restating the account's type so a discriminator would fire; `# pyright:` suppressions in every file that crossed; loops in verbs over `.each` to avoid a branch.

Every one of these is the shape of a mechanical question hit at the keyboard: what to do with a null, a sign, an untyped SDK, a checker refusal, a discriminator that needs a field. None is the shape of anything in the world. They read as workarounds because they are. And every derivation written afterward was translation between the modeler's own vocabularies, work that existed only because the vocabularies did.

## The shape of a thing

The same domain, built after the thinking was finished: `DepositBalances` holds a ledger balance and an available balance, each a sum with the way it stands. `CreditBalances` adds a limit. `LoanBalances` holds a ledger balance alone. `Loan` carries terms, security, and servicing. `Mortgage` is always secured by real property, so it carries the property, not a `Security` union. `StudentLoan` is never secured, so it has no security field. An account's number is masked, full, or unknown. `Money` is `Money` everywhere it appears.

Every file reads as a description of the thing it names. There is nothing in any of them about how the data arrived, what the checker thinks, or what the modeler struggled with. No wrapper, no lookup table, no `.root` read, no alias, no suppression, because nothing crosses anywhere yet, so nothing has to be explained.

## Why fast building produces obstacles

The model generates left to right. A construct is a graph decision: its correctness depends on relations to things not yet written. Writing a type well requires the whole shape decided first. When the shape is not decided and a token has to land, what lands is whatever answers the local question in front of the generator. The local question at the keyboard is never "what is a balance"; it is "this key is null, what do I do." So the type that lands is the shape of that question.

This is why discovery separates [things](./things.md) from [constructs](./constructs.md), and why neither is code. By the time a construct is chosen, the thing, its parts, its constraints, and its name are already written down, and the construct has nothing left to invent. The obstacles still exist. They are met at the crossing, in the [foreign model](../constructs/foreign-model.md), where the answer to "this key is null" is an alias and a union already decided from the world, not a new noun.

## The test

Read the construct and ask what it is the shape of. If the answer names a thing a domain expert would recognize, it holds. If the answer names a null, a sign, a checker, a vendor, or a step in the modeler's process, it is an obstacle wearing a type, and the thinking it stands in for has not been done.
