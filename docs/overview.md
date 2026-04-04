# Overview

**Runtime:** Python 3.12+
**Construction Language:** Pydantic v2

---

## The Claim

Pydantic is a programming language. Python is its runtime.

This is not analogy. A Pydantic model is an active machine with a four-layer construction pipeline and a lazy projection surface that fires every time data enters it. Construction is proof: if the object exists, it satisfies every constraint declared in its type. If construction fails, no object exists. There is no third outcome.

```python
class Customer(BaseModel, frozen=True, extra="forbid"):
    id: CustomerId           # Annotated[str, MinLen(1), MaxLen(36)]
    name: CustomerName       # Annotated[str, MinLen(1)]
    risk: RiskProfile        # nested model, fires its own construction pipeline
    segment: CustomerSegment # StrEnum, closed vocabulary

customer = Customer.model_validate(raw)  # exists = proven. no exceptions = valid.
```

The proof is relative to what the type declares. A type that declares more proves more. Much of the behavior in schema-rich systems emerges from sufficiently precise construction. Model the domain through type shape and the functionality follows from the construction graph.

---

## What TCA Replaces

Most applications hide the program in service layers. Raw data arrives, gets mapped through adapters, interpreted by service methods, enriched by helper functions, and formatted by output converters. The domain types are passive bags the service fills. Uncertain intermediate states slosh between layers.

TCA inverts this. The program lives in the domain context — frozen models, enums, constrained types, projections, and construction graphs. Routes expose context-owned contracts. Infrastructure starts the system. Services, if they exist at all, are connectors so thin they are almost embarrassing.

The app interior is railroaded by constructed certainty. There are no uncertain intermediate states.

The dominant alternative is strings in, strings out: untyped, unproven, unconstrained. TCA replaces hope with proof.

---

## The Evaluation Model

Type Construction Architecture is the discipline of writing programs in construction semantics. Three mechanisms compose them:

- **Wiring**: `from_attributes` lets one model read another's surface by name.
- **Dispatch**: discriminated unions route on tags; smart enums classify inputs into their members.
- **Orchestration**: projections on proven models construct new proven models via `@cached_property` + `model_validate`.

Orchestration is what makes this a programming paradigm. Construction drives derivation. Derivation drives further construction. This construction-derivation loop is the evaluation model of a TCA program. The loop is lazy (projections fire on first access), deterministic (frozen models guarantee evaluation-order independence), and compositional (each model's proof is independent of how it was demanded).

Construction is not limited to `model_validate` at a root. A model as a field on another model drives construction. A projection that constructs further proven objects extends the proof graph. A tiny function that connects proven models to further construction is still within the discipline. The measure is whether the program is expressed as a construction/derivation graph with clear ownership, or whether it leaks back into free procedure.

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
| [Three Mechanisms](mechanisms.md) | Wiring, dispatch, orchestration — how types compose |
| [Program Architecture](program-architecture.md) | Where the program lives, the application shape, why services disappear |
| [Roots and Proof Obligations](roots-and-proof-obligations.md) | How to discover what your program must prove |
| [Principles](principles.md) | Structural, ownership, naming, and development disciplines |
| [Irreducible Seams](irreducible-seams.md) | How to tell a real seam from a modeling failure |
| [Building Block Classifier](building-block-classifier.md) | Worked example demonstrating every mechanism |
| [Semantic Index Types](semantic-index-types.md) | What changes when the consumer is neural |
| [Failure Modes](failure-modes.md) | Design diagnostics — every failure is a modeling opportunity |
