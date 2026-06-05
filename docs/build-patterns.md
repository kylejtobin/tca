# TCA Build Patterns

This document is a companion to `docs/type-construction-architecture.md`. It does not
extend that doctrine. It operationalizes it.

The construct set is closed. The approved constructs and edges are:

- semantic scalar
- collection
- frozen model
- union
- derivation
- boundary model
- domain event
- active model
- service
- route
- config
- composition root
- projection

Anything else is meaning escaped, duplicated, vacuous, or fused.

## Construction Graph Mindset

Build as a graph, never as a pipeline of helpers.

- Nodes are declared types and constructed values.
- Edges are legal implications between those values.
- A value existing is proof that its constraints held.
- If you need a check after construction, the type is incomplete.

## Pattern 1: Declare Semantic Scalars

Own domain leaves first. A primitive in a frozen domain model is an undeclared domain.

```python
from pydantic import Field, RootModel


class InvariantName(RootModel[str], frozen=True):
    root: str = Field(min_length=1, pattern=r"^[A-Z][A-Za-z0-9_]*$")


class MessageText(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class PositiveLineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)
```

A scalar's value space may be a closed named set, not only an open range. A uniform
vocabulary, one axis with every member the same kind of thing, is a scalar whose value
space is a `StrEnum`: named in one place, proven at construction, never scattered as bare
literals and never branched on. The `StrEnum` is the value space, the role `Decimal` plays
in `RootModel[Decimal]`; the scalar is the domain type that travels and proves membership.

```python
from enum import StrEnum

from pydantic import RootModel


class Suit(StrEnum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"


class CardSuit(RootModel[Suit], frozen=True):
    root: Suit
```

## Pattern 2: Declare Collections As Domain Values

A sequence is either a field on a frozen model (`tuple[T, ...]`) or a named collection
type when the sequence itself has identity.

```python
from pydantic import RootModel


class SmellList(RootModel[tuple["Smell", ...]], frozen=True):
    root: tuple["Smell", ...]
```

Element `T` is always a declared type, never a primitive.

## Pattern 3: Construct Frozen Products From Declared Fields

Frozen models compose declared types and close shape with `extra="forbid"`.

```python
from pydantic import BaseModel, ConfigDict


class SourceLocation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file_path: "PythonFilePath"
    line_number: PositiveLineNumber


class Smell(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    invariant_name: InvariantName
    message_text: MessageText
    source_location: SourceLocation
```

No primitive fields. No stored field derivable from other fields.

## Pattern 4: Model A Closed Vocabulary By Its Dimensionality

A closed vocabulary sorts by dimensionality, not by size. A uniform vocabulary, one axis
with every member the same kind of thing, is a semantic scalar over a `StrEnum` value space
(Pattern 1). A vocabulary whose members are distinct structures, each carrying fields or
behavior the others lack, is a union of disjoint variant models: variant type is identity,
and there is no tag field and no discriminator field.

```python
from pydantic import BaseModel, ConfigDict, RootModel


class Card(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    last_four: "CardLastFour"
    expiry: "CardExpiry"


class BankAccount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    account_number: "AccountNumber"
    routing_number: "RoutingNumber"


class Wallet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    wallet_id: "WalletId"


class PaymentMethod(RootModel[Card | BankAccount | Wallet], frozen=True):
    root: Card | BankAccount | Wallet
```

A value carrying a routing number can only be a `BankAccount`; construction lands exactly one
variant because the shapes are disjoint.

When a flat vocabulary feels like a bag, it has fused several axes into one label list, and
the cure is to name the axes. `OrderStatus = {PENDING, FILLED, REJECTED, EXPIRED, ...}` fuses
lifecycle, outcome payload, and terminality at once: `FILLED` carries a fill price, `REJECTED`
carries a reason, `PENDING` carries nothing, and terminal-versus-transient cuts across all of
them. Factor it. The outcomes that carry their own payload are the variants of a union.

