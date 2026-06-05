# TCA — Agentic Constructs

*A foundational-proposition document. It transfers the complete context a build team
needs to locate and construct this component of TCA. It is not an implementation: it
defines no constructs, ships no code, and names nothing as doctrine. Locating and
naming the constructs is the build team's act of construction.*

*Every statement below is one of three things, and is marked as such: an **established
floor** the team builds on, a **bet** the team is being asked to construct and prove, or
an **open frontier** stated with the test that closes it. A statement that is none of
these does not belong in this document.*

---

## The proposition

A TCA program is written in Pydantic. A Pydantic frozen model is read by two consumers
that disagree about what it is.

The **machine compiler** erases the field names and reads structure — arity, types,
constraints, construction invariants. It decides what is *valid*.

The **neural compiler** (the language model) reads the field names and descriptions as
instructions. It decides what is *likely*.

The same Pydantic declaration. Two interpreters. TCA already forces meaning into the
structure so the machine compiler proves correctness. The proposition is that this is
*identically* what programs the neural compiler — that the structure written to satisfy
the first reader is the program, the context, and the governance for the second.

So in a TCA system whose substrate includes a language model, the Pydantic types are not
only the domain model. They are simultaneously the program given to the neural compiler,
the context it reads, and the constraint that bounds it. The prompt, the orchestration,
and the guardrails are not separate artifacts maintained alongside the types. They are
projections of the types.

That collapse — four hand-maintained artifacts into one declaration read by two
interpreters — is the proposition this component rests on. TCA's principle was *meaning
lives in the structure, and construction is its proof*. That principle was written for
the machine compiler. It fits the neural compiler, which executes meaning directly, at
least as well — and the architecture was not designed for that reader. This component is
the recognition of that fit, not an extension bolted onto it.

---

## The established floor

These the build team can stand on without re-deriving. They are established or follow
directly from definitions.

**The neural compiler conditions on a name's meaning, not its identity.** Every prior
runtime reader of a name — a serializer key, an ORM column, a dispatcher — reads it as an
opaque key and stays invariant under consistent renaming: change the name everywhere at
once and behavior is preserved, because nothing read what the name *meant*. The neural
compiler is the first reader that breaks this. Rename a Pydantic field in a way that
changes its meaning, and the model's behavior changes even when every machine-reader is
updated in lockstep. This is why the schema is part of the inference surface — read going
in, not only checked coming out — and why field names and descriptions are not labels but
instructions the model executes.

**A name can only steer where the input left the answer undetermined, and the type caps
how far.** A field's name moves the model's output only into the room the input left
open; on an input that already pins the answer, the name is worth nothing, and on an
ambiguous one it can drive the whole choice. Crucially, a narrow Pydantic type — a
two-or-three-variant union, a constrained scalar — caps how far *any* instruction in the
name can move the output, on *every* input. A wide `str` field leaves that room uncapped.
This is the floor under the governance claim: the bound is a property of the Pydantic
type, holding for all inputs, not a behavioral hope. (The information-theoretic identity
that proves this — the output's uncertainty splitting into room-the-input-leaves,
room-the-name-takes, and noise — is the justification, available to the team as the
proof. The instrument they hold is the Pydantic type whose variant count sets the ceiling.)
The bound holds for all inputs, so it caps the model's own default as much as any
instruction in the name: the same ceiling that limits a poisoned instruction limits the
gradient's pull toward a procedural shape. At the limit the bound is absolute, a form with
no variant in the output type is not merely unlikely but unconstructable, absent from what
the model can emit at all.

**A constructed Pydantic value already carries its guarantee.** This is parse-don't-
validate at whole-program scope: a value that exists has satisfied everything its type
declares. So one Pydantic declaration does three jobs the field currently splits across
three artifacts — it *instructs* (names and descriptions, read by the neural compiler),
it *constrains* (types and unions, read by the machine compiler), and it *certifies*
(construction is the proof). The prompt template, the validation pipeline, and the
orchestration glue are not three things kept in sync. They are one declaration.

**Projection is the doctrine's only sanctioned exit, and it is now the program's voice to
its own compiler.** TCA already holds that typed truth leaves the graph only by
projection (`model_dump` / `model_dump_json`), and that a hand-assembled string is the
escape it forbids. This component points that existing edge at the neural compiler: the
prompt the model receives is a projection of the construct graph, never a string the graph
assembles. The edge the doctrine treats as "not a construct in its own right" is, on this
horizon, the most load-bearing relation in the system — the place where the two compilers
meet on one artifact. And because it is a projection it is computed at the crossing, not
stored. A prompt written to a file, even one generated from the types, is a second copy
that can drift, the two-substance gap reappearing one layer in. The faithful form
materializes nothing: the instruction exists only as the projection of the graph at the
moment the model is called.

---

## The bet

These the team is being asked to construct and prove. They are well-motivated by the
floor and by converging evidence from the field, and they are not yet demonstrated in
this substrate. They are stated as bets so the document's foundation is not confused with
its wager.

**The prompt is the projection of composed Pydantic types, not a hand-written string.**
When the cognitive work is modeled as types, what is left to project at each step is only
the irreducible instruction for that step — its framing arrives as the typed inputs it
received, structurally present rather than restated in prose. The projected prompt per
step is therefore smaller and more precise than any hand-written prompt, because the graph
carries what the prose used to. The bet is that this is faithful and complete — that the
projection is byte-for-byte what the model needs, with no meaning re-escaping into a hand-
formatted string at the crossing.

