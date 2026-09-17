---
name: python-development
description: The Type Construction Architecture standard for building Python programs as executable ontologies with Pydantic as the runtime construction substrate. Use when implementing, reviewing, or refactoring Python through the closed construct whitelist.
---

# Python Development

- [tca.md](tca.md): The executable-ontology principle, one-to-one correspondence, and four TCA breaks. Read before applying the construct whitelist.
- [construction.md](construction.md): How construction proves admitted meanings and preserves completed facts. Read when defining construction, refusal, immutability, or successor semantics.
- [pydantic.md](pydantic.md): How Pydantic executes TCA construction graphs as the runtime construction substrate. Read before implementing or interpreting any whitelisted construct.
- [construct-selection.md](construct-selection.md): How to select among thirteen declaration forms and distinguish named shapes and sites. Read before introducing program structure.
- [topology.md](topology.md): How TCA constructs compose through an acyclic dependency graph from semantic types to runtime boundaries. Read when placing code or choosing dependency direction.
- [constructs/semantic-scalar.md](constructs/semantic-scalar.md): How one admitted atomic meaning is constructed over a primitive or closed value space. Read when a value has independent identity, vocabulary, units, or constraints.
- [constructs/value-object.md](constructs/value-object.md): How a frozen identityless product is constructed and compared by value. Read when a descriptive or measured meaning is exhausted by its field values.
- [constructs/concept-model.md](constructs/concept-model.md): How a frozen complete domain thing or fact is constructed from declared meanings. Read when modeling a full concept, refinement, or durable fact.
- [constructs/union.md](constructs/union.md): How a closed algebraic sum represents alternatives with variant-specific facts. Read when one semantic axis has multiple valid shapes.
- [constructs/ordered-union.md](constructs/ordered-union.md): How attempt order constructs alternatives when the strong variant can fail only for the declared fallback. Read when proving membership or admitting another failure-exhaustive choice.
- [constructs/collection.md](constructs/collection.md): How a typed sequence or association is constructed when the collection has meaning of its own. Read when order, multiplicity, uniqueness, keys, or collection constraints matter.
- [constructs/transformation.md](constructs/transformation.md): How a pure typed transformation maps proven inputs to a constructed output. Read when deriving, calculating, querying, folding, or converting program meanings.
- [constructs/foreign-model.md](constructs/foreign-model.md): How another system's representation is lifted into a frozen typed boundary model. Read when foreign shape or vocabulary differs from the program's meaning.
- [constructs/contract-model.md](constructs/contract-model.md): How this program's request or reply contract is constructed and serialized. Read when defining a program-owned external interface.
- [constructs/config.md](constructs/config.md): How environment and deployment input constructs frozen typed configuration. Read when adding settings, environment variables, defaults, or secrets.
- [constructs/composition-root.md](constructs/composition-root.md): Where a framework callback evaluates the per-input terminal expression. Read when registering the program boundary or wiring read and write interpreters.
- [constructs/route.md](constructs/route.md): How transport ingress constructs typed input and projects declared output. Read when implementing an HTTP, CLI, message, stream, or framework entrypoint.
- [constructs/effect-interpreter.md](constructs/effect-interpreter.md): How typed actions are executed through concrete external capabilities and observed outcomes are constructed. Read when binding effects to clients, storage, subprocesses, or transports.
- [constructs/state-transition.md](constructs/state-transition.md): How a concept model's prior field represents immutable succession. Read when using the state-transition shape without mutation or procedural state management.
- [constructs/action.md](constructs/action.md): How a frozen typed value describes one intended external effect without executing it. Read when an effect request must be inspected, routed, persisted, retried, or interpreted.
