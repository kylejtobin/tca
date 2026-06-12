# Type Construction Architecture

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Type Checked: basedpyright](https://img.shields.io/badge/type%20checked-basedpyright-cyan.svg)](https://github.com/DetachHead/basedpyright)

**Meaning lives in the structure of the type, and construction is its proof.**

For about sixty years, no consumer at an application's primary execution surface read the
program's *meaning* as instruction. Type checkers, ORMs, and schema generators read the
program's mechanism; the meaning carried by names, descriptions, and type structure was read
only by humans. That is no longer true. A neural model now reads field names, variant names,
type names, and descriptions, in the application's own language, and acts on them. Rename
`churn_risk_tier` to `x7` and the mechanism is unchanged while the model's output degrades,
because the name was load-bearing to a reader that was never there before.

This is the event Type Construction Architecture responds to. A gap that was tolerable when
humans paid the bill slowly, the domain ontology kept in one artifact and the running program
in another, reconciled by hand, now carries a per-inference price, because the reader of
meaning sits at the surface where the work happens and prices every disagreement between what
the program *says* and what it *runs*. TCA's answer is to stop keeping two copies: write the
ontology directly in the executable types, so the program that runs and the meaning it encodes
are one object.

This repository is two things, and the pairing is the point. It is **the doctrine**, the
canonical articulation of TCA, and it is **the build system** that extracts conforming TCA from
a language model whose training pulls it toward procedure on every token. The build system is
not a second copy of the rules. It is derived from them: the agents and the gate enforce exactly
what the docs state, one source and not two. The repo is itself an instance of TCA's deepest
claim, that the ontology *is* the program.

---

## What TCA is

TCA is a software design paradigm built on one principle: a value's existence is the evidence
that its constraints held, so an illegal value cannot be built. A "validation" you would write
later is a type you have not written yet. This is not a style guide. It is a continuous test
applied to every inherited pattern, *does it put meaning into the type, or accommodate meaning
escaping the type?*, that keeps the rules forcing meaning into the type and breaks the ones that
let it escape.

A TCA program is built from a **closed set of constructs**. Each is a node or an edge in a
single construction graph; whatever is not one of them is escaped meaning.

- **Semantic scalar.** A frozen `RootModel` over one primitive, carrying a constraint or a name
  that does real work. The graph's leaf; construction proves the constraint.
- **Frozen model.** A frozen `BaseModel` composing declared types into one proven product. Its
  existence is the certificate that every field's constraint held together.
- **Union.** A closed set of frozen-model variants over one domain axis, a `StrEnum` naming the
  axis and each variant pinning one member as its typed `kind`. The envelope discriminates on it,
  so construction proves which case a value is the moment it exists.
- **Collection.** A frozen `RootModel[tuple[T, ...]]` whose element is a declared type.
- **Derivation.** A fact a frozen model implies from its own proven fields. The only behavior a
  frozen value has: it cannot change, only imply. It returns a constructed declared object, never
  a bare primitive and never a hand-formatted string.
- **Boundary model.** Where foreign-shaped data is lifted into domain truth in a single
  declarative construction (`Field(alias=...)`, nested models, `model_validate_json`).
- **Consistency model.** The single unfrozen model of a context, the one node where live mutable
  state converges and the graph meets time. Its obligation is its name: every state it holds is a
  proven fact.
- **Service**, **route**, **config**, **composition root.** The thin wiring around the typed core:
  transport binding, the ingress membrane, typed startup, and the imperative shell that builds the
  core and steps back.

**Projection** (`model_dump`) is how typed truth leaves the graph as plain data. It is the exit
relation, a use of a frozen model, not a construct in its own right.

Three consequences set TCA apart from ordinary type-driven Python:

- **Identity is a field, never an inference.** Variant identity is a real domain meaning, so it
  gets the home every meaning gets: a `kind` field pinning one member of the axis's `StrEnum`,
  discriminated at construction. Shape inference fails exactly where domains are densest, variants
  with identical payloads, and a meaning living between shapes is a meaning with no structure.
- **A closed vocabulary sorts by dimensionality, not size.** A uniform one-axis vocabulary is a
  semantic scalar whose closed value space a `StrEnum` names; when members grow payloads or
  behavior, the same `StrEnum` becomes the kind axis of a union.
- **Behavior divides by where its meaning lives.** A fact a variant implies from its own fields
  is a same-named derivation on every variant, forwarded by the envelope, exhaustive by the type
  checker. What a consumer does about a variant is the consumer's meaning: one exhaustive `match`
  over the narrowed root, in the consumer, proven total by the checker. `if`/`elif` chains and
  `isinstance` ladders re-implement that dispatch without the proof and stay forbidden.

The complete construct set, with each one's forbidden mirror, is in
[`docs/type-construction-architecture.md`](docs/type-construction-architecture.md), the
authority. Nothing else in the repo may contradict it.

---

## Why now

Two traditions spent decades insisting the domain should be modeled as primary structure, and
both were right. The **ontology tradition** (RDF, OWL, knowledge graphs) said the domain should
be a formal structure of concepts and relations. The **type-theory tradition** (parse-don't-
validate, algebraic data types, dependent types) said types should carry meaning and construction
should prove correctness. Both were also marginal, for the same reason: their executors were
never the dominant production runtime. The ontology sat beside the running program; the type
system the industry shipped was not the one the PL community asked for.

A reader of meaning has now arrived at the application's primary execution surface, and it prices
every gap between the program's semantic structure and what the program actually runs, on every
inference. That converts "the ontology is the program" from a tradition's insistence into a
runtime requirement, and brings the ontology home to the surface where the work happens.
"Reflects," "is synced with," "is generated from" each contain the whole old world of two
substances reconciled by hand; "is" contains the new one. The claim is identity, not
correspondence.

The full argument, narrow on purpose and defensible against every well-actually about what
already existed, is in [`docs/executable-ontology.md`](docs/executable-ontology.md).

---

## The doctrine

The doctrine is layered, a three-part spine and three companions. Each link points to a real
file.

**The spine, what then how then why:**

- [`docs/type-construction-architecture.md`](docs/type-construction-architecture.md): **the
  what.** The definition, the four breaks, and the closed construct set. The authority.
- `.claude/skills/tca-*`: **the how.** One skill per construct: template, absolutes, substrate-proven probe
  as before-and-after build patterns in dependency order.
- [`docs/executable-ontology.md`](docs/executable-ontology.md): **the why.** Why a reader of
  meaning at the execution surface forces the ontology back into the runtime.

**The companions:**

- [`docs/proofs-and-graph.md`](docs/proofs-and-graph.md): design and audit lenses. Design from the
  obligation, read a codebase by its terminals, share a leaf by its edge.
- [`docs/program-topology.md`](docs/program-topology.md): where code lives. The dependency graph,
  file roles, and the naming principle.
- [`docs/semantic-index-types.md`](docs/semantic-index-types.md): naming as instruction. When the
  consumer reads names as meaning, a rename is a behavioral change.

**Forward, a proposition under construction, not yet doctrine:**

- [`docs/agentic-constructs.md`](docs/agentic-constructs.md): the bet that the same typed structure
  proving validity to the machine compiler is what programs and bounds the language model, so the
  prompt, the orchestration, and the governance become projections of the types rather than
  artifacts maintained beside them. It marks its own claims as floor, bet, and frontier.

---

## Building TCA with a language model that resists it

A language model fails at TCA by default. Its training corpus is overwhelmingly procedural Python,
services that hold logic, functions that compute over fields, mappers, branch-on-a-string routers,
so its generation defaults to procedural shapes even when it can state the architecture correctly
in prose. It will articulate the principle, then write a `model_validator` where a narrowed scalar
belonged, a service where a derivation belonged, an `if`/`elif` ladder where an exhaustive
`match` over a narrowed union belonged. Describing is cheap; generating fights that gravity on
every token.

Instruction alone does not fix this, because the instruction occupies one paragraph of context
while the training data occupies billions of tokens. The fix is structural, and the `.claude/`
directory is that structure: a crew of agents that produce the shape rather than request it, gated
so the breaks are unconstructable rather than discouraged. One meaning, one home, across the
pieces:

- The **authority** (`docs/`) holds the meaning, stated once.
- The **spec** (`spec/model.json`, owned by the `tca-spec` agent) is the program as a catalog of
  typed rows, designed before any code and enforced against every write after. Beside it, the
  **violation ledger** (`spec/violation.json`) holds every break observed in the tree: sentenced
  by file and symbol with a pointing note bounded by construction, kept until the violation
  leaves the tree, refused by the gate the moment an entry outlives its corpse.
- The **skills** (`.claude/skills/tca-*`) carry the making: one skill per construct, each a
  closed whitelist of allowed patterns with literal templates.
- The **agents** (`.claude/agents/`) carry disposition, not duplicated doctrine. `tca-spec`
  models the catalog and sentences violations; `tca-dev` expands rows through the skills, halts
  on any mismatch, and never marks its own work done; completion is decided by the operator.
- The **deterministic gate** (`.claude/scripts/tca_gate.py`), wired as a write-time hook, denies a
  non-conforming write before it lands, so the mechanically-decidable breaks are structurally
  impossible.

These run as a **loop**: the dev agent builds, the gate denies the breaks at write time, the
findings are fixed, and the loop repeats until every write lands clean. Correctness is the loop's
property, not any single agent's.

This crew is the active frontier of the project, the working test of the agentic-constructs bet,
and it is developed against real adversarial input. [`tests/non_conforming/`](tests/non_conforming/)
holds a substantial, deliberately non-conforming program, used to measure whether the crew can
re-derive pure TCA from code that teaches the opposite and presumes a reader who is pulled the
wrong way.

---

## Repo layout

```text
.claude/
  agents/      tca-dev (models and renders from a plan)
  rules/       the path-scoped law of each structural home, injected on file touch
  scripts/     tca_gate.py, the deterministic gate
  skills/      one tca-* skill per construct (template, allowed patterns)
  settings.json   wires the gate (PreToolUse)
app/         a minimal FastAPI skeleton, the transport shell a built core wires into
docs/        the doctrine: the spine and companions above
tca/         the TCA source tree, where built domains land
tests/       the substrate tests, and non_conforming/, the adversarial fixture
CLAUDE.md    the cognitive frame every agent builds under, plus one repo-specific block
```

[`CLAUDE.md`](CLAUDE.md) is the cognitive frame for any agent building here, plus a single
repo-specific block. Adapting it to another project means replacing that block and nothing else.

---

## Read next

- **Why this matters now**: [`docs/executable-ontology.md`](docs/executable-ontology.md)
- **What TCA is, precisely**:
  [`docs/type-construction-architecture.md`](docs/type-construction-architecture.md)
- **How to build it**: the `tca-*` skills in `.claude/skills/`
- **How to design and audit a graph**: [`docs/proofs-and-graph.md`](docs/proofs-and-graph.md)
- **Where code lives**: [`docs/program-topology.md`](docs/program-topology.md)
- **Why names are instructions**: [`docs/semantic-index-types.md`](docs/semantic-index-types.md),
  then the companion project [Semantic Index Types](https://github.com/kylejtobin/sit)
- **The agentic proposition**: [`docs/agentic-constructs.md`](docs/agentic-constructs.md)
- **Constrain a model to write TCA**: [`CLAUDE.md`](CLAUDE.md) and the agents in
  [`.claude/agents/`](.claude/agents/)

---

## Requirements

- Python 3.12+
- Pydantic 2.12+

## License

[MIT](LICENSE)
</content>
