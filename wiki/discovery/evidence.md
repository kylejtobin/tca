---
type: Reference
description: A foreign reply is a witness to the world, not a thing to translate; render the real one and read it as a graph before naming anything.
---

# Evidence

Discovery starts from evidence, never from a class shape, a workflow, or a vendor's field list. The evidence is whatever an outside source says about the world the program models: an API reply, an SDK's generated types, a document, a specification, a domain expert's description.

## The source is a witness

A vendor that has looked at thousands of institutions, or a standard that many systems agreed on, has already done work on the world. Its shape is evidence about the domain's nouns. Its nulls are evidence about which facts are absent for which kinds, which is evidence about unions. Its closed vocabularies are evidence about axes. Its nesting is evidence about composition.

It is evidence, not the thing. The source has its own transport, its own enrichment, its own naming, and its own convenience shapes. A flat `names: ["Kyle Tobin", "Kyle A Tobin"]` is one source's rendering of a structured personal name. A `primary: true` flag on every row is one source's rendering of a set that has a preferred member. Reading the witness means recovering the thing it saw, not copying the page it wrote.

Where independent witnesses converge, the shape is real. A person, as Plaid renders an account owner and as SCIM (RFC 7643) renders a user, has several names, several contact points each of a kind with one preferred, and addresses of the same shape. Two witnesses that never met agree, so that is what a person is. Where they diverge, decide from the thing.

## Render the real thing

Print the evidence before deciding anything, and print the real one. For an API, construct the reply through the vendor's SDK so the nulls fall where the vendor puts them and the keys are the vendor's, not remembered. For a document, quote it. Authoring evidence from memory is the first substitution: it lets the model decide what the world contains while appearing to read it.

## Read it as a graph

The reply is a composition graph, not a flat list of keys. A reply holds an item and accounts; an account holds balances; balances hold sums and a currency. Read what holds what. Then read the nulls per kind: a deposit account has no limit, a loan has no available balance, so balances are one value per kind, not one value with optional fields. Then read the vocabularies: a two-level type and subtype where subtypes partition under types is an axis with a per-member vocabulary.

Keys can name a noun, hide one, split one across several keys, or be no noun at all. `pending: false` hides settlement, a state with two members. A signed `amount` splits a magnitude and a direction into one number. `request_id` is no noun. The reading is not a scan for strings; it is asking what thing in the world made the source put this here.

## What evidence does not decide

Evidence says what exists. It does not say what the program's vocabulary is where nature has none. What a movement of money was *for* has no shape in the world; its vocabulary comes from what the program does with it. A vendor's 104-value taxonomy is that vendor's product, and adopting it is modeling the vendor. See [deciding](./deciding.md).

Evidence is read once per source, and the next step, [things](./things.md), is run against it.
