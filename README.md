<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

**Every layer of your service has something that checks it, except the one where your logic lives. TCA removes that layer. You write your business as types, and the program is correct because it constructed.**

## What it is

A backend framework for Python, on Pydantic. You declare what exists in your business: the values, the facts that follow from them, the rules that compare them, the questions you ask other systems and the conclusions you reach. A generic engine constructs those declarations in the order their dependencies dictate, calls the outside parties they need, and returns the reply.

No service, no handler and no function sits between the request and the reply. The type checker reads the whole program.

## The problem

In the layered habit the framework validates what arrives, the database holds the schema and the container checks the wiring. The service method holds every rule, every call and every decision, and nothing checks it but tests. The bug that reached production last quarter came from there, and it passed the type checker and the tests.

## What a program looks like

A line is discounted when its total is over a threshold. In a service method that is an `if`. Here it is declarations:

```python
class Quantity(Scalar[int]):
    """How many of a product a line asks for."""
    root: int = Field(gt=0)

class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its unit price times its quantity."""

class Reduced(Times[LineTotal, Rate]):
    """What a discounted line pays: its total at the rate."""

class Small(AtMost[LineTotal, Threshold]): ...

class Large(Beyond[LineTotal, Threshold]): ...

class FullPrice(Fact):
    line: Line
    tier: Small
    due: LineTotal

class Discounted(Fact):
    line: Line
    tier: Large
    due: Reduced
```

- **A rule is a type.** `Quantity(0)` raises `ValidationError`, and nothing downstream rechecks it, because nothing downstream can hold a bad one.
- **A decision is one type per outcome.** For a line total of 7.50, `Small` constructs and `Large` refuses, so `FullPrice` exists and `Discounted` is never built.
- **Nothing is written as procedure.** There is no `if`, no expression and no validator. The framework multiplies, compares and chooses.
- **The proof runs at startup.** It shows that exactly one of the two outcomes can exist, and the program does not start if it cannot.

## What you stop doing

- **Writing logic nothing can read.** Your strict type checker reads every rule, computation and choice, because there is nothing else to read.
- **Writing the same model three times.** What arrives, what a party says and what the business concludes are each written once, with no mappers.
- **Deciding what runs first.** A thing exists when what it is made of exists. Independent questions are asked together, with no task, gather or schedule.
- **Shipping a program that is wired wrong.** A question nothing answers, a cycle, two outcomes that could both hold, or a call made whichever outcome held stops the program at startup, in your names.
- **Writing the command line and the API by hand.** Both are read off the types, so the field descriptions you wrote are the help text and cannot drift. The command line exists today. The HTTP server is designed and not built.
- **Writing a second way to fail.** A value the business does not have is refused by name, whether it came from the shell or a request body. A party's refusal is an answer, so it reaches the caller as a reply.

## What stays yours, and what it costs

Pydantic, your strict type checker, your HTTP server, your database and your tracing stay yours. TCA adds no validator, no DSL and no handler. Every construct is a documented Pydantic feature.

You cannot write a function when a type gets hard. There is no escape hatch inside a program, because that is where unchecked logic would go. A party the framework has no kind for is a kind to write.

Do not use it if you are not on Python, if your service is CRUD with few decisions, if a process must survive a restart, or if business users edit rules without a deploy. For a thin handler, FastAPI with Pydantic is the better tool.

## Try it

```
git clone https://github.com/kylejtobin/tca && cd tca
uv sync --all-packages
uv run just check
```

The last command runs the smell check, ruff, basedpyright strict, the import contracts, bandit and the tests that run the engine. What exists today is the type system, the engine and the command line. `TODO.md` says what is next.

To go further, [`docs/architecture.md`](docs/architecture.md) explains the engine, [`.agents/skills/tca-python-dev/SKILL.md`](.agents/skills/tca-python-dev/SKILL.md) is the developer's reference, and [`docs/decisions/`](docs/decisions/) holds every design decision with its evidence.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
