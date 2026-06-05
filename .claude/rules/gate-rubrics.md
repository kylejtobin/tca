# gate rubrics — the adjudication shapes the reviewer judges against

This rule is the single source the post-edit review judges against. It carries no path glob:
the review hook loads it. The three gates below are derived from the Four Breaks and the
closed catalog in `docs/type-construction-architecture.md`, which is the authority. Each gate
has a question, the shapes it allows, and the shapes it forbids. The deterministic gate
(`.claude/scripts/tca_gate.py`) decides the mechanically-detectable breaks first; this rubric
is the semantic residue a parser cannot decide.

A construct PASSES a gate when it matches only allowed shapes. It FAILS when it matches a
forbidden shape — cite the shape and the break (escaped, duplicated, vacuous, fused). It
ESCALATES when classification is genuinely ambiguous — name the authority section.

## Gate 1 — Type integrity (does each meaning have a structure?)

Question: is every domain value carried by a declared type whose construction proves it?

Allowed: semantic scalars (`RootModel[P]` with a `Field()` constraint or a real domain name);
frozen models composing declared types with `extra="forbid"`; collections of declared
elements; `StrEnum` as the closed value space of a scalar.

Forbidden: a bare primitive standing for a domain value (escaped). A `RootModel[str]` with
neither constraint nor genuine name (vacuous, primitive laundering). A closed vocabulary as
bare string literals (escaped).

## Gate 2 — Construction carries meaning (is each fact proven, not checked or fused?)

Question: does construction prove every invariant, with no post-proof step and no meaning
flattened?

Allowed: `Field()` constraints; reparameterization that collapses a relation into a scalar
and a derivation; an asserting `model_validator(mode="after")` that only raises a cross-field
invariant; derivations as a single returned expression over typed fields; a union of typed
result variants for a decision; variant-carried derivations read off the selected variant,
whether they return a value or a typed effect description (a frozen model).

Forbidden: a validation step that lets a checked-but-untyped value move on (escaped). A `bool`
returned as a decision (fused outcomes). A standalone function computing from a model's
fields, or a stored derivable field (escaped derivation). A `model_validator` measuring one
field against a constant (a scalar left unforged) or comparing a field to a threshold (a
decision in the wrong shape). A derivation that unwraps `.root` to primitives or assembles a
hand-formatted string (escaped meaning).

## Gate 3 — Program shape (does each module hold one meaning?)

Question: does each construct sit in its one structural home, with selection by structure not
by tag?

Allowed: disjoint unions selected by structure; a service that only binds transport; a route
that only constructs-dispatches-projects; one active model per context holding the live
clients; a variant-dependent effect read off the variant and run by one uniform emit step;
config reading the environment once; main wiring only.

Forbidden: a stored discriminator/tag or a routing function (duplicated). An `if`/`elif` or
`match` over a union, including inside the active model (duplicated dispatch). Domain logic in
a service or route (escaped). A second unfrozen model in a context (duplicated live node). A
mapper between foreign and domain (escaped — use a boundary model). A foreign handle on a
boundary model (its home is the active model). An orchestrator/pipeline sequencing work the
construction graph already orders. A `match` or branch in the active model selecting which
effect to emit, or an emit step that inspects effect kinds and picks a client call (the
forbidden dispatch relocated into the emitter); a variant-dependent effect is a typed
description read off the variant, run by one uniform emit. An effect emitted before proof.
