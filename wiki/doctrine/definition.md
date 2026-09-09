---
type: Reference
description: The one principle, the core test, and the four breaks.
---

# Type Construction Architecture

## Definition

Type Construction Architecture (TCA) is a software design paradigm built on one principle: **meaning lives in the structure of the type, and construction is its proof.** A value's existence is the evidence that its constraints held, so an illegal value cannot be built. In its precise form, the principle is a one-to-one correspondence between the domain's meanings and the program's structures: every meaning has exactly one structural home, and every structure carries exactly one meaning. TCA is the continuous application of that correspondence as a test.

Carried to its conclusion, the correspondence makes the program an **executable ontology**. The domain's concepts, relations, constraints, and vocabularies are the program's types, fields, derivations, and the construction graph that joins them, not a model kept in a separate artifact the program consults. The type is the concept, the field is the relation, construction is the inference that proves a fact. Kinds nest, so a type may be a kind of a type. There is no second copy of the meaning to keep in agreement: a meaning that needed one would be a meaning with two structures, which is already the architecture failing.

Type-driven design argued this principle for the compiler, the reader that erases names and reads structure to decide what is valid. It binds harder now because a second reader has arrived. A language model reads the names and descriptions as instructions and decides what is likely, so the same declaration is read by both: the structure that proves correctness to the machine is identically what programs and bounds the model. One structure carrying one meaning is a single constraint to the machine and a single instruction to the model; a structure carrying several meanings, or a meaning smeared across several structures, dulls both readers at once. For software built on a language model, the executable ontology stops being good taste and becomes the substrate, because every gap between the meaning and the running program is paid on every inference.

## The Core Test

Every programming rule faces one question: does it hold the correspondence, or break it? Does each meaning land in exactly one structure, and does each structure mean exactly one thing? Held, a meaning is stated once, in one structure, and proven by construction. Broken, it is restated by hand, duplicated, left as noise, or fused with others. This question sorts the whole inherited rulebook into what TCA keeps and what it breaks.

## The Four Breaks

The correspondence is one-to-one, so its failures are counted, not collected: the mapping runs in two directions, and each direction fails by absence or by multiplicity. Two directions, two failures, exactly four breaks.

A meaning with **no structure** is escaped: it lives in a comment, a procedure, or a convention the type does not carry.

A meaning with **more than one structure** is duplicated: a second copy kept in agreement by hand, the same fact in two fields, one rule restated across layers.

A structure with **no meaning** is vacuous: a type minted to save repetition, a name that says nothing real, noise no reader can use.

A structure with **more than one meaning** is fused: several domain axes in one field or one label set, so the type holds them all and tells none of them cleanly.

Every forbidden pattern is one of these four because the counting allows no fifth, and every approved structure holds one meaning, once, proven by construction.

## Inherited Principles

TCA keeps the rules that build the correspondence.

- **Parse, don't validate.** Construction yields the value whose existence is the proof; nothing is left to check after it, and no unproven value moves forward.
- **Make illegal states unrepresentable.** The constraint is the edge of what the type admits, so a meaning has no illegal value to mishandle.
- **Model the domain, never the primitive.** Every domain meaning gets its own named structure that travels to every reader; a primitive with its meaning in a comment is a meaning with no structure.
- **Immutability.** A proven structure is fixed at construction, so its meaning cannot drift out from under the proof. One exception exists: the single consistency model, the one live node a context allows.

## Broken Rules

TCA breaks the inherited methodology that breaks the correspondence.

- **Validation as a step.** A separate check holds the constraint while the value moves on untyped, so the meaning escapes into the step. Construction is the check.
- **Functions as the unit of logic.** A function computing from a model's own fields is a derivation that escaped the model. Construction and derivation do the work.
- **Procedural layering.** The validator, mapper, and handler stack restates one meaning across layers. TCA keeps the structural separation, each layer owning a distinct construct, and breaks the copying.
- **Inert naming.** The name is a structure both readers consume, so a name that says nothing is a vacuous structure and a rename is a behavioral change.
- **I/O barred from domain models.** I/O is not banished; it is confined to where the graph meets time. The single unfrozen consistency model holds the live edge, and every frozen value holds none.

## Lineage

The principles above are rules; the schools below are where they were taught. Almost nothing in TCA's parts is new, and saying so is the point: the test is what is new, and it sorts each school the same way it sorts a rule. Every school below reached for the correspondence and broke it somewhere, so TCA keeps the part that holds and refuses the part that breaks, including the part a school treats as its own identity.

- **Typed functional programming** (ML, Haskell, F#, OCaml). Kept whole: the algebraic data type, which is the concept model and the union; the newtype, which is the semantic scalar; the smart constructor, which is construction as proof. Refused: the function as the unit of logic, because a function computing from a model's fields is a derivation that escaped its owner, and a pipeline of them is procedure the correspondence has no place for. TCA owes this school the most and cuts from it the deepest.
- **Railway-oriented programming** (Wlaschin). Kept: failure modeled as a value, and attempts taken in a fixed order, which is the ordered union. Refused: the `match` over the result and the bind chain that reads it, because selecting after construction re-decides what construction already settled.
- **Domain-Driven Design** (Evans). Kept whole: the ubiquitous language, which is the naming test every structure must pass, and the value object under its own name. Kept reshaped: the bounded context, unsealed so domains compose as primitives, and the aggregate, concentrated into the one consistency model a context allows. Refused: the repository and the domain service, a fetch surface and free-floating logic that the construction graph and its derivations already carry.
- **Functional core, imperative shell** (Bernhardt). Kept whole: a frozen construction graph everywhere and exactly one live node where the program meets time. This is the topology itself, not an influence on it.
- **Value and identity** (Hickey, and event sourcing). Kept: state as an identity that successively points at immutable proven values, which is the consistency model re-pointing a field, and state as the fold of immutable facts, which is `Position(prior, fill)`. Refused: the event log's ceremony and the past-tense event class that copies a fact already modeled.
- **Hexagonal architecture and the composition root** (Cockburn, Seemann). Kept: thin edges, a domain center, and dependencies constructed once at the top and injected, which are the route, the binding, and the composition root. Refused: the layer stack's copying, the DTO and the mapper restating one meaning per layer, because the foreign model lifts the outside shape whole in one construction.
- **Replace conditional with polymorphism** (Fowler). Kept as law: behavior that differs by case lives with the case, which is the same-named derivation on every union variant, held exhaustive by the checker rather than by discipline. Refused: a base class created to share fields, a second structure for one meaning. A type that is a kind of a type is the ontology nesting kinds, not that break.
- **Twelve-factor config.** Kept whole, with construction added: the environment is read once into a proven, typed config and injected, never read again.
- **Gradual typing and runtime construction** (PEP 484, pyright, Pydantic v2). Not inherited but built on: the static checker that narrows a discriminated union and the runtime that constructs and proves a value are the two readers the definition turns on, and TCA exists in the capability they opened.
