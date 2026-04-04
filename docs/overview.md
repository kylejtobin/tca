# Overview

**Runtime:** Python 3.12+
**Construction Language:** Pydantic v2

---

## The Claim

Pydantic is a programming language. Python is its runtime.

This is not analogy. A Pydantic model is an active machine with a four-layer construction pipeline and a lazy projection surface that fires every time data enters it. Construction is proof: if the object exists, it satisfies every constraint declared in its type. If construction fails, no object exists. There is no third outcome.

```python
class DomainTrade(BaseModel, frozen=True, extra="forbid"):
    symbol: Symbol
    price: Price
    quantity: Quantity

trade = DomainTrade.model_validate(raw)  # exists = proven. no exceptions = valid.
```

The proof is relative to what the type declares. A type that declares more proves more. Much of the behavior in schema-rich systems emerges from sufficiently precise construction. Model the domain through type shape and the functionality follows from the construction graph.

---

## What TCA Replaces

Most applications hide the program in service layers. Raw data arrives, gets mapped through adapters, interpreted by service methods, enriched by helper functions, and formatted by output converters. The domain types are passive bags the service fills. Uncertain intermediate states slosh between layers.

TCA inverts this. The program lives in the domain context — frozen models, enums, constrained types, projections, and construction graphs. Routes expose context-owned contracts. Infrastructure starts the system. Services, if they exist at all, are connectors so thin they are almost embarrassing.

The app interior is railroaded by constructed certainty. There are no unmodeled uncertain intermediate states.

Unknown outcomes do not disappear. They become typed. A classifier may emit one case or many. A foreign call may succeed, fail, pend, or require review. Those are still cases, still states, still part of a declared possibility space. TCA rejects improvised controller state, untyped staging payloads, and semantic orchestration by side effect. It does not reject uncertainty; it forces uncertainty to become representable.

The dominant alternative is strings in, strings out: untyped, unproven, unconstrained. TCA replaces hope with proof.

---

## The Evaluation Model

Type Construction Architecture is the discipline of writing programs in construction semantics. The broad pattern language is larger than any one list: capture live input, normalize foreign payloads, mirror foreign schemas, compose proven models, derive on the model, declare cases instead of branching, unfold composite inputs, let one construction trigger the next, and render final shapes from owned truth.

For the dependency-ordered build path, the teaching sequence is: name the domain vocabulary, let fields declare their own constraints, own the foreign schema, absorb outer wrappers on that same boundary, hand live input to it, lift into domain truth, compose proven models, read declared surfaces, derive intrinsic facts, dispatch structurally, continue by shape when needed, chain construction from proof, and render a terminal surface. See the [README build path](../README.md#how-to-build-in-tca) for the front-door version of that sequence.

Under those visible patterns are three core mechanisms that make many of them possible:

- **Wiring**: `from_attributes` and aliases let one model read another model's declared surface.
- **Dispatch**: discriminated unions and enum-owned classification route construction into the correct case.
- **Orchestration**: projections on proven models trigger further proven construction.

These mechanisms matter because they turn isolated model proofs into programs. Construction drives derivation. Derivation drives further construction. Composition grows a semantic world through fields. Dispatch settles shape. Projection extends proof on demand. This construction-derivation graph is the evaluation model of a TCA program.

Construction is not limited to `model_validate` at a root. A model as a field on another model drives construction. A projection that constructs further proven objects extends the proof graph. A tiny function that connects proven models to further construction can still be within the discipline when it is truly an irreducible seam. The measure is whether the program is expressed as a construction and derivation graph with clear ownership, or whether it leaks back into free procedure.

---

## Proof Obligations and Roots

A TCA program is a set of proof obligations, each discharged by a root type. The first design question is not "what classes do I need?" but "what must be certain before this program can be correct?" Each answer becomes a root.

A classifier has one root. A context program typically has three: environment, action, result. A pipeline may have more. The number follows from the domain, not from a template.

Everything else — routes, event loops, infrastructure — is plumbing that hands raw data to a construction machine and receives a proven object. Many programs are far more construction-dominant than their architecture admits.

See [Roots and Proof Obligations](roots-and-proof-obligations.md) for the full treatment.

---

## Relationship to Existing Work

TCA draws on and extends several traditions.

**Parse, Don't Validate** (Alexis King, 2019). TCA is a direct realization of this principle. Construction is parsing. If it constructs, it's valid. There is no unvalidated representation. TCA extends the principle from a design heuristic into a full programming paradigm with a concrete construction language.

**Domain-Driven Design** (Eric Evans, 2003). TCA shares DDD's emphasis on ubiquitous language, bounded contexts, and making the domain model central. TCA diverges in that the domain model is not a separate representation that application code operates on; it carries the construction logic directly. Orchestration chains proofs through projections on a frozen model, not through method calls on a service class.

**Algebraic Data Types.** TCA's structural foundation is algebraic. Product types are `BaseModel` with multiple fields. Sum types are discriminated unions with `Literal` tags. Identity types are `NewType` and constrained primitives. Type families use an abstract base to define shared construction, concrete subclasses carry `Literal` tags, and a discriminated union over the subclasses dispatches. These building blocks compose into construction graphs.

**Type-Driven Development.** TCA shares the commitment to types as the primary design tool. TCA extends it by treating types not merely as constraints on computation but as computation itself. The construction pipeline is the program, not a safety net around it.

**Lazy Evaluation.** TCA's construction-derivation loop is demand-driven evaluation over a directed graph of proven values. `@cached_property` is the laziness primitive. `model_dump()` is the forcing function. This connects TCA to the lazy evaluation tradition, with one distinction: TCA's thunks produce proven objects, not arbitrary values. Each forced property extends the proof graph.

---

## How To Read The Spec

The docs are split by ownership. Enter at the point that matches your intent.

| Document | What it covers |
|:---|:---|
| [Manifesto](manifesto.md) | Why TCA exists, what we believe, what we reject |
| [The Construction Machine](construction-machine.md) | The four-layer pipeline, projection surface, and trust conditions |
| [Core Mechanisms](mechanisms.md) | Wiring, dispatch, orchestration — the deep machinery behind many construction patterns |
| [Program Architecture](program-architecture.md) | Where the program lives, the application shape, why services disappear |
| [Roots and Proof Obligations](roots-and-proof-obligations.md) | How to discover what your program must prove |
| [Principles](principles.md) | Structural, ownership, naming, and development disciplines |
| [Irreducible Seams](irreducible-seams.md) | How to tell a real seam from a modeling failure |
| [Building Block Classifier](building-block-classifier.md) | Advanced worked example showing the mechanisms and seams in a dense recursive program |
| [Semantic Index Types](semantic-index-types.md) | What changes when the consumer is neural |
| [Failure Modes](failure-modes.md) | Design diagnostics — every failure is a modeling opportunity |
