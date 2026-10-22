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

A backend application framework for Python, on Pydantic. You declare what exists in your business: the values, the facts that follow from them, the rules that compare them, the questions you ask other systems, and the conclusions you reach. A generic engine constructs those declarations, in the order their dependencies dictate, performing the external calls they require, until the reply exists. There is no service, no handler and no function between the request and the reply. There is nothing for a bug to live in that the type checker cannot read.

[`docs/architecture.md`](docs/architecture.md) says how, package by package: the run, the child runs, the proof and what it establishes, the effects, the lifecycle and the interfaces.

## Who this is for

You write business services in Python: an order, a quote, a claim, a decision that depends on what a payment provider, a supplier or your own database says. You write them the way you would in Spring or ASP.NET: a controller, a request model with its validator, a service, a repository, a container that wires them, a mapper between every pair of models, and a rules engine when the logic gets thick.

Your type checker sees the request and the response. The container sees the wiring. The database sees the schema. The service sees nothing but tests, and the service is where every rule, every call and every decision is. The bug that reached production last quarter came from there, and it passed the type checker and the tests.

## What a program looks like

A line is discounted when its total is over the threshold. In a service method that is an `if`. Here it is as declarations, and the engine builds the one that is true:

```python
class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its unit price times its quantity."""

class Small(AtMost[LineTotal, Threshold]):
    bound: Threshold = Threshold()

class Large(Beyond[LineTotal, Threshold]):
    bound: Threshold = Threshold()

class FullPrice(Fact):
    line: Line
    tier: Small
    due: LineTotal

class Discounted(Fact):
    line: Line
    tier: Large
    due: Reduced
```

The framework multiplies, compares and chooses. Exactly one of `FullPrice` and `Discounted` can exist for a line, because exactly one of `Small` and `Large` can.

## What you stop doing

**You stop writing logic nothing can read.** A rule is a type that cannot hold the wrong value. A comparison, a computed value and a choice among several are declared with their parts named. A decision is one type per outcome, and only the outcome that is true can exist. Your type checker reads all of it, in strict mode, because there is nothing else to read.

**You stop writing the same model three times.** What arrives, what a party says and what the business concludes are each written once. A party's answer is read by the party's own field names. Nothing maps between them.

**You stop deciding what runs first.** You say what each thing is made of, and it exists when what it is made of exists. Order falls out. Two questions that need nothing from each other are asked together, and you wrote no task, no gather and no schedule.

**You stop shipping a program that is wired wrong.** A program with a question nothing answers, a value nothing produces, two things that each need the other, two outcomes that could both be true, a rule its own bounds decide, or a call to a party that would be made whichever outcome held does not start. It tells you which, in the names you gave them.

**You stop writing documentation, a command line and an API.** All three are read off the types you wrote. A route is a command and an endpoint at once. The description on a field is what the operator sees in the shell and what the integrator sees in the API document, and it cannot drift, because it is not a copy.

**You stop writing a second way to fail.** A value the business does not have is refused, by name, whether it arrived on the command line or in a request body. A party that does not answer raises its own client's error. Nothing else fails, because nothing else runs.

## How it grows

The engine does not know what a discount is. It asks Pydantic for each class your program declares and keeps what constructs. Everything a business does is a kind, written once in the framework and declared by every program after, and each kind declares its meaning once, as Pydantic reads it, so the startup proof reads the same declaration construction runs. This is `AtMost`, as it is written, with its documentation removed: the one comparison every relation makes, restricted to the orderings this one admits.

```python
class AtMost[A: Numeric, B: Numeric](Compare[A, B, Literal[-1, 0]]): ...
```

Today the kinds are `Times` and `Sum` for computing, `Under`, `AtMost`, `Equal`, `AtLeast`, `Beyond`, `Differs` and `Between` for comparing, and `Least`, `Greatest`, `First` and `Only` for choosing. A kind for a temporal comparison, a set operation or a statistical measure is a class of that size, and every program gets it without a change. A party over a new transport is the same: one kind that opens the client and reads the answer, and no program contains it. Capability grows in the kinds; the engine stays the size it is.