```python
class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    fill_price: "Price"
    filled_quantity: "Quantity"


class Rejected(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    reason: "RejectionReason"


class Pending(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    placed_at: "Timestamp"


class OrderOutcome(RootModel[Filled | Rejected | Pending], frozen=True):
    root: Filled | Rejected | Pending
```

The terminality that cut across the labels is a single axis with no payload, so it is a
variant-carried derivation, each variant returning its own `Terminality` read off the
selected outcome (Pattern 10). Two structures fall out of one bag, and neither is a label.

## Pattern 5: Use Boundary Models To Own Foreign Shape

Boundary models lift foreign data into typed truth declaratively.

```python
from pydantic import BaseModel, ConfigDict, Field


class HookToolInputBoundary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file_path: "PythonFilePath" = Field(alias="filePath")
    source_text: "FileSourceText" = Field(alias="sourceText")


class HookEventBoundary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    tool_name: "ToolName"
    tool_input: HookToolInputBoundary
```

No adapter/mapper layer between foreign payload and boundary model.

## Pattern 6: Absorb Transport Wrappers At The Same Boundary

Use `mode="before"` only in the extreme foreign-boundary case where `Field(alias=...)`,
nested boundary models, `from_attributes=True`, and direct `model_validate_json` cannot
declaratively reach the payload.

```python
from pydantic import BaseModel, ConfigDict, model_validator


class HookEnvelopeBoundary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    event: HookEventBoundary

    @model_validator(mode="before")
    @classmethod
    def _unwrap_envelope(cls, data: object) -> object:
        if isinstance(data, dict) and "payload" in data:
            return {"event": data["payload"]}
        return data
```

### Anti-pattern: Branch Parser In The Boundary Validator

```python
@model_validator(mode="before")
@classmethod
def _parse_payload(cls, data: object) -> object:
    if not isinstance(data, dict):
        return data
    if data.get("kind") == "direct":
        return {"event": {"tool_name": data["name"], "tool_input": data["input"]}}
    if data.get("kind") == "optional":
        return {"event": {"tool_name": data["name"], "tool_input": data["payload"]}}
    return {"event": {"tool_name": data["legacy_name"], "tool_input": data["legacy"]}}
```

This is wrong because it parses the payload and routes to different shapes by a tag value,
decision logic inside the validator. The legitimate `mode="before"` reaches the payload past a
single transport wrapper and nothing more; it does not classify or route.

## Pattern 7: Keep The Transport Edge Thin

At ingress, read unstable bytes and immediately construct boundary truth.

```python
import sys


raw_message = sys.stdin.read()
hook_envelope = HookEnvelopeBoundary.model_validate_json(raw_message)
```

No `json.loads` dict-carrying phase through the program.

## Pattern 8: Construct Domain Truth Directly From Proven Boundary Truth

Cross into domain by construction, not translator classes.

```python
class FileSourceText(RootModel[str], frozen=True):
    root: str


class FileContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file_path: "PythonFilePath"
    file_source_text: FileSourceText


file_context = FileContext(
    file_path=hook_envelope.event.tool_input.file_path,
    file_source_text=hook_envelope.event.tool_input.source_text,
)
```

## Pattern 9: Derive Only Intrinsic Facts

Derivation is the only behavior on a frozen value. It returns a constructed declared object
implied by the model's own fields. It never flattens those fields into a hand-formatted string
or unwraps them to primitives for presentation; a format convention is meaning escaped into a
string, and typed truth becomes data only by projection.

```python
from functools import cached_property

from pydantic import Field, RootModel


class SmellCount(RootModel[int], frozen=True):
    root: int = Field(ge=0)


class SmellList(RootModel[tuple[Smell, ...]], frozen=True):
    root: tuple[Smell, ...]

    @cached_property
    def smell_count(self) -> SmellCount:
        return SmellCount(len(self.root))
```

The derivation returns a constructed `SmellCount`, never a bare number or string. No helper
functions nested inside derivations. No bool-returning gates.

## Pattern 10: Behavior Is Carried By Variants, Not Switched

