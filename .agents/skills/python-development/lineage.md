---
type: Reference
description: Where TCA's kept and refused rules were taught, school by school. Read when sorting an influence, defending a refusal, or asking what TCA owes a methodology.
---


# Lineage

The principles on [SKILL.md](SKILL.md) are rules; the schools below are where they were taught. Almost nothing in TCA's parts is new, and saying so is the point: the test is what is new, and it sorts each school the same way it sorts a rule. Every school below reached for the correspondence and broke it somewhere, so TCA keeps the part that holds and refuses the part that breaks, including the part a school treats as its own identity.

- **Typed functional programming** (ML, Haskell, F#, OCaml). Kept whole: the algebraic data type, which is the concept model and the union; the newtype, which is the semantic scalar; the smart constructor, which is construction as proof. Refused: the function as the unit of logic, because a function computing from a model's fields is a derivation that escaped its owner, and a pipeline of them is procedure the correspondence has no place for. TCA owes this school the most and cuts from it the deepest.
- **Railway-oriented programming** (Wlaschin). Kept: failure modeled as a value, and attempts taken in a fixed order, which is the ordered union. Refused: the `match` over the result and the bind chain that reads it, because selecting after construction re-decides what construction already settled.
- **Domain-Driven Design** (Evans). Kept whole: the ubiquitous language, which is the naming test every structure must pass, and the value object under its own name. Kept reshaped: the bounded context, unsealed so domains compose as primitives, and the aggregate, concentrated into the one consistency model a context allows. Refused: the repository and the domain service, a fetch surface and free-floating logic that the construction graph and its derivations already carry.
- **Functional core, imperative shell** (Bernhardt). Kept whole: a frozen construction graph everywhere and exactly one live node where the program meets time. This is the topology itself, not an influence on it.
- **Value and identity** (Hickey, and event sourcing). Kept: state as an identity that successively points at immutable proven values, which is the consistency model re-pointing a field, and state as the fold of immutable facts, which is `Position(prior, fill)`. Refused: the event log's ceremony and the past-tense event class that copies a fact already modeled.
- **Hexagonal architecture and the composition root** (Cockburn, Seemann). Kept: thin edges, a domain center, and dependencies constructed once at the top and injected, which are the route, the binding, and the composition root. Refused: the layer stack's copying, the DTO and the mapper restating one meaning per layer, because the foreign model lifts the outside shape whole in one construction.
- **Replace conditional with polymorphism** (Fowler). Kept as law: behavior that differs by case lives with the case, which is the same-named derivation on every union variant, held exhaustive by the checker rather than by discipline. Refused: inheritance as its mechanism, because a base class created to share fields is a second structure for one meaning.
- **Twelve-factor config.** Kept whole, with construction added: the environment is read once into a proven, typed config and injected, never read again.
- **Gradual typing and runtime construction** (PEP 484, pyright, Pydantic v2). Not inherited but built on: the static checker that narrows a discriminated union and the runtime that constructs and proves a value are the two readers the definition turns on, and TCA exists in the capability they opened.
