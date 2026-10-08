<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSL%201.1-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSL 1.1"></a>
</p>

<p align="center"><strong>A program is a set of types. Constructing them is the only operation.</strong></p>

---

## The same feature, twice

A trading desk has to know what every account holds, and the clearing house is the record it answers to. When a venue reports a fill, the program updates the account's position, records it with the clearing house, and tells the desk what happened.

Here is the version everyone writes, and every coding agent writes by default:

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
async def receive_fill(request: Request) -> Response:
    return Response(
        FillReplyRoute.model_validate(
            await PersistPositionInterpreter(
                action=(
                    await ReadPositionInterpreter(
                        action=FillRoute.model_validate_json(await request.body()).fill.reading,
                        client=clearing,
                    ).interpret()
                ).persistence,
                client=clearing,
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
                await self.client.put(
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

That is the picture at the top of this page, and it is the whole method.

A procedure says: do this, then that. TCA says: the later thing holds the earlier thing. A reply holds the outcome. The outcome holds the position. The position holds the fill and the position before it, down to the flat position at the start. Order is depth, and Pydantic's constructors run it. You never write the sequence, so you cannot write it wrong. And a position is its own history: its fields are the trades that made it, back to flat.

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

A whole program is built from these declarations, in the order its files depend on each other. Each one replaces a habit.

| Construct | What it is | Lives in | What it replaces |
|---|---|---|---|
| [Semantic scalar](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/semantic-scalar.md) | One atomic meaning over a primitive or a closed vocabulary | `type.py` | The bare `str` and `Decimal` |
| [Ordered union](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/ordered-union.md) | A strong alternative whose only failure means the fallback | `type.py` | `try/except` and `.get()` returning `None` |
| [Collection](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/collection.md) | Several with a meaning of their own, as a frozen tuple | `type.py`, `value.py` | The mutable list |
| [Foreign model](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/foreign-model.md) | Another system's thing, under its names | `integration/<system>/model.py` | The mapper, the adapter, the DTO |
| [Value object](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/value-object.md) | A frozen product with no identity, equal when its fields are equal | `value.py` | The tuple or dict of parts |
| [Agent skills](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/agent-skills.md) | An agent's words and the skills it may load, as package data; its prompt's slots are exactly the fields of its value object | `prompts/` | The prompt string built in code, and the everything-prompt |
| [Union](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/union.md) | Closed alternatives on one axis, each holding its own facts | `<concept>.py` | The `if/elif` ladder and the `bool` |
| [Concept model](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/concept-model.md) | A full domain thing or durable fact, holding the one before it | `<concept>.py` | The `kind` field and the registry |
| [Action](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/action.md) | One intended external effect, as a value that performs nothing | `<concept>.py` | The side effect performed in place |
| [Contract model](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/contract-model.md) | This program's published request or reply | `api.py` | The hand-built response dict |
| [Config](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/config.md) | Deployment input, constructed once; each provider's part derives its client | `config.py` | The scattered `os.environ` read |
| [Transformation](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/transformation.md) | A fact its owner's fields determine, as one returned expression | on its owner | The helper function and the service method |
| [Effect interpreter](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/effect-interpreter.md) | The one place an action's external effect exists | `integration/<system>/interpreter.py` | The client call inside domain code |
| [Route](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/route.md) | One transport crossing, in or out | `api/<context>.py` | The handler that parses by hand |
| [Composition root](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/composition-root.md) | The config, the clients, and the callbacks, each one returned expression | `main.py`, or a package's `__init__.py` | The wiring spread through the code |

Succession is a [concept model](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/concept-model.md) with a self-typed `prior`, as `Position` is above.

## Built for the agent that writes your code

A coding agent can recite all of the above and will still write the procedural version, because reciting is recall and writing code is habit. TCA is delivered as a system that works against that, not as a document to be remembered.

- **The skill meets the agent at the moment.** [`python-dev-tca`](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/SKILL.md) is read just before the agent writes Python. It holds the three questions, the levels, the rules and one whole program; each construct page is that construct's description and its code.
- **The smell check does not negotiate.** [`smell-check`](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/smell-check/SKILL.md) scans for the free function, `isinstance`, the loop, the conditional, the dict, and the parse method. Every hit is a violation. A build is complete when it exits 0.

  ```text
  CONDITIONAL   src/venue/position.py:12:    if position is None:
  LOOP          src/venue/bids.py:8:    for bid in bids:
  DICT          src/venue/fill.py:21:    return {"sequence": sequence}
  ```

- **The reviewer assumes bad faith.** [`code-review-tca`](.agents/agents/code-review-tca.md) reads the work as written by someone looking for a way around the standard: tests that pass by construction, exceptions used as the normal path, compliance with a rule's wording that defeats its purpose.
- **The environment is modeled too.** [`docker-infra-tca`](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/docker-infra-tca/SKILL.md) holds the image, the service and the recipes a TCA project is built, checked and run in, in the same shape.

## Adopt it

1. Copy the skill directories in [`packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/`](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/) into your repository's `.agents/skills/`, and [`.agents/agents/`](.agents/agents/) into its `.agents/agents/`.
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

The example world every page of the skill is written in, with every union and derivation: [A whole program](packages/python/type-construction-agent/src/type_construction/agent/prompts/skills/python-dev-tca/SKILL.md#a-whole-program).

## The TCA agent

The agent is built in TCA and carries `python-dev-tca`, `docker-infra-tca` and `smell-check` as skills it loads when a task needs them. Install it from this repository:

```sh
pip install "git+https://github.com/kylejtobin/tca.git#subdirectory=packages/python/type-construction-agent"
```

```python
from type_construction.agent import Prompt, run_sync

answer = run_sync(Prompt(text="Model a checkout domain."))
print(answer.text.root)
```

It reads its provider, model and credentials from the environment, listed in [`.env.example`](.env.example) and in [its README](packages/python/type-construction-agent/README.md).

To work on this repository, install Docker and [just](https://github.com/casey/just), copy `.env.example` to `.env`, and run:

```sh
just build                  # the development image, with the locked dependencies
just check                  # lint, type-check, smell check, tests
just ask "Model a checkout domain."
```

## Why this, why now

The procedural version was always the cheap one on day one and the expensive one for the life of the system. Teams took that trade because modeling first looked slow.

A model that can read your field names, your variants, and your type structure removes the reason for the trade. The modeled design now arrives at the speed the shortcut used to, without the bugs listed at the top of this page.

And a type is an instruction. The same declaration that stops an invalid value from existing tells a model what is allowed to exist. One structure does both jobs, so requirements, design, code, and documentation stop being four copies of the same intent.

None of the ideas are new. This is the good half of typed functional programming and domain-driven design, held to one test and delivered in a form an agent cannot talk its way around.
