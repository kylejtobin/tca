---
name: python-development
description: The construct standard for all Python code in this repo is Type Construction Architecture (TCA). In TCA meaning lives in the structure of the type, construction is its proof, every meaning has exactly one structural home and every structure carries exactly one meaning. Use when writing, reviewing, or refactoring any Python code. Covers the executable ontology, the core test, the four breaks, inherited and broken rules, program topology, the 15 constructs, naming, construction discipline, substrate verification, and lineage.
---

# Python Development

## Definition

Type Construction Architecture (TCA) is a software design paradigm built on one principle: **meaning lives in the structure of the type, and construction is its proof.** A value's existence is the evidence that its constraints held, so an illegal value cannot be built. In its precise form, the principle is a one-to-one correspondence between the domain's meanings and the program's structures: every meaning has exactly one structural home, and every structure carries exactly one meaning. TCA is the continuous application of that correspondence as a test.

Carried to its conclusion, the correspondence makes the program an **executable ontology**. The domain's concepts, relations, constraints, and vocabularies are the program's types, fields, derivations, and the construction graph that joins them, not a model kept in a separate artifact the program consults. The type is the concept, the field is the relation, construction is the inference that proves a fact. Kinds nest, so a type may be a kind of a type. There is no second copy of the meaning to keep in agreement: a meaning that needed one would be a meaning with two structures, which is already the architecture failing.

Type-driven design argued this principle for the compiler, the reader that erases names and reads structure to decide what is valid. It binds harder now because a second reader has arrived. A language model reads the names and descriptions as instructions and decides what is likely, so the same declaration is read by both: the structure that proves correctness to the machine is identically what programs and bounds the model. One structure carrying one meaning is a single constraint to the machine and a single instruction to the model; a structure carrying several meanings, or a meaning smeared across several structures, dulls both readers at once. For software built on a language model, the executable ontology stops being good taste and becomes the substrate, because every gap between the meaning and the running program is paid on every inference.

**Domain execution is a dependency graph of constructed values, never procedural orchestration.**

## The Core Test

Every programming rule faces one question: does it hold the correspondence, or break it? Does each meaning land in exactly one structure, and does each structure mean exactly one thing? Held, a meaning is stated once, in one structure, and proven by construction. Broken, it is restated by hand, duplicated, left as noise, or fused with others. This question sorts the whole inherited rulebook into what TCA keeps and what it breaks.

## The Four Breaks

The correspondence is one-to-one, so its failures are counted, not collected: the mapping runs in two directions, and each direction fails by absence or by multiplicity. Two directions, two failures, exactly four breaks. Run this test before finishing any code. Name the break or there is none.

- **escaped** — a meaning with no structure: it lives in a comment, a procedure, or a convention the type does not carry
- **duplicated** — a meaning with more than one structure: a second copy kept in agreement by hand, the same fact in two fields, one rule restated across layers
- **vacuous** — a structure with no meaning: a type minted to save repetition, a name that says nothing real, noise no reader can use
- **fused** — a structure with more than one meaning: several domain axes in one field or one label set, so the type holds them all and tells none of them cleanly

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

## Naming

Name every structure for the domain thing or fact it carries — never a pipeline stage, a data direction, or a processing step. Banned: `Record`, `Item`, `Data`, `Payload`, `Result`, `Entry`, `Info`, `Handler`, `Manager`, `Processor`, `Incoming`, `Outgoing`, `Processed`, `Enriched`, and the `Event` suffix. Test: a domain expert recognizes the thing named, without describing the data flow.

Domain files follow the same test: name for what the domain *contains*, never for what the technology *does* (`repository`, `handler`, `manager`) or for a dumping ground (`utils`, `helpers`, `common`). Full placement law is on [topology.md](topology.md).

## Topology

The construction graph is gravitational and acyclic: densest at `domain/<context>/type.py`, composing upward; nothing below imports what is above. Peer contexts compose freely at frozen layers; context boundaries seal exactly one live node.

- Every model is frozen except one [consistency model](consistency-model.md) per context.
- `type.py` and `value.py` look only downward (own scalars/values, or foundation peers — never upward).
- Types flow domain → edge: [composition root](composition-root.md), [binding](binding.md), and [route](route.md) import domain types; they do not define types domain imports.
- `service/` is binding only; `api/` route files import contracts from `domain/<context>/api.py` and define none of their own.
- When a service or route file grows interesting, domain meaning has escaped.

## Construction discipline

- Construction replaces validation: a value that fails construction does not exist as a domain value.
- Never check a value after construction, never move an unproven value forward, never store, pass, or branch on unmodeled data.
- No module-level functions; every operation belongs to the semantic structure that owns its inputs and result.
- No module-level domain values, registries, configuration, caches, clients, or `SCREAMING_SNAKE_CASE` constants; globals are meaning without an owning structure.
- A domain fact implied by a model's fields is a derivation on that model, never a free function.
- Never sequence domain work in a function, handler, processor, manager, pipeline, or orchestrator — the dependency graph between constructed values determines construction order.

## Route the thing you are building

- one atomic value → [semantic scalar](semantic-scalar.md)
- a small value, no identity → [value object](value-object.md)
- a full domain thing or fact → [concept model](concept-model.md)
- a choice on one axis → [union](union.md)
- foreign data, no identity, may fail → [ordered union](ordered-union.md)
- a sequence with its own meaning → [collection](collection.md)
- a fact of a model's fields, or a question with an input → [derivation](derivation.md)
- another system's shape → [foreign model](foreign-model.md)
- this program's API shape → [contract model](contract-model.md)
- environment values → [config](config.md)
- the entrypoint → [composition root](composition-root.md)
- transport ingress → [route](route.md)
- binding clients to the model → [binding](binding.md)
- live state plus clients → [consistency model](consistency-model.md)
- a state transition → [verb](verb.md)
- [topology.md](topology.md): Where TCA code belongs — the dependency graph, file roles, domain layers, and placement invariants. Read when placing a file, choosing an import direction, naming a domain module, or auditing whether meaning has escaped to the edge.
- [lineage.md](lineage.md): Where TCA's kept and refused rules were taught, school by school. Read when sorting an influence, defending a refusal, or asking what TCA owes a methodology.

## Substrate claims

A claim about Pydantic construction behavior requires a substrate run; a claim about gate coverage requires a gate run; a claim about basedpyright behavior requires a basedpyright run. Never add doctrine from analogy, idiom, or common Python practice.

All exemplars share one domain — venue fills, positions, and orders — and are correct to copy verbatim.