Per-variant behavior is a same-named derivation on each variant, each returning a constructed
declared object; a consumer reads it off the selected variant. Construction already chose the
variant, so there is no `match`, and the type checker requires every variant to define the
derivation, which makes the set exhaustive by construction.

```python
from functools import cached_property


class Card(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    last_four: "CardLastFour"
    expiry: "CardExpiry"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(0)


class BankAccount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    account_number: "AccountNumber"
    routing_number: "RoutingNumber"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(3)


class Wallet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    wallet_id: "WalletId"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(0)


class PaymentMethod(RootModel[Card | BankAccount | Wallet], frozen=True):
    root: Card | BankAccount | Wallet

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return self.root.settlement_days
```

Each variant returns a constructed `SettlementDays`; the envelope forwards to the selected
variant. A card and a wallet clear the same day, a bank transfer takes three, and the value lives
on the variant, chosen by construction, never by a `match`.

## Pattern 11: Active Model Is The Single Live Node

Exactly one unfrozen model per context. It holds the clients, receives live input, constructs
the domain fact from it, and emits the derived result after proof. It never branches on a
value: the analysis is a derivation, and its projection serializes whichever variant it is.

```python
from pydantic import BaseModel


class AnalysisActiveModel(BaseModel):
    bus: "EventBusClient"

    def analyze(self, hook_envelope: HookEnvelopeBoundary) -> None:
        file_context = FileContext(
            file_path=hook_envelope.event.tool_input.file_path,
            file_source_text=hook_envelope.event.tool_input.source_text,
        )
        self.bus.publish(file_context.analysis.model_dump_json())
```

The active model is exempt from immutability, not from typing rules. The source text is already
proven boundary truth from the payload, so there is no fetch; the analysis is a derivation on
`FileContext`, and the active model only constructs the fact and emits its projection.

## Pattern 12: Service Is Transport Binding Only

Service binds clients to active model. It owns no domain logic.

```python
class AnalysisService:
    def connect(self, bus: "EventBusClient") -> AnalysisActiveModel:
        return AnalysisActiveModel(bus=bus)
```

## Pattern 13: Route Is Ingress Membrane Only

Route constructs boundary truth, dispatches to active model, and projects response.

```python
def hook_route(raw_message: str, active_model: AnalysisActiveModel) -> str:
    envelope = HookEnvelopeBoundary.model_validate_json(raw_message)
    active_model.analyze(envelope)
    return AckBoundary(message=AckMessage("accepted")).model_dump_json()
```

Route defines no domain types and computes no domain meaning.

## Pattern 14: Config Is Typed, Frozen Startup Proof

Configuration is a frozen settings model built once at startup.

```python
from pydantic_settings import BaseSettings


class BusUrl(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class AnalysisConfig(BaseSettings):
    model_config = ConfigDict(frozen=True, extra="forbid")
    bus_url: BusUrl
```

No scattered `os.environ` reads.

## Pattern 15: Composition Root Is Wiring Only

`main.py` instantiates concrete clients, services, active model, and routes.

```python
def main() -> None:
    config = AnalysisConfig()  # Construct typed config proof once.
    bus = EventBusClient(config.bus_url.root)
    active_model = AnalysisService().connect(bus=bus)
    run_transport_loop(lambda raw: hook_route(raw, active_model))
```

No domain modeling and no domain decisions live here.

## Pattern 16: Domain Events Cross Process Boundaries

Established facts are projected as events and reconstructed on the far side.

```python
class AnalysisSucceededEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    file_path: "PythonFilePath"
    smell_count: "SmellCount"


serialized_event = AnalysisSucceededEvent(
    file_path=file_context.file_path,
    smell_count=SmellCount(3),
).model_dump_json()
```

The event type is the contract.

## Pattern 17: Projection Is A First-Class Edge

Projection is how typed truth leaves the graph: a structured value dumped, never a string
assembled by hand. The wire shape is the model's structure, so each part stays labeled by its
field instead of encoded in a format convention.

```python
class AnalysisResponseBoundary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    smells: "SmellList"


response_json = AnalysisResponseBoundary(smells=SmellList(())).model_dump_json()
```

