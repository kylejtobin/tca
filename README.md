<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.12+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSL%201.1-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSL 1.1"></a>
<a href="https://github.com/DetachHead/basedpyright"><img src="https://img.shields.io/badge/Type%20Checked-basedpyright-22D3EE?style=flat-square&labelColor=0d1117" alt="Type Checked: basedpyright"></a>
</p>

<p align="center"><strong>Your software's meaning lives in its types.<br>The compiler proves the meaning true.<br>You bring a feature to a crew of AI agents.<br>One models it as constructs.<br>The others build it from the model.<br>One construct, one type, one file at a time.<br>No agent guessing allowed.</strong></p>

---

For decades, the best engineers argued that meaning belongs in the types:

> Model the domain, make illegal states impossible to construct, and let a value's existence prove its own correctness instead of bolting validation on after the fact.

They were right. That didn't matter. Because project management runs on one rule it rarely says out loud:

> We separate the cost of finishing the first task from the lifetime cost of what we build.

Make the first task look 75% faster, move the real cost into every month that follows, and call that delivery. That is what imperative procedural code inside a poorly typed architecture really is: not speed, but cost displacement. A loan drawn on day one and repaid for the life of the system in bug-interest toil.

AI changes that math. Radically.

Not by making the shortcut safe. By taking away the shortcut's only advantage.

The deferred-cost path had one thing to sell: visible first-day movement. It let the team arrive at "done" before the system had to prove anything. But now an LLM can read your field names, your variants, and your type structure en masse. It can help you name the domain, shape the cases, close the gaps, and build the modeled design at speed.

So the bad trade loses its cover story.

The disciplined path now gets the early movement the shortcut used to sell, without inheriting the hidden tax the shortcut always carried. You get the fast start and the durable architecture. The path they called slow and expensive becomes the one that ships cleanly, changes safely, and ages cheaply.

That is the smaller half of it.

The larger half is that a type is an instruction.

The same declaration that proves your code correct to the compiler now tells a model what is allowed to exist, and what is not. One structure carries two jobs at once:

- The constraint that stops a generator from inventing
- The context that tells it what you meant

Your types are no longer just implementation detail. They become the shared language between the compiler, the AI, and the next engineer who has to live inside the system.

That changes the center of gravity. Design, code, and documentation stop drifting apart as separate copies of intent. The domain model becomes the place intent lives. The compiler enforces it. The AI reads it. The engineer extends it.

The rigor that used to be good taste is now the thing that makes AI-built software worth trusting.

---

## The Construction Crew

The SDLC was never about building. It is a coordination protocol for multiple humans at human speed: the requirements doc, the handoffs, the standup, the roles, all of it exists to keep work split across many brains from contradicting itself. Remove the need to split the work, and the apparatus is just overhead.

<p align="center"><img src="img/tca-construction-crew.png" alt="The TCA construction crew. The operator holds authority and acceptance and dispatches the main agent. The main agent orchestrates and writes no code: it sends the request to the plan agent, receives the returned plan, sets file targets and context, dispatches the build agents in graph order, and reviews. The plan agent works the construction worksheet, selects only whitelist constructs from the MCP skill cards, and emits a validated plan through tca_construction_plan, where an off-construct entry cannot enter. The build agents each render one construct of one type into one file from its card, one agent per type per file, stacked serially when a file takes several types. The source code flows to evidence, basedpyright and pytest, which returns to the operator. A block, a meaning no card carries or a construct that will not render, returns to the operator. The fifteen construct cards feed both the plan agent's selection and the build agents' form." width="680"></p>

So this drops the apparatus. You own the product. A crew of specialized agents does the labor, each one allowed a single job:

- **The operator** is you. You hold authority and acceptance, you bring the feature, and you make the calls only you can make.
- **The main agent** orchestrates. It sends the request to the plan agent, receives the plan back, sets each construct's file target and the context a builder needs, dispatches the build agents, reviews every result, and diagnoses every block. It models nothing and writes no code.
- **The plan agent** turns the request into a validated plan. It works the construction worksheet, selects the one whitelist construct that carries each meaning from its card, and emits the plan through `tca_construction_plan`. It writes no code.
- **The build agents** build. Each renders one construct, of one type, into one file, from that construct's card. One agent per type per file, so a file holding three kinds is built by three agents in series. A build agent decides nothing; it transcribes the card's required form and leaves everything else alone.

Legality is proven where it is cheapest. An illegal construct cannot enter the plan, a build agent scoped to a single card cannot wander, and `basedpyright` and `pytest` prove what lands.

You make the calls only you can make. The walls the last era fought to tear down, dev from ops and the deeper one between the people who know the business and the people who build it, fall here for the same reason: one builder, holding the meaning, commands the whole line.