**The prompting strategies the field has catalogued are real, composable Pydantic
constructs.** Chain-of-thought, reflection, verification, few-shot, decomposition and the
rest have stable identity, compose, and separate the cognitive *what* from the prompted
*how* — the field has independently reified exactly this separation, and it holds.
Modeled as Pydantic constructs, they form a cognitive layer of TCA's catalog that does not
exist today: composable primitives for reasoning, each certified by construction.

**Orchestration is escaped meaning, and the construction graph replaces it.** The
dependency between cognitive facts is the sequence; an orchestrator that sequences the work
is that dependency restated procedurally. Each cognitive step is a node whose inputs are
proven prior facts — its context — and whose Pydantic type bounds its output — its
guardrail. The flow between steps is dependency between constructed values, not a procedure
someone wrote.

**The agent is a cognitive primitive, and its loop is owned by the primitive, not by the
program.** A Pydantic AI agent carries its tools, its projected instructions, and its
output type, and runs the think / call-tool / observe cycle internally, terminating by
constructing a typed value. The active model — the single live node where the graph meets
time — invokes the agent with proven inputs and receives the landed value. The loop is not
in the program's control flow; it is inside the primitive, so the program never branches
on an intermediate result. The agent is wired into the graph by the transport fork TCA
already decides: as a client field on the active model when the cognition is in-graph, or
as a domain event across a boundary when it is cross-process.

**Termination is a union variant constructed, so the active model never branches.** The
agent's output type is a union, and the loop ends by the model being forced to land one
variant — the boundary crossing pointed at the neural compiler. Every outcome must be
expressible as a variant the agent can land: success, ambiguity, each failure, and budget-
exhaustion. The bet is that this is exhaustive — that no outcome resists being a variant
and forces a guard back into the active model's code. The active model then constructs the
inputs, runs the agent, reads the landed variant's own derivation, and emits. No value-
branch anywhere.

**A builder's output type can be the construct catalog itself, so a nonconforming form is
unrepresentable rather than merely discouraged.** When the thing under construction is
code, the agent need not emit code as text. Its output type can be a closed grammar of the
catalog's constructs, and a deterministic projection renders that value to source. A
grammar with no procedural variant cannot express a procedural shape, so the drift the
model would otherwise produce is not forbidden by instruction but absent from what it can
construct, and conformance becomes a property of the output type rather than a review
performed afterward. The bet is that the grammar can be made complete enough to express
every legal construct without loosening enough to readmit the escaped forms, which is the
over-constraint dial named below, measured per construct by building.

---

## The open frontiers

These the team must treat as unsolved. Each is closed by building and running the named
test, not by argument.

**Is the cognitive layer a type system or a glossary?** Take two catalogued strategies,
strip the names, and apply the deletion test: is there real structural difference between
them, or only relabeled prose? Some may collapse to one construct; some may prove to be a
constrained scalar rather than a union; some may be primitive laundering — a named type
carrying no real structure. The cognitive layer is real only for the constructs that
survive this test.

**Does the per-field bound compose to a system?** The information bound sizes one field's
channel. It says nothing about a name in one field reframing how the model reads another;
that cross-field coupling lives in a larger joint quantity that no single-field ceiling
caps. An end-to-end optimizer tuning the semantic channel is the entity most likely to
*find* such couplings, because it optimizes the joint objective and does not respect field
boundaries. Whether a system-level guarantee exists, and what construct carries it, is
open. The resolution is measurement of cross-field influence, not assertion. A coupling the
optimizer finds is to be treated as the signal that a construct has not yet been located —
a real dependency the graph has not captured — never as a behavior to keep.

**Does the crossing preserve meaning-as-structure, or re-escape it?** The structure must
cross into the model in some projected form. Whether that projection preserves the meaning-
in-structure property, or quietly reintroduces a serialization step where meaning re-
escapes into a string and the advantage leaks away, is not settled by the philosophy. It
is observed by building one node end-to-end and checking the projection against what the
model actually receives.

**Does over-constraint strangle the cognition it was meant to bound?** Narrowing a type
moves a failure from the semantic channel (merely unlikely) to the structural channel
(impossible) — but constraining too far can reduce the model's reasoning quality on the
step itself. Where the dial sits, per field, is found by the development loop — steer with
the name, observe where it fails, harden the failure into structure — not chosen in
advance. The bound is the exchange rate; the right setting is empirical.

---

## What this component opens

Stated as the consequence it is, not as a result. If the bets hold and the frontiers
resolve, this component yields what the field is currently building by hand and failing
at: governance as a structural quantity rather than a behavioral discipline — a Pydantic
type's variant count provably caps how far any instruction, including a poisoned one, can
move the model, on every input; a reusable library of cognitive constructs, certified by
construction; the elevation of projection from a humble exit to the program's voice to its
own compiler; and a development loop in which the semantic channel can be optimized inside
a structurally certified ceiling it cannot breach — optimization that is safe by
construction. These are the upside the component is a bet on. They are collected by
building, not by argument.

---

## Out of scope for this document

No construct definitions. No Pydantic class layouts or `output_type` union designs. No
Pydantic AI wiring patterns. No per-case client-versus-event transport decision. No
implementation sequencing. No rewrite of existing prompt examples. No doctrinal name for
this component. Locating, naming, and constructing the constructs is the build team's work,
and pre-specifying it here would be the forward-projection the doctrine forbids: the felt
need to name a construct now is the signal that the construct has not yet been found.
