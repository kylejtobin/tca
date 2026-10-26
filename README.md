<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center"><strong>Make the business model executable.</strong></p>

<p align="center">
<a href="#construction-current-status"><img src="https://img.shields.io/badge/Status-Under%20Construction-F59E0B?style=flat-square&labelColor=0d1117" alt="Status: Under Construction"></a>
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

TCA is a declarative backend application framework being built to eliminate the separately authored layer that translates a business model into application behavior.

Developers describe business values, rules, relationships, and intended outcomes. The framework derives what can be constructed and which operations are justified by the available evidence.

**When the business changes, change the model. Execution follows from its declarations.**

## The work we want to remove

A business rule rarely lives in one place. It appears in a model, then again in service methods, SQL transformations, integration mappings, pipelines, or workflow code. Changing the rule means finding and updating the implementations that give it effect.

TCA makes those relationships executable. A condition, the evidence that establishes it, and the operation it permits belong to the same declared program.

For an order that ships only after payment, the application describes the required payment evidence and its relationship to shipment. The engine obtains what is needed, waits when evidence is missing, and releases shipment when its prerequisites hold. The developer does not also write the sequence that coordinates those facts.

Database queries and external calls still happen through reusable capabilities. The work removed is the application-specific procedure that repeatedly translates business meaning into those operations.

## What this changes for agents

An agent maintaining conventional software must keep the implementation faithful to a business description. With TCA, the agent changes the executable model itself.

Declared constraints govern which values can construct. Explicit prerequisites govern which operations can run. Execution retains the evidence that explains why an action was justified.

This gives humans and agents the same structured program to inspect, change, and test. Review still establishes whether the model expresses the right business requirements; the framework enforces the relationships that were actually declared.

## 🏗️ From architectural discipline to framework

TCA brings together type-driven development, declarative modeling, and domain-driven design around construction: valid values and business conclusions are built from the evidence they require.

Early work explored that approach as a pattern developers and agents could follow. The difficult part remained implementing the construction and execution mechanics correctly.

The project now puts that responsibility in an engine. Python and Pydantic supply native value construction; reusable primitives express computations and conditions; explicit relationships supply execution meaning. The same model governs immediate work and continuation as evidence arrives over time.

<a id="construction-current-status"></a>
## 🚧 Current status

TCA is in active architectural development and implementation. **There is not yet a working product ready to install and evaluate.**

The repository contains value primitives and experimental execution code. Current work is establishing the contract that connects native construction, trusted evidence, and justified execution, including how those relationships survive delayed responses and interrupted work.

The product and architecture documents describe that design and its required behavior. They are the best starting point for understanding and assessing the project.

| Read | What it explains |
|---|---|
| [Product definition](docs/product.md) | The developer experience, capabilities, scope, and intended value |
| [Architecture](docs/TCA_ARCHITECTURAL_FOUNDATIONS.md) | The components, contracts, and execution semantics |

## License

[BSD 3-Clause with the Commons Clause](LICENSE). Agent instructions and skills under `.agents/` use [Apache 2.0](.agents/LICENSE).
