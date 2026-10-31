<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center"><strong>Make the business model executable.</strong></p>

<p align="center">
<a href="#construction-current-status"><img src="https://img.shields.io/badge/Status-Under%20Construction-F59E0B?style=flat-square&labelColor=0d1117" alt="Status: Under Construction"></a>
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-22D3EE?style=flat-square&labelColor=0d1117" alt="License: Apache 2.0"></a>
</p>

---

TCA is a declarative, event-driven backend application framework under development. Developers name, specialize, and compose business types and supplied application constructs into one executable application model.

The supplied constructs define their execution semantics. Developers declare application-specific meaning and relationships without writing handlers, startup orchestration, or a separate workflow. Those relationships determine native execution through Pydantic, FastStream, and NATS/JetStream.

**When the business changes, change the model. Execution follows from its declarations.**

## The work we want to remove

A business rule rarely lives in one place. It appears in a model, then again in service methods, SQL transformations, integration mappings, pipelines, or workflow code. Changing the rule means finding and updating the implementations that give it effect.

TCA makes those relationships executable. A condition, the evidence that establishes it, and the operation it permits belong to the same declared program.

For an order that ships only after payment, the application names payment confirmation, shipment prerequisites, and the shipping capability. The selected constructs supply receiving, waiting, and justified execution behavior; the developer composes their application-specific relationships.

Database queries and external calls still happen through reusable capabilities. The work removed is the application-specific procedure that repeatedly translates business meaning into those operations.

## What this changes for agents

An agent maintaining conventional software must keep the implementation faithful to a business description. With TCA, the agent changes the executable model itself.

Declared constraints govern which values can construct. Explicit prerequisites govern which operations can run. Execution retains the evidence that explains why an action was justified.

This gives humans and agents the same application model to inspect, change, and test. Review still establishes whether the model expresses the right business requirements; the framework enforces the relationships that were actually declared.

## Typed composition and native execution

Business values and framework application constructs follow one bounded modeling discipline. Pydantic constructs values, Pydantic Settings constructs configuration, FastStream supplies typed invocation and resource lifecycle, and NATS/JetStream supplies routing, retained history, and delivery.

TCA derives native bindings from named application relationships. The same declarations govern activation, required evidence, results, continuation, and execution explanations. Framework constructs supply their semantics through modeled composition and native facilities.

<a id="construction-current-status"></a>
## 🚧 Current status

TCA is in active architectural development and implementation. **There is not yet a working product ready to install and evaluate.**

The single `type-construction` distribution currently exports the configuration-only
Pydantic bases `Model` and `Root` from `type_construction`. Application constructs
and native execution integrations are not yet implemented.

The product and architecture documents describe that design and its required behavior. They are the best starting point for understanding and assessing the project.

| Read | What it explains |
|---|---|
| [Product definition](docs/product.md) | The developer experience, capabilities, scope, and intended value |
| [Architecture design](docs/architecture/DESIGN.md) | The declarative foundation and Pydantic, FastStream, and NATS/JetStream responsibilities |

## Development infrastructure

The Compose stack has two services: `dev` for TCA development and `nats` with JetStream enabled. A named volume retains NATS data across container replacement. NATS is available at `nats://nats:4222` within the stack and `nats://localhost:4222` from the host.

## 🚧 Roadmap

The [outcome roadmap](docs/plan/ROADMAP.md) records current priorities. The
[task board](docs/plan/TASKS.md) tracks execution work.

## License

[Apache License 2.0](LICENSE), for the whole repository, agent instructions and skills included.
