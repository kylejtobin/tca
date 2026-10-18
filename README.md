<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>


<p align="center"><strong>A program is a set of types. Constructing them is the only operation.</strong></p>

TCA is declarative and schema-first. A program is the types it declares, and the only thing that happens at runtime is a type being constructed: from what crosses a boundary, or from a type already held. Every effect is a transition from one declared state to the next, performed by a library, never by a step of ours. There is no procedural flow to write, and no place for one to hide.

---

**Contents** · [The same feature, twice](#the-same-feature-twice) · [What happened to each line](#what-happened-to-each-line) · [Each fact holds the one before it](#each-fact-holds-the-one-before-it) · [Three questions](#three-questions) · [The shapes](#the-shapes) · [Built for the agent that writes your code](#built-for-the-agent-that-writes-your-code) · [Adopt it](#adopt-it) · [The TCA agent](#the-tca-agent) · [Why this, why now](#why-this-why-now)

## The same feature, twice

A trading desk must know what every account holds, and the clearing house is the record it answers to. A venue reports a fill; the program updates the position, records it, and tells the desk. Here is the version everyone writes, and every coding agent writes by default:

```python
positions = {}

def on_fill(raw):
    body = json.loads(raw)
    fill = body["data"]["payload"]
    key = (fill["account"], fill["instrument"])
    position = positions.get(key)
    if position is None:
        position = {"net": Decimal(0)}
    if fill["side"] == "buy":
        position["net"] += Decimal(fill["quantity"])
    else:
        position["net"] -= Decimal(fill["quantity"])
    try:
        reply = client.save(position)
    except ClearingError:
        return None
    positions[key] = position
    return {"sequence": reply["sequence"], "net": str(position["net"])}
```

It works on the day it is written. It also contains these, none of which a test suite will find until production does:

- `"Buy"` with a capital B is booked as a sell: the account now holds the opposite of what it traded.
- A halted clearing house and a bug both return `None`: the desk cannot tell an unrecorded trade from a crash.
- A restart forgets every position: after a deploy, nobody knows what the firm holds.
- A refused save leaves the position changed in memory: the program believes a trade the clearing house never recorded.
- A missing `quantity` is a `KeyError` three lines after the fill was accepted: the venue gets a crash instead of a rejection.

Here is the same feature in TCA. Every class is frozen and strict; that configuration is left out here and is exact in the skill.

```python
class BuyFill(BaseModel):
    """A quantity of an instrument an account bought."""

    account: AccountId
    instrument: InstrumentId
    side: Buy
    quantity: Quantity

    @property
    def signed(self) -> NetQuantity:
        return NetQuantity(self.quantity.root)


class SellFill(BaseModel):
    """A quantity of an instrument an account sold."""

    account: AccountId
    instrument: InstrumentId
    side: Sell
    quantity: Quantity

    @property
    def signed(self) -> NetQuantity:
        return NetQuantity(-self.quantity.root)


class Position(BaseModel):
    """One account's holding in one instrument: the holding before it, and one more fill."""

    prior: "FlatPosition | Position"
    fill: Fill

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(self.prior.net_quantity.root + self.fill.signed.root)

    @property
    def persistence(self) -> PersistPosition:
        return PersistPosition(position=self)
```

Every way a trade can go is a model over its variants, and construction picks the one that happened:

```python
class Fill(RootModel[BuyFill | SellFill]):
    """A trade a venue executed for an account."""


class ClearingReply(RootModel[ClearingAcknowledgement | ClearingRefusal]):
    """What the clearing house says of a position it was asked to record."""


class PositionOutcome(RootModel[RecordedPosition | RefusedPosition]):
    """What became of a position at the clearing house."""


class FillReply(RootModel[FillBooked | FillDeclined]):
    """This program's reply to a fill."""
```

And this is the entire program that runs:

```python
config = DeskConfig()


async def receive_fill(request: Request) -> Response:
    return Response(
        FillReplyRoute.model_validate(
            await PersistPositionInterpreter(
                action=(
                    await ReadPositionInterpreter(
                        action=FillRoute.model_validate_json(await request.body()).fill.reading,
                        provider=config.clearing,
                    ).interpret()
                ).persistence,
                provider=config.clearing,
            ).interpret()
        ).model_dump_json(),
        media_type=MediaType.JSON,
    )
```

One function, one returned expression. The raw message is read once, where it arrives, and the reply is written once, where it leaves. No `if`, no `try`, no `None`, no loop, no dictionary, nothing kept between messages.

## What happened to each line

| The procedural line | What it became | What can no longer happen |
|---|---|---|
| `json.loads(raw)` and `body["data"]["payload"]` | `FillRoute.model_validate_json(...)`: the whole message given to one constructor where it arrives | a fill accepted, then dropped halfway through |
| `if fill["side"] == "buy"` | `BuyFill` or `SellFill`, picked by construction, each with its own `signed` | a sell booked from a mistyped buy; `"Buy"` constructs neither |
| `positions.get(key)` and `if position is None` | `FlatPosition`, the holding before any fill | an account's first trade crashing on a missing position |
| `position["net"] += ...` | a new `Position` that holds its `prior` and one `Fill` | a position the program believes and the clearing house never recorded |
| `positions = {}` | the prior, read from the clearing house on every fill | every position lost on a restart |
| `try` / `except` / `return None` | `ClearingRefusal`, a variant of the reply; `RefusedPosition`, of the outcome; `FillDeclined`, of what the desk receives | a refusal the desk never hears about |
| `return {...}` | `FillBooked` or `FillDeclined`, picked by construction | a reply the desk was never promised |

The clearing house's raw reply enters at one place, its interpreter, and is given whole to the union:

```python
async def interpret(self) -> PersistAttempt:
    return PersistAttempt(
        position=self.action.position,
        reply=ClearingReply.model_validate_json(
            (
                await self.provider.client.put(
                    PositionAddress.model_validate(self.action.position).path.root,
                    content=self.action.position.model_dump_json(),
                )
            ).content
        ),
    )
```

When the clearing house answers `{"error": "halted"}`, the desk is told exactly that: which position, and why it was refused.

```json
{"outcome":{"position":{"account":"A1","instrument":"ESZ6","net_quantity":"1"},"clearing":{"reason":"halted"}}}
```

Nothing was caught. The refusal was constructed, carried, and published like any other fact.

## Each fact holds the one before it

That is the picture at the top of this page, and it is the whole method. A procedure says *do this, then that*. TCA says *the later thing holds the earlier thing*: the reply holds the outcome, the outcome holds the position, the position holds the fill and the position before it, down to flat. Order is depth, and Pydantic's constructors run it, so the sequence cannot be written wrong. A position is its own history.

Every step you are about to type is a thing you have not named yet:

| You are about to… | The question it settles | You declare |
|---|---|---|
| do this, then that | What does this depend on? | a later fact holding the earlier fact as a field |
| check whether | Which case is this? | a union; construction picks the variant |
| handle it failing | What if they say no? | a refusal variant in the reply and in the outcome |
| handle there being none | What if there is nothing? | a named thing for the empty case |
| handle several | What if there are many? | a tuple held whole, or one construction for each arrival |
| read what another system sent | What exactly did they send? | a route or foreign model given the raw input where it arrives |
| ask another system for something | What do we ask, and what can come back? | an action, one interpreter, and the raw reply given to a union |
| keep something between arrivals | What do we remember between trades? | a prior read on each arrival, and a successor constructed from it |

## Three questions

Ask them of every change:

1. Remove every body. Do the types alone still specify the domain? If what remains is a pipeline, there is no model.
2. Which types are named for a stage of the run? Each is workflow inhabiting a class, and the domain thing under it has no type.
3. Are the inhabitants of the types in bijection with the states of the domain? If not, the model is wrong. Remodel from the domain; do not patch the type.

The third fails in exactly four ways:

- **Escaped.** A meaning with no structure: it lives in a comment, a procedure, or a convention. *A halted market refuses trades, says a comment.*
- **Duplicated.** A meaning with two structures, kept in agreement by hand. *The side is `"buy"` in one place and `+1` in another.*
- **Vacuous.** A structure with no meaning: a wrapper, a helper, a name that says nothing. *`PositionManager`.*
- **Fused.** A structure with two meanings that vary independently. *One `status` string for both refused and unreachable.*

There is no fifth. Every design argument reduces to which of the four it is.

## The shapes

Every type sits on one level, and its fields hold only types from the levels above it. A type you cannot place by its fields is procedure.

```text
Scalar → Value → Thing → Alternative → Crossing
```

Each construct has a page in the skill with its description and its code. Each one replaces a habit:

| Construct | Replaces |
|---|---|
| [Semantic scalar](.agents/skills/python-dev-tca/semantic-scalar.md) | the bare `str` and `Decimal` |
| [Ordered union](.agents/skills/python-dev-tca/ordered-union.md) | `try/except`, and `.get()` returning `None` |
| [Collection](.agents/skills/python-dev-tca/collection.md) | the mutable list |
| [Foreign model](.agents/skills/python-dev-tca/foreign-model.md) | the mapper, the adapter, the DTO |
| [Format type](.agents/skills/python-dev-tca/format-type.md) | the hand parser scattered through the code |
| [Value object](.agents/skills/python-dev-tca/value-object.md) | the tuple or dict of parts |
| [Provider](.agents/skills/python-dev-tca/provider.md) | the client built at import time and passed around |
| [Union](.agents/skills/python-dev-tca/union.md) | the `if/elif` ladder and the `bool` |
| [Concept model](.agents/skills/python-dev-tca/concept-model.md) | the `kind` field and the registry |
| [Action](.agents/skills/python-dev-tca/action.md) | the side effect performed in place |
| [Contract model](.agents/skills/python-dev-tca/contract-model.md) | the hand-built response dict |
| [Config](.agents/skills/python-dev-tca/config.md) | the scattered `os.environ` read |
| [Transformation](.agents/skills/python-dev-tca/transformation.md) | the helper function and the service method |
| [Effect interpreter](.agents/skills/python-dev-tca/effect-interpreter.md) | the client call inside domain code |
| [Route](.agents/skills/python-dev-tca/route.md) | the handler that parses by hand |
| [Composition root](.agents/skills/python-dev-tca/composition-root.md) | the wiring spread through the code |

Succession is a [concept model](.agents/skills/python-dev-tca/concept-model.md) with a self-typed `prior`, as `Position` is above. The whole example world, every union and derivation, is in [the whole program](.agents/skills/python-dev-tca/whole-program.md).

## Built for the agent that writes your code

A coding agent can recite all of the above and still write the procedural version, because reciting is recall and writing code is habit. TCA ships as a system that works against that, not as a document to remember.

- **The skill meets the agent at the moment.** [`python-dev-tca`](.agents/skills/python-dev-tca/SKILL.md) is read just before the agent writes Python: the three questions, the levels, the rules, a page per construct, and [one whole program](.agents/skills/python-dev-tca/whole-program.md).
- **The smell check does not negotiate.** [`smell-check`](.agents/skills/smell-check/SKILL.md) scans for the free function, `isinstance`, the loop, the conditional, the dict and the parse method. Every hit is a violation; a build is complete at exit 0.

  ```text
  CONDITIONAL   src/venue/position.py:12:    if position is None:
  LOOP          src/venue/bids.py:8:    for bid in bids:
  DICT          src/venue/fill.py:21:    return {"sequence": sequence}
  ```

- **The reviewer assumes bad faith.** [`code-review-tca`](.agents/agents/code-review-tca.md) reads the work as written by someone looking for a way around the standard: tests that pass by construction, exceptions as the normal path, compliance with a rule's wording that defeats its purpose.
- **The environment is modeled too.** [`docker-infra-tca`](.agents/skills/docker-infra-tca/SKILL.md) holds the image, the service and the recipes a TCA project is built, checked and run in, in the same shape.

## Adopt it

1. Copy [`.agents/skills/`](.agents/skills/) into your repository's `.agents/skills/`, and [`.agents/agents/`](.agents/agents/) into its `.agents/agents/`.
2. Bind your agent to it, in `AGENTS.md`:

   ```text
   You MUST use the python-dev-tca skill to make every decision.
   Before reporting any Python build complete, run the smell-check skill; a nonzero exit is not complete.
   ```

3. Put the smell check in front of every commit, in `.pre-commit-config.yaml`:

   ```yaml
   - repo: https://github.com/kylejtobin/tca
     rev: <commit>
     hooks:
       - id: smell-check
   ```

## The TCA agent

The agent that models a domain under TCA, itself built under TCA on Pydantic AI. Install it from this repository:

```sh
pip install "git+https://github.com/kylejtobin/tca.git#subdirectory=packages/python/type-construction-agent"
```

```python
from type_construction.agent import AgentConfig, Opening, PromptText, answer_sync

reply = answer_sync(AgentConfig(), Opening(text=PromptText("Model a checkout domain.")))
print(reply.answer.text.root)
```

A deployment names three things in the environment: the model, whose provider reads its own credentials there; the workspace the agent models in, local or sandboxed; and the SQLite file its runs are recorded in. [`.env.example`](.env.example) lists them and [the package README](packages/python/type-construction-agent/README.md) explains each. Next for it: the [eval](packages/python/type-construction-eval/README.md) that baselines it, then the loop as a durable flow of typed steps on Temporal.

To work on this repository, install Docker, [just](https://github.com/casey/just), [uv](https://docs.astral.sh/uv/) and [pre-commit](https://pre-commit.com), copy `.env.example` to `.env`, and run:

```sh
pre-commit install                        # the hooks, the commit gate among them
git config commit.template .gitmessage    # the shape of every commit message
just build                                # the development image, with the locked dependencies
just check                                # lint, type-check, smell check, tests
```

The commit gate asks Claude Code's two review agents whether the staged change reaches the outcome the message declares, so committing needs the [`claude`](https://docs.claude.com/en/docs/claude-code) command line; only a PASS commits.

## Why this, why now

A model that can read your field names, your variants and your type structure removes the reason the procedural shortcut was ever taken. The modeled design now arrives at the speed the shortcut used to, without the bugs listed at the top of this page.

And a type is an instruction. The declaration that stops an invalid value from existing tells a model what is allowed to exist. One structure does both jobs, so requirements, design, code and documentation stop being four copies of the same intent.

None of the ideas are new. This is the good half of typed functional programming and domain-driven design, held to one test and delivered in a form an agent cannot talk its way around.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
