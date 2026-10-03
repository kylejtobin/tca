<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.12+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSL%201.1-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSL 1.1"></a>
</p>

<p align="center"><strong>Your software's meaning lives in its types.<br>Construction is its proof.<br>Every meaning has one structural home.<br>Every structure carries one meaning.<br>Thirteen constructs. No fourteenth.</strong></p>

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

## The Test

Every meaning has exactly one structural home, and every structure carries exactly one meaning. That correspondence is the whole of TCA, applied continuously as a test.

It is one-to-one, so it fails in exactly four ways:

- **Escaped.** A meaning with no structure: it lives in a comment, a procedure, or a convention the type does not carry.
- **Duplicated.** A meaning with more than one structure: a second copy kept in agreement by hand.
- **Vacuous.** A structure with no meaning: a type minted to save repetition, a name that says nothing real.
- **Fused.** A structure with more than one meaning: several domain axes in one field, so the type tells none of them cleanly.

There is no fifth. Every forbidden pattern is one of these four, and every approved structure holds one meaning, once, proven by construction.

---

## Thirteen Shapes, No Fourteenth

You build your whole domain from thirteen declaration forms, one named shape, and one named site. Each carries one meaning and rejects the shapes that bury it: the bare primitive, the `if/elif` ladder, the mapper, the stray helper.

| Construct | What it means | What it replaces |
|---|---|---|
| [Semantic scalar](.agents/skills/python-dev-tca/constructs/semantic-scalar.md) | One atomic meaning over a primitive or closed value space | The bare primitive |
| [Value object](.agents/skills/python-dev-tca/constructs/value-object.md) | A frozen identityless product exhausted by field equality | The tuple or dict of parts |
| [Concept model](.agents/skills/python-dev-tca/constructs/concept-model.md) | A complete domain thing, durable fact, or refinement; the class is the kind | The `kind` field and the registry |
| [Union](.agents/skills/python-dev-tca/constructs/union.md) | A closed sum on one semantic axis, each variant carrying its own facts | The `if/elif` ladder and the `bool` decision |
| [Ordered union](.agents/skills/python-dev-tca/constructs/ordered-union.md) | Attempt-order construction where the strong variant's sole failure means the fallback | The `try/except` and the `.get()` returning `None` |
| [Collection](.agents/skills/python-dev-tca/constructs/collection.md) | A frozen typed sequence with meaning of its own | The mutable list and the dict used as a namespace |
| [Transformation](.agents/skills/python-dev-tca/constructs/transformation.md) | A pure implication from proven inputs to a constructed output, one expression from a closed algebra | The helper function and the service method |
| [Foreign model](.agents/skills/python-dev-tca/constructs/foreign-model.md) | Another system's shape lifted whole into a frozen model | The mapper, the adapter, the DTO |
| [Contract model](.agents/skills/python-dev-tca/constructs/contract-model.md) | This program's published request or reply, exactly the decided wire facts | The hand-built response dict |
| [Config](.agents/skills/python-dev-tca/constructs/config.md) | Environment input constructed once into a frozen settings model | The scattered `os.environ` read |
| [Route](.agents/skills/python-dev-tca/constructs/route.md) | One transport crossing, constructing ingress and projecting egress | The handler that parses by hand |
| [Effect interpreter](.agents/skills/python-dev-tca/constructs/effect-interpreter.md) | Execution of one action through one capability, constructing the observed outcome | The client call inside domain code |
| [Action](.agents/skills/python-dev-tca/constructs/action.md) | An intended external effect as a frozen value | The side effect performed in place |
| [State transition](.agents/skills/python-dev-tca/constructs/concept-model.md) | The concept-model shape whose self-typed `prior` represents succession | The mutable aggregate and the re-pointed field |
| [Composition root](.agents/skills/python-dev-tca/constructs/composition-root.md) | The site where a framework callback evaluates the per-input terminal expression | The runner, the loop, the current-state local |

Each construct has one page in the skill: the class shape, its exact configuration, and what is visible in a finished file. Every example shares one world: a trading venue's fills, the positions they fold into, and a clearing house that records, refuses, and answers empty. That world is [`world/venue.md`](.agents/skills/python-dev-tca/world/venue.md).

---

## How an Agent Builds With It

The standard is a skill an agent reads just before it writes Python, not a document it is asked to remember.

[`python-dev-tca`](.agents/skills/python-dev-tca/SKILL.md) meets the agent at the moment a procedural step comes to mind and hands it the classes that declare that step as a thing.

| The agent is about to… | It declares |
|---|---|
| do this, then that | a later fact holding the earlier fact as a field |
| check whether | a union; construction picks the variant |
| handle it failing | a refusal variant in the reply and in the outcome |
| handle there being none | a named thing for the empty case |
| handle several | a tuple held whole, or one construction for each arrival |
| read what another system sent | a route or foreign model given the raw input |
| ask another system for something | an action, one interpreter, and the raw reply given to a union |
| keep something between arrivals | a prior read on each arrival, and a successor constructed from it |

Around it:

- [`domain-discovery`](.agents/skills/domain-discovery/SKILL.md) runs before any type is written: from evidence, to decided things, to the exact constructs to build.
- [`smell-check`](.agents/skills/smell-check/SKILL.md) scans the result for the procedural patterns a model writes by habit. A build is not complete until it exits 0.
- [`code-review-tca`](.agents/agents/code-review-tca.md) is the review agent. It reads the work as written by someone looking for a way around the standard.
- [`AGENTS.md`](AGENTS.md) binds an agent to all of it.

---

## Almost None of This Is New, and That Is the Point

It is the good half of typed functional programming, domain-driven design, and a few older schools, pulled together and made to hold under one test. Two camps spent decades saying the domain's structure should come first. They were right, and ignored, because the systems that ran the work never read what they wrote. A model reads it now, and the gap they were marginalized for is the gap that costs you on every run.

---

## Start Here

- **The skill's entry point**, every moment and every construct: [`python-dev-tca/SKILL.md`](.agents/skills/python-dev-tca/SKILL.md)
- **The example world** every page is written in: [`world/venue.md`](.agents/skills/python-dev-tca/world/venue.md)
- **The signals** that a step was written where a thing belonged: [`signals.md`](.agents/skills/python-dev-tca/signals.md)
