---
type: Reference
description: Decide what the world contains, how it composes, what must be true of it, and what it is called, before any construct is named.
---

# Things

Step two of discovery decides what exists. It ends with two lists, things to create and things to change, and no construct type appears in either. The construct is chosen later, from what the thing is. Choosing it first is how a type ends up shaped like a problem instead of a thing; see [shape of a thing](./shape-of-a-thing.md).

## The six questions

Each question has one input, the evidence, and feeds one output, the filled schema. Each exists to forestall a specific failure.

**1. What things in the world is this evidence of, and how do they compose into each other?**
The graph question. It is asked of the whole reply, once, before any thing is examined alone. Answered per key instead, it degenerates into a loop over nouns that manufactures a mechanical pass for each. The answer is a tree: obligation hangs on an account; terms, security, servicing hang on the obligation; collateral hangs on security; an address hangs on real property.

**2. For each thing: is it already ours, and if so which type, or is it new?**
Reuse before creation. Every date is `Date`, every sum is `Money`, every party reference is `PartyId`. A thing that already exists gets its existing type; a second type for the same meaning is the duplicated break, and this question kills it before code exists. Only what survives this question is new.

**3. For each thing: what is it, as it is in nature, and what must be true of it?**
The ontology question. One sentence a domain expert accepts, then the constraints: principal above zero, maturity after origination, a secured obligation with nothing named is impossible. This is where the value space is decided, and it is decided by the thing, not by a list of permitted primitives. A point in time is a timezone-qualified datetime. An identifier is a UUIDv7. A string with a pattern admits what the real type refuses.

**4. For each thing: what is its best name?**
The word a domain expert already uses, so a reader recognizes the thing without a definition. The vendor's word is irrelevant to the choice: if it is the expert's word, matching costs nothing; if it is worse, ours is better and the alias carries theirs at the crossing. `Movement`, `Day`, `Other side` chosen to differ from `transaction`, `date`, `counterparty` are names chosen for the wrong reason. See [naming](../constructs/naming.md).

**5. What in the evidence is the source's account of a thing and not the thing?**
Asked of every thing and every part named in question 1, not only of the reply's top-level keys. Transport: cursors, request ids, echoed frames. Enrichment: logos, confidence scores, icon URLs. Rendering: a flat list of name strings, a per-row `primary` flag, `"30 year"` as prose for a term in months. Bookkeeping dressed as nature: `removed` as a state a transaction passes through, when in the world a transaction is pending or posted and a reversal is its own movement.

**6. Seen whole with these things in it, should the world look different, and how?**
The holistic pass. Reading a transaction can change what money is: a signed sum was carrying a direction and a standing that are their own facts. Reading an owner can change what a party is: the flat party was the organization arm of a union. The question demands the answer, not the doubt. "Does anything look wrong" invites a report; "what is it instead" demands a decision.

## The output

A filled schema and nothing else:

```json
{
  "create": [{"name": "", "is": "what it is in nature", "must": ["what is true of every one"], "holds": ["things it composes"]}],
  "change": [{"name": "existing type", "becomes": "what it is now"}],
  "unchanged": ["existing types the evidence touches and leaves as they are"]
}
```

`name / is / must / holds` is a concept model written in prose: identity, definition, constraints, composition edges. The create list is a construction graph before code. The schema is the gate: a missing field is visible on the page, and a hedge has no slot to sit in. An essay in its place hides every skipped decision behind a sentence that explains.

## Why it is run one question at a time

Nine questions answered for fifteen things at once produce a loop, and each pass gets the attention of one hundred thirty-fifth of a turn. One question as the whole turn gets the whole turn, and the prior answer is its only input. The operator advances the step. The model does not control its own advancement, because an agent that controls advancement skips steps and does not know it did; see [substitutions](./substitutions.md).
