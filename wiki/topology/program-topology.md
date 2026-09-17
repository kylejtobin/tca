---
type: Reference
description: Where TCA code belongs and which direction dependencies flow.
---

# Program Topology

The structural companion to the [definition](../doctrine/definition.md) and the [construct pages](../constructs/index.md). The construct pages define what each form is and how to build it; this page defines where that code belongs and what it may import. Well-constructed code in the wrong place is still the escaped break, because placement is a convention the type does not carry.

## Dependency Direction

Every arrow means "may depend on". The Python import graph is acyclic. A semantic type may refer recursively to itself or a forward-declared peer; every constructed runtime value remains finite and complete.

| Construct | May depend on |
|---|---|
| Semantic scalar | Pydantic and its primitive or `StrEnum` value space |
| Value object | Semantic scalars, value objects, unions, collections |
| Concept model | Semantic scalars, value objects, concept models, unions, collections; a fact that authorizes effects may also derive actions over lower-level concepts |
| Union | Alternatives on one semantic axis; the union occupies its variants' dependency layer |
| Ordered union | Domain or foreign alternatives satisfying the sole-failure fallback rule |
| Collection | Members from its own layer or a lower semantic layer |
| Transformation | Semantic scalars, value objects, concept models, unions, admitted ordered unions, collections, foreign models, contract models, actions, transformations |
| Action | Semantic scalars, value objects, concept models including state-transition shapes, unions, collections |
| Foreign model | Semantic scalars, matching domain values or concepts, and nested foreign models, unions, or collections |
| Contract model | Semantic scalars, value objects, concept models, unions, collections |
| Config | Semantic scalars, value objects, `SecretStr`, and the settings substrate |
| Route | Domain models matching ingress or supplying facts for egress projection, foreign models, and contract models |
| Effect interpreter | Actions, foreign models, concept-model or union outcomes, and one imported capability |

State transition is a concept-model shape and composition root is a site; neither adds a row. A successor fact may derive an action carrying that same fact: the two declarations share their domain module with a forward return annotation, and construction establishes the successor's fields before the derivation is read. A foreign-to-domain transformation depends on both representations only when their meanings actually differ; name or wrapper lifting is nested construction.

Peer domain contexts compose freely at every layer, because every construct is frozen and nothing is context-bound. Direction is always inward: domain modules never import from routes, interpreters, or `main.py`, and a model that serves several contexts lives in the context whose concept it most directly represents.

## Placement

```text
domain/<context>/type.py              semantic scalars
domain/<context>/value.py             value objects and their unions or collections
domain/<context>/<concept>.py         concepts, transformations, actions, transitions,
                                     and their owned unions or collections
domain/<context>/api.py               contract models
integration/<system>/model.py         foreign models
integration/<system>/<meaning>.py     necessary foreign-to-domain transformations
integration/<system>/interpreter.py   effect interpreters
api/<context>.py                      routes
config.py                             config
main.py                               one-time callback registration and per-input terminal expression
```

Domain concept files are named for their domain meaning, including files containing transformations, actions, or transitions. Several declarations in a file do not justify `transformation.py`, `action.py`, or `transition.py`; they live with their owning domain concept. `type.py`, `value.py`, and `api.py` keep their stated roles as the vocabulary and contract layers. Foreign models and interpreters live under `integration/<system>/` because their shape and names belong to the other system, so their owner is that crossing.

Technology-pattern filenames are forbidden in the domain: `store`, `repository`, `handler`, `controller`, `manager`, `processor`, `router`, and `crud`. They appear in every project regardless of domain, so they say nothing about this one. Dumping-ground names are forbidden too: `utils`, `helpers`, `common`, `misc`, and `shared`; in a TCA program every declaration belongs to a domain concept, and a declaration that cannot be placed is a fact that has not been named. The test: does the filename describe something the domain contains, or something the technology does? Declaration names follow [naming](../constructs/naming.md).

A union or collection is colocated with the layer of its variants or members and never moves those dependencies to a higher or lower layer.

## Boundaries

- Domain constructs import no SDK, framework, environment, client, database, broker, filesystem, or subprocess capability.
- Foreign models contain no live client.
- Actions contain no interpreter, client, outcome, or mutable current-state reference; an immutable state value may be an effect input.
- State transitions are immutable successor facts, not procedures; they own any action authorization but no effect execution and no current-state holder.
- Routes contain no domain decision.
- Effect interpreters contain no domain transition.
- `main.py` registers the one-expression callback once and obtains prior state through its nested read interpreter. Omitting either the read source or the evaluation site leaves wiring as escaped meaning. Current-state slots, receive loops, and domain orchestration stay out of the callback.

## Reading the Program

| Layer | Answers |
|:---|:---|
| `main.py` | What capabilities are bound, and what expression runs per input? |
| `config.py` | What does the program require from its environment? |
| `api/` | What surfaces does the program expose? |
| `integration/<system>/` | Which other systems does the program read from and act on, and in what shapes? |
| `domain/<context>/type.py` | What are the atomic values? |
| `domain/<context>/value.py` | How do those values compose? |
| `domain/<context>/<concept>.py` | What concepts does the domain contain, what do they imply, what do they authorize, and how do they succeed one another? |
| `domain/<context>/api.py` | What crosses the boundary? |

Open the domain directory and read the domain. The file listing is the vocabulary. The import graph is the dependency structure. No file is mysterious, and no file requires reading another to understand its role.
