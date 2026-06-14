---
name: tca-topology
description: Where code belongs, what goes in which file, what each file may import, and what every file is named. MUST be consulted whenever deciding where a type, model, or file lives, what to name a new file, or which layer may import which; if a file is about to be created, placed, or named by feel, stop and read this first. Distills docs/program-topology.md; the ontology catalog's file column is written against these rules and the gate enforces them.
---

# topology

A TCA program has gravitational structure: scalars at the bottom, everything above composes from below, nothing below depends on what is above. The import arrow always points inward and downward. A file's name is domain vocabulary, never technology: `order.py`, `catalog.py`, `session.py`; never `store.py`, `handler.py`, `manager.py`, `utils.py`. The test for any filename: does it name something the domain *contains*, or something the technology *does*?

## What goes where

| File | Holds | Imports from |
|------|-------|--------------|
| `domain/<ctx>/type.py` | scalars only, the atomic vocabulary (frozen `RootModel` + its value-space enums) | stdlib, third-party; nothing from the program |
| `domain/<ctx>/value.py` | small frozen compositions of scalars | own context's `type.py` only |
| `domain/<ctx>/<concept>.py` | frozen domain models, foreign models, unions and their variants, derivations | own `type.py`/`value.py`; peer contexts' types and frozen models |
| `domain/<ctx>/<consistency model>.py` | the one unfrozen model, named for its concept (`cart.py`, never `consistency_model.py`) | all layers below, in this context |
| `domain/<ctx>/api.py` | contract models, the published shapes of the APIs this context serves, composed of declared types | own context's layers below; peer contexts' types and frozen models |
| `service/<ctx>.py` | one class, one `connect`, binds client to consistency model | the context's consistency model |
| `api/<ctx>.py` | route functions: construct, dispatch, project | contracts from `domain/<ctx>/api.py`, framework |
| `config.py` | the frozen `BaseSettings` proof | stdlib, third-party |
| `main.py` | the composition root, wiring only | `config.py`, `service/*`, `api/*` |

## The rules that decide placement

- **Semantic scalars live in `type.py` and nothing else lives there.** The gate refuses a semantic scalar row anywhere else and any other construct there.
- **Contract models live in the context's `api.py`, composed of declared types.** A foreign model is domain vocabulary like any other model: it lives in a concept-named file for the foreign thing it models, and an ordered crossing lives beside the foreign shapes it selects among.
- **A derivation lives in its model's file.** Always.
- **One unfrozen model per context**, in its own concept-named file. A second one means the context is two contexts.
- **Direction is always inward.** Domain files never import from `service/`, `api/`, `config.py`, or `main.py`. Types flow from domain toward edge; no edge file defines a type a domain file imports.
- **Peer contexts compose at the frozen layer.** `domain/order/` may import scalars and frozen models from `domain/catalog/`; the shared model lives in the context whose concept it most directly names, and when one context already depends on the other, in the depended-upon one.
- **`type.py` imports nothing from the program.** If the root looks upward, every file above it transitively inherits the cycle.

## Reading it back

Each layer answers one question: `main.py`, what composes this program; `config.py`, what the environment must provide; `service/`, what connections are held; `api/`, what surfaces exist; `type.py`, what the atomic values are; `value.py`, how they compose; `<concept>.py`, what the domain contains; the consistency model file, where live state converges; `api.py`, the contracts this context serves. Open the domain directory and the file listing is the vocabulary.

The full doctrine, with the dependency diagram, is `docs/program-topology.md`. The ontology catalog's `file` column is written against these rules, so a placement decision is made once, in the table, and the gate holds every write to it.