## What stays yours

Pydantic. Your strict type checker. Your HTTP server. Your database. Your tracing. TCA adds no validator, no DSL, no handler and no command framework. Every construct is a documented Pydantic feature, so a developer who has read the Pydantic docs and one program can write the next route without opening the framework.

## What it costs

You cannot write a function when a type gets hard. There is no escape hatch inside your program, because an escape hatch is exactly where the unchecked logic would go. A party the framework has no kind for is a kind to write, not a function in your program. Some will see that as the cost. It is the point.

## The questions you will ask

**Where does the logic go?** Into types. A rule on one value is a value that can only be built within the rule. A rule that compares values is declared with the two values named, and the outcome that holds is the one that gets built. A computed value is declared with its parts named. A choice among several is declared with the several named. A conclusion is a type whose parts are what it was concluded from.

**How is the order determined?** It is not. Each thing exists when its parts exist. "Reserve before charge" is written as: the charge is made from the reservation.

**When is a party called?** When the question's parts exist, once per request. A question that must wait on an outcome is made of that outcome: a charge that must follow a passed screen holds the passed screen.

**Where does state live?** With your parties, where it lives today. Within a request, the state is what has been concluded so far, and nothing concluded changes.

**What happens when a party refuses?** A refusal is an answer, and an answer is a type. The conclusion that follows from a decline is its own type, and it reaches the caller as a reply, not as an exception.

**What about a database?** A party like any other: a connection, a question, and an answer read by its column names.

**Why not FastAPI plus Pydantic?** It checks the edges. The handler between them is the service layer again. If your handler is ten lines of CRUD, use it.

**What about a coding model?** Give it the types to write and the checker that judges them. It writes a constrained set of declarations, the same checker and the same startup proof judge them, and there is no procedure left over for you to review. A value it invents is a value the program refuses.

## Neighbors, and what each leaves you to write

| Framework | What you still write |
| --- | --- |
| Spring Boot, ASP.NET Core, NestJS | the service methods the container hands control to |
| Django, Rails | the application behavior behind the models |
| Effect, ZIO | the effectful program that composes the typed dependencies |
| Servant | the handlers the API type checks |
| TCA | declarations |

Where each is better: FastAPI with Pydantic when the logic is thin or you want to write the handler. Hamilton and Dagster for data pipelines; they derive order from declarations for assets, not applications. Temporal for execution that survives a crash and resumes days later; TCA runs one request, and runs inside Temporal when you need both. A rules engine when people who are not developers change the rules at runtime.

## Who should not use it

Anyone not on Python. A CRUD service with few decisions. A team that wants a function when a type is in the way. A process that must survive a restart. Rules that business users edit without a deploy.

## Why it is built this way

A program is nothing but a true description of a business, and it runs because it is true. For as long as there has been software, the business lived in someone's head and the program was a translation of it into steps a machine could follow, and every bug lived in the translation. Types made the machine able to hold what you mean, and every framework stopped them at the edges. TCA takes them through the middle: the whole program is the statement of what exists in the business and what follows from what, and the statement itself is what runs. The wrong program cannot be written. The business is the program. And because the program is a world that refuses what is false, a mind can be let into it, yours or a model's, and its errors cannot run.

Write one route. If the type checker is green and the program starts, it does what you said.

## Try it

```
git clone https://github.com/kylejtobin/tca && cd tca
uv sync --all-packages
uv run just check
```

The last command runs the gate: the smell check, ruff, basedpyright strict, the import contracts, bandit, and the tests that run the engine over the program the test module is. What exists today is the type system, the engine and the command line; the HTTP server is designed and not built, and `TODO.md` says what is next, in order.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
