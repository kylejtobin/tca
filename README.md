<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

## What it is

Type Construction Architecture (TCA) is a declarative, type-driven approach to backend applications in Python, on Pydantic. A developer declares what exists in a business: its values, the facts that follow from them, the rules that compare them, the questions asked of other systems and the conclusions reached. The framework is meant to derive execution from those declarations, so the business is not written a second time as a workflow.

## Where it is going

The target is execution across events, time and failure. An invocation pursues a declared outcome. It can wait days for external evidence, survive process loss, and recover without forgetting or repeating an external effect that already happened. Its lifetime does not depend on a request, a connection or a coroutine.

The target architecture is in [`docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`](docs/TCA_ARCHITECTURAL_FOUNDATIONS.md). Its proposals are not yet verified. The behavior a replacement must show is in [`docs/REFACTOR_ACCEPTANCE.md`](docs/REFACTOR_ACCEPTANCE.md). Those are requirements, not implemented tests.

## Current status

**The old request runtime has been removed, and its replacement is not built.** The previous engine, command line, HTTP package and demo are gone from the tree and remain in Git history. Today the repository cannot run a program. `TODO.md` lists what is not done, in order.

## What exists: the world primitives

[`packages/python/type-construction-world`](packages/python/type-construction-world) holds declarative value and computation primitives. Every class is strict, frozen and refuses undeclared fields, except `Setting`, which accepts text.

- **Values.** `Scalar`, `Setting`, `Value`, `Record`, `Fact` and `Duration`.
- **Derivations.** `Times` and `Sum` compute a value from their operands at construction. A caller cannot supply the computed result.
- **Relations.** `Under`, `AtMost`, `Equal`, `AtLeast`, `Beyond`, `Differs` and `Between` compare values, and refuse with a distinct error type when the condition does not hold.
- **Selections.** `Least`, `Greatest`, `First` and `Only` choose among the elements of a finite tuple. They do not establish that an external source is complete.

```python
class Quantity(Scalar[int]):
    """How many of a product a line asks for."""
    root: int = Field(gt=0)

class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its unit price times its quantity."""

class Small(AtMost[LineTotal, Threshold]): ...
```

`Quantity(0)` raises `ValidationError`. `Small` constructs when a line total is at most the threshold and refuses otherwise. Constructing these types validates values. It does not prove a whole business program correct, and it does not run one.

The primitives are reusable components. They are not a commitment to the previous engine or its public API.

## Install and check

```
git clone https://github.com/kylejtobin/tca && cd tca
uv sync --all-packages
uv run just check
uv run just audit
```

`just check` runs ruff, the formatter check, strict basedpyright, bandit and pytest. `just audit` checks the lockfile, known vulnerabilities, code patterns and pinned images. `just build`, `just lock` and `just shell` use the development container.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
