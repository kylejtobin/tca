<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

**Every layer of your service has something that checks it, except the one where your logic lives. TCA removes that layer. You write your business as types, and the program is correct because it constructed.**

## Who this is for

You write business services in Python: an order, a quote, a claim, a decision that depends on what a payment provider, a supplier or your own database says. You write them the way you would in Spring or ASP.NET: a controller, a request model with its validator, a service, a repository, a container that wires them, a mapper between every pair of models, and a rules engine when the logic gets thick.

Your type checker sees the request and the response. The container sees the wiring. The database sees the schema. The service sees nothing but tests, and the service is where every rule, every call and every decision is. The bug that reached production last quarter came from there, and it passed the type checker and the tests.

## What you stop doing

**You stop writing logic nothing can read.** There is no service, no handler, and no function between what arrives and what leaves. A rule is a type that cannot hold the wrong value. A decision is one type per outcome, and only the outcome that is true can exist. Your type checker reads all of it, in strict mode, because there is nothing else to read.

**You stop writing the same model three times.** What arrives, what a party says and what the business concludes are each written once. A party's answer is read by the party's own field names. Nothing maps between them.

**You stop deciding what runs first.** You say what each thing is made of, and it exists when what it is made of exists. Order falls out. A conclusion that needs a party's answer waits for it. Two questions that need nothing from each other are asked together.

**You stop shipping a program that is wired wrong.** A program with a question nothing answers, a value nothing produces, or two things that each need the other does not start. It tells you which, in the names you gave them.

**You stop writing documentation, a command line and an API.** All three are read off the types you wrote. A route is a command and an endpoint at once. The description you put on a field is what the operator sees in the shell and what the integrator sees in the API document, and it cannot drift, because it is not a copy.

**You stop writing a second way to fail.** There is one. A value the business does not have is refused, by name, whether it arrived on the command line or in a request body. A party that does not answer raises its own client's error. Nothing else fails, because nothing else runs.

## What stays yours

Pydantic. Your strict type checker. Your HTTP server. Your database. Your tracing. TCA adds no validator, no DSL, no handler and no command framework. Every construct is a documented Pydantic feature, so a developer who has read the Pydantic docs and one program can write the next route without opening the framework.

## What it costs

You cannot write a function when a type gets hard. There is no escape hatch inside your program, because an escape hatch is exactly where the unchecked logic would go. A party the framework has no library kind for is a library kind to write, not a function in your program. Some will see that as the cost. It is the point.

## The questions you will ask

**Where does the logic go?** Into types. A rule is a value that can only be built within the rule. A choice is one type per outcome, and the one whose conditions hold is the one that gets built. A conclusion is a type whose parts are what it was concluded from.

**How is the order determined?** It is not. Each thing exists when its parts exist. "Reserve before charge" is written as: the charge is made from the reservation.

**Where does state live?** With your parties, where it lives today. Within a request, the state is what has been concluded so far, and nothing concluded changes.

**What happens when a party refuses?** A refusal is an answer, and an answer is a type. The conclusion that follows from a decline is its own type, and it reaches the caller as a reply, not as an exception.

**What about a database?** A party like any other: a connection, a question, and an answer read by its column names.

**Why not FastAPI plus Pydantic?** It checks the edges. The handler between them is the service layer again. If your handler is ten lines of CRUD, use it.

**What about a coding model?** Give it the types to write and the checker that judges them. Its mistakes have nowhere unchecked to go. A value it invents is a value the program refuses.

## Neighbors, and where each is better

- **FastAPI with Pydantic**, when the logic is thin or you want to write the handler.
- **Hamilton and Dagster**, for data pipelines. They derive order from declarations too, for assets, not applications.
- **Temporal**, for execution that survives a crash and resumes days later. TCA runs one request, and runs inside Temporal when you need both.
- **ZIO and Effect**, the same idea in Scala and TypeScript.
- **A rules engine**, when people who are not developers change the rules at runtime.

## Who should not use it

Anyone not on Python. A CRUD service with few decisions. A team that wants a function when a type is in the way. A process that must survive a restart. Rules that business users edit without a deploy.

## Why it is built this way

A program is nothing but a true description of a business, and it runs because it is true. For as long as there has been software, the business lived in someone's head and the program was a translation of it into steps a machine could follow, and every bug lived in the translation. Types made the machine able to hold what you mean. TCA finishes that: the whole program is the statement of what exists in the business and what follows from what, and the statement itself is what runs. The wrong program cannot be written. The business is the program. And because the program is a world that refuses what is false, a mind can be let into it, yours or a model's, and its errors cannot run.

Write one route. If the type checker is green and the program starts, it does what you said.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