It works for a team, exactly as well. What it makes newly possible is one person owning a product at a scale that used to take a room, and the process to keep the room in sync.

---

## A Scaffold, Not a Method

You pull the repo, bring a feature, and run the loop. The starter app is a placeholder; the crew overwrites it with the system built from your plan, so you begin from a clean shape and end with your own. What is here today scaffolds the application. Templatizing the infrastructure beneath it, at cloud scale, is the next chapter.

---

## Set Against the Alternatives

<p align="center"><img src="img/table-alternatives.png" alt="Set against the alternatives. Who picks the structure: typical AI coding, the model mid-keystroke; spec-driven (Spec Kit, Kiro, BMAD), a written spec it can read past; TCA, you, in the model. What stops a wrong write: nothing; nothing; the construct boundary, before it enters the plan. When it is not sure: it guesses; it guesses; it stops and asks you. Who reviews the output: you, every line; you, every line; you review the plan, the checker proves the build." width="880"></p>

The spec-driven tools split the work across a pretend team, one agent each playing analyst, PM, architect, scrum master: waterfall with robots. The benchmarks show the bill, slower than writing the code yourself and more tokens spent re-reading its own rules than doing the work. TCA has no manager agents, because there is no room of humans to coordinate. The split is by authority, and the construct boundary, not your patience, holds the line.

---

## Fifteen Shapes, No Sixteenth

You build your whole domain from fifteen constructs. There is no sixteenth, and reaching for one is the single move the system will not allow. Each carries one meaning and rejects the shapes that bury it: the bare primitive, the `if/elif` ladder, the mapper, the stray helper.

<p align="center"><img src="img/table-constructs.png" alt="The fifteen constructs, each with what it means and what it replaces. Semantic scalar: one atomic domain value, replacing the bare primitive. Value object: a small value made of scalars with no identity, replacing the tuple or dict of primitives. Concept model: one full domain thing or fact made of declared types, replacing the dataclass, the T-or-None field, the validator. Collection: a sequence that is its own domain thing, replacing the raw list, set, or dict field. Union: a closed choice over one axis, replacing the bool, the if/elif, the isinstance ladder. Ordered union: outside data tried in order, allowed to fail, replacing the try/except that returns a default. Derivation: a fact worked out from a value's own proven fields, replacing the helper, util, or stored computed field. Foreign model: another system's shape taken in whole at the edge, replacing the mapper, adapter, DTO. Contract model: your own API request or reply shape, replacing reuse of a foreign shape. Consistency model: the one live spot where changing state collects, replacing the manager, engine, or module-level client. Verb: one change of state on the consistency model, replacing the multi-step service method. Binding: the clients tied to the consistency model, replacing the repository. Route: build a value, send it in, return the reply, replacing the handler that parses, computes, and decides. Config: the environment read once into a typed value, replacing scattered os.environ reads. Composition root: the start that wires config, clients, bindings, routes, replacing the runner, orchestrator, or step list." width="900"></p>

Every shape it rejects is one of four mistakes: a meaning with no type to hold it, the same meaning kept in two places by hand, a type that means nothing, or one type trying to mean two things. There is no fifth. That is the whole test, and the constructs enforce it by their shape: a shape that fails it cannot enter the plan.

---

## It Is Cheap to Run

- **You do not pay the model to redesign on every run.** Your design is saved as the plan. A build agent reads one construct entry; it does not work out what a `Price` is again.
- **The boundary is free.** An illegal construct fails validation at the plan tool, plain Pydantic, zero model tokens.
- **The check is deterministic.** `basedpyright` and `pytest` prove each file the same way every run, substrate not model, no tokens spent guessing.
- **It stops instead of thrashing.** When a construct will not build, the run raises a block and tells you. It cannot spin for an hour down a dead path.
- **You pay for the strong model only where it earns it.** A capable model to plan with you, a cheap one for the near-mechanical build agents, no model at all for the boundary or the checker.

---

## Almost None of This Is New, and That Is the Point

It is the good half of typed functional programming, domain-driven design, and a few older schools, pulled together and made to hold under one test. Two camps spent decades saying the domain's structure should come first. They were right, and ignored, because the systems that ran the work never read what they wrote. A model reads it now, and the gap they were marginalized for is the gap that costs you on every run.

---

## Start Here

```bash
git clone https://github.com/kylejtobin/tca && cd tca
uv sync
```

- **The whole idea**, the one rule and the four ways it breaks: [`docs/definition.md`](docs/definition.md)
- **Why the domain belongs in the running code now**: [`docs/programs-are-ontologies.md`](docs/programs-are-ontologies.md)
- **Learn it by building**: [`docs/learning-path.md`](docs/learning-path.md)
- **The crew and the loop in full**: [`.claude/README.md`](.claude/README.md)
