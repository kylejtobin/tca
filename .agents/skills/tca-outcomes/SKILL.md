---
name: tca-outcomes
description: "How to write and keep a TCA project's outcomes document (TODO.md): one generic outcome at the root, cut into crossing outcomes that the tca-modeling loop reaches one at a time, each stated in the loop's own terms. Use when starting a project, when an outcome lands and the rest must be rederived, or when a request has to be turned into something the loop can build."
---

# TCA outcomes

The outcomes document is the plan, and it is written in the loop's own units so
that no translation stands between planning and building. It has no tasks, no
estimates, no steps and no files; those belong to the loop. It has outcomes.

## The two kinds

A **generic outcome** is something a party outside the system can newly do.
It has no single boundary. There is one, at the root, and it is never built
directly; it is reached by cutting it.

A **crossing outcome** is a generic outcome pinned to one boundary: what
crosses, the contract that owns it, and the domain type it is. The loop runs
only on crossing outcomes, because its first step needs an owner and a type.
Everything under the root is a crossing outcome, and each one, when the loop
derives its crossings, cuts into crossing outcomes again. The schema is the
same at every depth; the party outside a file is the file above it, the party
outside the package is the person using it.

## The document

```
# TODO

The outcome: <the generic outcome: what a person or program can newly do, in
one sentence, with how they know it>.

An outcome is one thing a party outside the system can newly do across one
crossing, reached by the loop in the `tca-modeling` skill: what crosses, the
contract that owns it, the domain type it is; then its nouns, by name and
kind; then the decisions it rests on. <keep this paragraph verbatim>

<one paragraph: how the outcomes cut one graph; which outcome owns the root
every other writes under, and which read or write what>

<one paragraph: the rules an earlier outcome established that bind every
later one, each cited to its decision>

## 0. <a person's act that needs nothing built, if the project begins with one>

<what the person does and learns; no Crossing, no Nouns>

## 1. <title>

Crossing: <what crosses> crosses when <the event>; <the contract that owns it>
owns it; the domain type is `<Type>`.

Nouns: `<Type>(<fields>)`; `<Type>`; <a noun described where its name is not
yet settled>; ... Proved on <the dataset or example the tests hold>.

Rests on D<n>, D<n>.

## 2. <title>
...
```

## Writing one outcome

- **Title**: what a party outside the system can newly do, as one sentence a
  stranger could test. Not a feature, not a component, not an activity.
- **Crossing**: three facts in the loop's order. What crosses, with the event
  that makes it cross. Which contract owns the crossing, so step 1 has
  something to cite. Which domain type it is, so the crossing has a name in
  the model.
- **Nouns**: every type the outcome needs, by name, with fields in parentheses
  where known, and a phrase where the noun is known but its name is not. A
  noun that an earlier outcome built and this one changes is named with the
  change ("`Version`, which regains `role`"). End with how it is proved: the
  dataset, example or interface the verification step crosses.
- **Rests on**: the decisions, by number, whose evidence the tactics will cite.
  Decisions live in the project's decisions document as `## D<n>. <title>`
  with their reason and evidence; an outcome never restates one.

## Ordering and cutting

- Outcomes sit in dependency order: each crosses something the ones before it
  made exist. The first builds the root everything else writes under.
- One outcome reaches one crossing. If the title needs "and", it is two
  outcomes, unless the second clause is how the first is proved.
- Cut the generic outcome by asking what must newly be possible, in what
  order, for the root sentence to become true; each answer is an outcome.
- An outcome that turns out to need a noun the document gave to a later one
  takes it, and the later one is rewritten; the document never holds a noun
  in two outcomes.

## Keeping it true

After every outcome lands, rederive the outcomes below it from what the loop
learned: the nouns that changed name or owner, the decisions that were amended
or added, the crossings that split or merged. Commit that rederivation on its
own, before the next outcome starts, with the rederivation as its outcome. The
document is never ahead of the model and never behind it.

## Example, from the eval package

```
## 2. A run is scored by code, and the oracle scores 1.0

Crossing: a recorded repetition crosses when the runner calls its scorer; the
log owns the score; the domain type is `Score`.

Nouns: `Criterion(id, description, kind)`; `Score(address, trace, criterion,
evaluator, label, value, confidence, explanation)`; the evaluator as a
`Version`, which regains `role`; `matches-expectation`, the code criterion
every dataset has; `EvaluateInterpreter`, whose span `evaluate <criterion>` is
a child of the run's root through the recorded ids, its verdict among its
attributes at acquisition; the scorer as a composition-root callback the
runner names by registry, as the solver is; a sample produced and then
errored, read as the score's error, not the run's; the Phoenix provider, its
annotation, project description and annotation configuration, each kept by
the reply Phoenix gives; rescoring as the runner's own `score`, which returns
the log. Proved on the dataset the tests hold.

Rests on D5, D6, D7, D17, D22.
```

Handed to `tca-agent` verbatim, with where the tree stands and the owner's
constraints, that text is the whole launch. Nothing else is needed, because it
is already in the loop's words.
