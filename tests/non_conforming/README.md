# Non-conforming test artifacts

This directory holds code that **deliberately does not conform to Type Construction
Architecture.** It is preserved, unaltered, as adversarial input for the build agent team.
Nothing here is an example to follow. Everything here is an example to *survive*.

The deterministic gate excludes `tests/`, so the non-conforming code here is never flagged
in normal operation. Its wrongness is intentional and load-bearing. **Do not "fix" it.**

## The artifact: `building_block.py`

A 1517-line recursive Pydantic type-tree classifier: hand it any `BaseModel` and it walks
the entire construction graph, classifying every field and every field of every model-typed
field, all the way down, with zero domain knowledge. It is a substantial, working program,
and it is non-conforming in nearly every way the doctrine names:

- It is built on **`Literal`-tag discriminated unions** routed by `Field(discriminator=...)`,
  the exact pattern the tagless-union doctrine removes. Worse, the unions are **not
  disjoint**: drop the tag and the variants collapse to identical payloads, so the tag
  carries the entire distinction rather than being a redundant label over disjoint structure.
- It is the forbidden **classify-then-tag-then-route** machine: hand-built classifier
  properties branch over `get_origin`/`get_args` to emit a tag, and a discriminated union
  routes on the tag.
- It launders domain values as **bare primitives** (`field_name: str`, `nullable: bool`,
  `cycle: bool`), uses **bare enums** as fields and as discriminators, shares fields by
  **inheritance**, threads a five-model `from_attributes` **mapper pipeline**, and hides a
  `ContextVar` **side-channel** inside a `mode="wrap"` validator.
- Its **docstrings teach all of this as best practice** — discriminated-union tags as "the
  key idea," `from_attributes` as "the wiring," and procedure as "the irreducible minimum of
  procedure."

It is, in short, a sophisticated, persuasive, thoroughly non-conforming implementation. That
is exactly why it is here.

## The fundamental problem this exposes

A language model fails at construction-declaration by default, for two compounding reasons.

**1. Training gravity.** A model's weights encode the statistics of public code, and public
code is overwhelmingly *procedural*: services that hold logic, functions that compute over
data, mappers that copy fields between layers, validators that check after the fact, `if`/
`elif` chains and discriminator tags that route by value. TCA is a sparse, low-probability
region of that distribution: meaning lives in the structure of the type, and construction is
its proof. So every token the model generates is a small fight against gravity, and by default
it loses. It will *describe* the architecture correctly in prose and then *generate* a
validator where a narrowed scalar belonged, a function where a derivation belonged, a `match`
where a variant-carried derivation belonged, a tag where disjoint structure belonged. Knowing
the rule and generating to the rule are different capabilities, and the distance between them
is what this artifact measures.

**2. Context absorption.** The model is also a *reader of meaning*. It acts on the names,
comments, and framing in whatever it reads, because that is precisely the second-reader
phenomenon TCA is built around: a neural model reads a program's prose as instruction. A file
that confidently *teaches* the forbidden patterns is therefore a trap. An agent asked to
"understand what this was trying to do" reads the docstrings sympathetically and **absorbs
their rationalizations as its own reasoning**, re-emitting "the irreducible minimum of
procedure" as if it were a conclusion it had reached rather than a stale excuse it had read.
This poison is more dangerous than the wrong code itself: wrong code is caught by the gate;
absorbed *reasoning* re-enters in a plan or a justification, where no gate is watching.

These two pulls compound. The model is dragged toward procedure by its weights and handed a
persuasive procedural rationalization to absorb from the file. An agent team that models
*this* cleanly has overcome both at once.

## Why it is an excellent test

- **It is real, not softball.** 1517 lines, recursion, unions, derivations, boundary
  crossings, a CLI: the hard half of the build patterns in one program. A clean toy proves
  nothing; this exercises the surfaces that actually break.
- **It is wrong precisely where the doctrine is most itself.** The `Literal`-tag unions are
  the exact target of the tagless-union doctrine, and the substrate confirms they are
  non-disjoint, so the team cannot merely delete the tags. It must re-derive what the real
  structural distinctions are, or recognize a uniform vocabulary that is a scalar. This is
  the disjointness discipline under load.
- **It is poisoned by design.** The persuasive docstrings test something a clean example
  cannot: whether the team can read a source for *what it does* without absorbing its account
  of *why*. That failure mode is otherwise invisible, because it manifests as reasoning, not
  as a gate violation.
- **It probes the doctrine's own edges.** Re-modeled honestly, the recursive type-walk with
  cycle detection reaches a place the closed catalog may have no construct for: transient
  accumulator state during a bottom-up construction. A good run does not paper that edge with
  procedure dressed as a construct (a classmethod, an active model with no live client); it
  declares the gap and routes it to the doctrine. So the artifact also measures whether the
  team tells the truth about TCA's limits instead of hiding them.
- **It demands re-derivation, not translation.** The instruction is never "convert this." It
  is "see what it was trying to do, and model *that* as max-pure TCA," which is Einstein's
  razor: match the problem's essential structure, not the original's accidental one. The
  honest re-model is almost certainly smaller and differently shaped than 1517 lines.
- **It is a calibrated, repeatable benchmark.** The deviations are already fully mapped by a
  purity review, so the same input can be run before and after any change to the agents and
  the result *measured*: did the team resist the poison this time, get the unions disjoint,
  declare the gap rather than smuggle it? A fixed adversarial input is what turns "the agents
  feel better" into "the agents improved on this axis."

## Using it

Run the build agent team against `building_block.py`: the reviewer covers its deviations
against the authority, the architect re-derives the obligation and the construction graph
(resisting the docstrings' framing), and the forge specialists render the result under the
gate. The artifact is preserved unaltered. Its wrongness, and the persuasiveness of its
wrongness, are the test.