Projection is not an ad hoc presenter rebuild.

## Pattern 18: Variant-Dependent Effects Are Reified, Not Switched

When which effect to emit depends on which variant a union holds, the effect is a value, not
a branch. Each variant carries a same-named derivation returning a typed effect description, a
frozen model; the active model reads it off the selected variant and emits it through one
uniform step. Construction already chose the variant, so there is no `match` to choose the
effect, exactly as there is none to choose a derived value (Pattern 10).

```python
from functools import cached_property

from pydantic import BaseModel, ConfigDict, RootModel


class OrderNotification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    recipient: "AccountId"
    headline: "NotificationHeadline"


class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    account_id: "AccountId"
    fill_price: "Price"

    @cached_property
    def notification(self) -> OrderNotification:
        return OrderNotification(
            recipient=self.account_id,
            headline=NotificationHeadline("order filled"),
        )


class Rejected(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    account_id: "AccountId"
    reason: "RejectionReason"

    @cached_property
    def notification(self) -> OrderNotification:
        return OrderNotification(
            recipient=self.account_id,
            headline=NotificationHeadline("order rejected"),
        )


class OrderOutcome(RootModel[Filled | Rejected], frozen=True):
    root: Filled | Rejected

    @cached_property
    def notification(self) -> OrderNotification:
        return self.root.notification
```

The active model reads the derivation and emits it through one uniform step:

```python
class OrderActiveModel(BaseModel):
    bus: "EventBusClient"

    def settle(self, outcome: OrderOutcome) -> None:
        self.bus.publish(outcome.notification.model_dump_json())
```

The emitter is uniform because it runs the one typed effect it is handed and never inspects it
to choose a call. A fill and a rejection notify with different payloads through the same
`publish`; the difference lives in the constructed `OrderNotification`, chosen by construction,
never by a `match`.

When the effect's channel itself varies, one literal `publish` cannot select the transport
without a branch, and the branch is the forbidden `match` relocated into the emitter. Reify the
variation as a domain event published uniformly here, and let each consuming context re-select
the variant by construction at its boundary and emit its own one uniform effect (Pattern 16).
The selection stays in construction; the emitter stays uniform. The effect description is no new
construct: it is a frozen model, variant-carried by derivation and run at the emit step, the
effect-analog of a projection.

## Forbidden Mirrors (Do Not Build These)

- Validator/normalizer/mapping pipeline that restates meaning across layers.
- A standalone enum or scattered string labels as a domain type, or branching on a vocabulary member (a uniform vocabulary is a `StrEnum`-backed scalar; distinct structures are a union).
- Stored discriminator/tag fields for union selection.
- `if`/`elif` or `match`/`case` dispatch over union identity, re-selecting what construction already chose.
- Booleans as decision outputs.
- Bare primitives in frozen domain models.
- Collections whose elements are bare primitives.
- Nested helper functions inside derivations.
- Hand-formatted strings or `.root` unwrapping inside a derivation, presentation that escapes the type; project a structured value instead.
- Domain model inheritance for field reuse.
- Foreign handles stored on boundary models.
- Second unfrozen model in one context.
- Route/service classes that compute domain meaning.
- Orchestrator/pipeline/step-runner sequencing work outside active model.
- Scattered `os.environ` reads or settings dicts outside config model.
- Versioned request-response contracts with generated clients between services.
- Emitting effects before constructing proof.
- Switching on a variant inside the active model to choose which effect to emit, instead of reifying the effect as a variant-carried value run by one uniform emit.

## Purity Check

A section in this document is valid only if all are true:

- It names one legal construct or edge from the closed set.
- Its example places meaning in declared shape, not procedural sequence.
- Constructed values are sufficient proof; no post-proof guard is needed.
- There is no value-branching: per-variant behavior, including which effect to emit, is a derivation on each variant, read off the selected one, never `match`, `if`/`elif`, a tag, or a boolean.
- Output leaves only as a projection of a structured value; no derivation flattens fields into a string.
- Any crossing is boundary or projection, never mapper code.
