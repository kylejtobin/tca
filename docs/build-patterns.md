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
- consistency model
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
(Pattern 1). When members grow payloads or behavior a sibling lacks, the same `StrEnum`
becomes the kind axis of a discriminated union: each variant pins exactly one member as its
typed `kind` field, and the envelope discriminates on it. Variant identity is a real domain
meaning, and the kind field is its one structural home.

```python
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel


class PaymentMethodKind(StrEnum):
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    WALLET = "wallet"


class Card(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.CARD] = PaymentMethodKind.CARD
    last_four: "CardLastFour"
    expiry: "CardExpiry"


class BankAccount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.BANK_ACCOUNT] = PaymentMethodKind.BANK_ACCOUNT
    account_number: "AccountNumber"
    routing_number: "RoutingNumber"


class Wallet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.WALLET] = PaymentMethodKind.WALLET
    wallet_id: "WalletId"


class PaymentMethod(RootModel[Card | BankAccount | Wallet], frozen=True):
    root: Card | BankAccount | Wallet = Field(discriminator="kind")
```

Construction reads the kind and lands exactly one variant, an O(1) lookup with exact
per-variant errors. The kind field carries identity where shape inference cannot: two
variants with identical payloads (every reversible operation, every symmetric outcome a
decision produces) differ in nothing but identity, so identity is a field or it is nowhere.
A raw-string `kind`, or the axis enum unpinned (`kind: PaymentMethodKind`), is not identity:
it admits every member on every variant. `Literal` pins exactly one.

When a flat vocabulary feels like a bag, it has fused several axes into one label list, and
the cure is to name the axes. `OrderStatus = {PENDING, FILLED, REJECTED, EXPIRED, ...}` fuses
lifecycle, outcome payload, and terminality at once: `FILLED` carries a fill price, `REJECTED`
carries a reason, `PENDING` carries nothing, and terminal-versus-transient cuts across all of
them. Factor it. The outcomes that carry their own payload are the variants of a union.

```python
class OrderOutcomeKind(StrEnum):
    FILLED = "filled"
    REJECTED = "rejected"
    PENDING = "pending"


class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.FILLED] = OrderOutcomeKind.FILLED
    fill_price: "Price"
    filled_quantity: "Quantity"


class Rejected(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.REJECTED] = OrderOutcomeKind.REJECTED
    reason: "RejectionReason"


class Pending(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.PENDING] = OrderOutcomeKind.PENDING
    placed_at: "Timestamp"


class OrderOutcome(RootModel[Filled | Rejected | Pending], frozen=True):
    root: Filled | Rejected | Pending = Field(discriminator="kind")
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

## Pattern 10: A Variant's Own Facts Are Variant-Carried Derivations

Behavior divides by where its meaning lives. A fact a variant implies from its own fields is
the variant's meaning: a same-named derivation on each variant, each returning a constructed
declared object, with the envelope forwarding to the selected variant. No dispatch is written
because none is needed, and the type checker requires every variant to define the derivation,
which makes the set exhaustive by construction. (What a consumer does about a variant is the
consumer's meaning and is Pattern 18.)

```python
from functools import cached_property


class Card(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.CARD] = PaymentMethodKind.CARD
    last_four: "CardLastFour"
    expiry: "CardExpiry"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(0)


class BankAccount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.BANK_ACCOUNT] = PaymentMethodKind.BANK_ACCOUNT
    account_number: "AccountNumber"
    routing_number: "RoutingNumber"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(3)


class Wallet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PaymentMethodKind.WALLET] = PaymentMethodKind.WALLET
    wallet_id: "WalletId"

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return SettlementDays(0)


class PaymentMethod(RootModel[Card | BankAccount | Wallet], frozen=True):
    root: Card | BankAccount | Wallet = Field(discriminator="kind")

    @cached_property
    def settlement_days(self) -> "SettlementDays":
        return self.root.settlement_days
```

Each variant returns a constructed `SettlementDays`; the envelope forwards to the selected
variant. A card and a wallet clear the same day, a bank transfer takes three. Settlement is
the payment method's own fact, so it lives on the variant; no consumer should re-derive it
in a `match` arm.

## Pattern 11: Consistency Model Is The Single Live Node

Exactly one unfrozen model per context. It holds the clients, receives live input, constructs
the domain fact from it, and emits the derived result after proof. It never branches on a
value: the analysis is a derivation, and its projection serializes whichever variant it is.

```python
from pydantic import BaseModel


class AnalysisConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bus: "EventBusClient"

    def analyze(self, hook_envelope: HookEnvelopeBoundary) -> None:
        file_context = FileContext(
            file_path=hook_envelope.event.tool_input.file_path,
            file_source_text=hook_envelope.event.tool_input.source_text,
        )
        self.bus.publish(file_context.analysis.model_dump_json())
```

The consistency model is exempt from immutability, not from typing rules. The source text is already
proven boundary truth from the payload, so there is no fetch; the analysis is a derivation on
`FileContext`, and the consistency model only constructs the fact and emits its projection.

### Chain Expansion: Verb-Body Shape

A mutation method's body is a chain of single legal operations whose order is the dependency
order of the constructions it performs, not an authored sequence. Each statement either
constructs a frozen fact from already-proven inputs, assigns a constructed value, reads a
derivation, or emits a projection. An effect is never emitted before the fact it projects is
constructed and proven.

```python
class ProcessingConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bus: "EventBusClient"
    store: "RecordStoreClient"

    def process(self, envelope: "IncomingEnvelopeBoundary") -> None:
        record = Record(
            record_id=envelope.record_id,
            payload=envelope.payload,
        )                                              # construct: proven fact
        enriched = EnrichedRecord(
            record=record,
            annotation=record.annotation,             # read derivation on proven fact
        )                                             # construct: depends on record
        self.store.save(enriched.model_dump_json())   # emit: only after proof
        self.bus.publish(enriched.summary.model_dump_json())  # emit: only after proof
```

When the method yields a stream of proven facts rather than emitting once, the body is an
`async def` returning `AsyncIterator[T]`, where each yielded value is a constructed proven
fact. The dependency order of constructions is preserved: a fact is yielded only after its
own construction and the constructions it depends on are complete.

```python
from collections.abc import AsyncIterator


class StreamingConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    source: "RecordSourceClient"
    bus: "EventBusClient"

    async def stream(
        self, request: "StreamRequestBoundary"
    ) -> AsyncIterator["EnrichedRecord"]:
        async for raw in self.source.fetch(request.cursor.root):
            record = Record(
                record_id=raw.record_id,
                payload=raw.payload,
            )                                          # construct: proven fact
            enriched = EnrichedRecord(
                record=record,
                annotation=record.annotation,         # read derivation on proven fact
            )                                         # construct: depends on record
            self.bus.publish(enriched.summary.model_dump_json())  # emit: after proof
            yield enriched                            # yield: constructed proven fact
```

The statement order in both forms is the dependency order of the constructions: `record`
before `enriched` because `enriched` composes `record`. That order falls out of the
construction graph and is never authored. A statement that could move earlier without
breaking construction is proof that the method holds two unrelated chains and should be
split.

## Pattern 12: Service Is Transport Binding Only

Service binds clients to consistency model. It owns no domain logic.

```python
class AnalysisService:
    def connect(self, bus: "EventBusClient") -> AnalysisConsistencyModel:
        return AnalysisConsistencyModel(bus=bus)
```

## Pattern 13: Route Is Ingress Membrane Only

Route constructs boundary truth, dispatches to consistency model, and projects response.

```python
def hook_route(raw_message: str, consistency_model: AnalysisConsistencyModel) -> str:
    envelope = HookEnvelopeBoundary.model_validate_json(raw_message)
    consistency_model.analyze(envelope)
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

`main.py` instantiates concrete clients, services, consistency model, and routes.

```python
def main() -> None:
    config = AnalysisConfig()  # Construct typed config proof once.
    bus = EventBusClient(config.bus_url.root)
    consistency_model = AnalysisService().connect(bus=bus)
    run_transport_loop(lambda raw: hook_route(raw, consistency_model))
```

No domain modeling and no domain decisions live here.

## Pattern 16: Facts Cross Process Boundaries by Projection and Re-proof

Established facts are projected to the wire and re-proven through a boundary model on the
far side.

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

## Pattern 18: Consumer Dispatch Is One Exhaustive Match Over The Narrowed Root

When what to do depends on which variant a union holds, that choice is the consumer's
meaning, and its home is the consumer: a single exhaustive `match` over the narrowed root,
proven total by the type checker. What stays on the variant is what the variant itself
implies (Pattern 10): the content of a notification is the outcome's own fact, a derivation,
read off the arm.

```python
from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field, RootModel


class OrderNotification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    recipient: "AccountId"
    headline: "NotificationHeadline"


class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.FILLED] = OrderOutcomeKind.FILLED
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
    kind: Literal[OrderOutcomeKind.REJECTED] = OrderOutcomeKind.REJECTED
    account_id: "AccountId"
    reason: "RejectionReason"

    @cached_property
    def notification(self) -> OrderNotification:
        return OrderNotification(
            recipient=self.account_id,
            headline=NotificationHeadline("order rejected"),
        )


class OrderOutcome(RootModel[Filled | Rejected], frozen=True):
    root: Filled | Rejected = Field(discriminator="kind")
```

First sort what actually varies. When only the *destination* varies, a static mapping
from variant identity to channel, that mapping is the variant's own fact (Pattern 10),
and the authority's rule applies with no exemption: "an effect whose channel varies
crosses as a projected fact and is re-selected by discriminated construction at the
consuming boundary." Each variant derives its subject; the consumer holds one client,
emits once, and no dispatch exists to write:

```python
class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.FILLED] = OrderOutcomeKind.FILLED
    account_id: "AccountId"
    fill_price: "Price"

    @cached_property
    def subject(self) -> "SubjectName":
        return SubjectName("orders.filled")
    # Rejected derives SubjectName("orders.rejected"); the envelope forwards both
    # `subject` and `notification` (Pattern 10), so the consumer reads them off the union.


class OrderConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bus: "EventBusClient"

    def settle(self, outcome: OrderOutcome) -> None:
        self.bus.publish(outcome.subject.root, outcome.notification.model_dump_json())
```

Whoever cares about rejections subscribes to `orders.rejected` and re-proves the fact by
discriminated construction at its own boundary. The destination travels as data, on a
transport that routes by data; two client fields for two destinations on one substrate is
the unfactored form, and a `match` whose arms differ only in which client they call is
that unfactoring made visible.

The `match` is the consumer's form when the *reactions* genuinely diverge in behavior:
different constructions, different state evolution per variant. Each arm is then a
sequence of the same legal operations every mutation method is held to, and the checker
proves the `match` total over the narrowed root, so a new variant fails the build until
every consumer handles it:

```python
    def reconcile(self, outcome: OrderOutcome) -> None:
        match outcome.root:
            case Filled() as filled:
                position = Position(account_id=filled.account_id, price=filled.fill_price)
                self.latest = position                       # state evolves only on a fill
                self.bus.publish(outcome.subject.root, position.model_dump_json())
            case Rejected():
                self.bus.publish(outcome.subject.root, outcome.notification.model_dump_json())
```

When the reacting context is a different process, the same rule already holds: the
variation crossed as a projected fact (Pattern 16), and the consuming context re-selects
the variant by discriminated construction at its own boundary, then writes its own
exhaustive `match` over reactions it owns.

## Pattern 19: Model Both Wire Shapes; Railroad The Reply

A foreign client that raises where it means no speaks a domain answer in refusal's
vocabulary. Both of the wire's shapes are known, so both are modeled, and the ordered
union routes by construction: the answering shape lifts its payload declaratively and
refuses the signal; the refusal falls through to the no-variant, which composes from
its pinned identity.

```python
class Carried(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    kind: Literal[GetReplyKind.CARRIED] = GetReplyKind.CARRIED
    data: "ObjectBytes"


class NotFound(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)
    kind: Literal[GetReplyKind.NOT_FOUND] = GetReplyKind.NOT_FOUND


GetReply = Annotated[Carried | NotFound, Field(union_mode="left_to_right")]


class GetReplyCrossing(RootModel[GetReply], frozen=True):
    pass
```

The verb owns the capture, three lines that make the raise a value and decide nothing;
an undeclared raise still propagates as the refusal it is:

```python
    async def get(self, name: ObjectName) -> GetReply:
        try:
            raw: object = await self.store.get(name.root)
        except ObjectNotFoundError as signal:
            raw = signal
        return GetReplyCrossing.model_validate(raw).root
```

### Anti-pattern: The Reply Parser

```python
def classify_reply(reply: object) -> GetReply:          # a parser beside the shapes
    if isinstance(reply, ObjectNotFoundError):          # routing the shapes already decide
        return NotFound()
    return Carried(data=reply.data or b"")              # and a coalesce forging a value
```

Every line restates work construction owns: the `isinstance` is the railroad's
selection, the arm is the crossing's construction, and the coalesce manufactures a
value nothing proved. Model the shapes; feed whatever arrived; construction routes.

## Forbidden Mirrors (Do Not Build These)

- Validator/normalizer/mapping pipeline that restates meaning across layers.
- A standalone enum or scattered string labels as a domain type, or branching on a vocabulary member (a uniform vocabulary is a `StrEnum`-backed scalar; members with payloads are a discriminated union).
- An untagged union selected by shape inference, or a kind field that does not pin one axis member (`kind: str`, `kind: PaymentMethodKind` bare).
- A second representation of the kind: a raw string beside the typed `kind` field, or the kind stored apart from the value it identifies.
- `if`/`elif` chains or `isinstance` ladders over union identity, dispatch re-implemented without an exhaustiveness proof.
- Booleans as decision outputs.
- Bare primitives in frozen domain models.
- Collections whose elements are bare primitives.
- Nested helper functions inside derivations.
- Hand-formatted strings or `.root` unwrapping inside a derivation, presentation that escapes the type; project a structured value instead.
- Domain model inheritance for field reuse.
- Foreign handles stored on boundary models.
- Second unfrozen model in one context.
- Route/service classes that compute domain meaning.
- Orchestrator/pipeline/step-runner sequencing work outside consistency model.
- Scattered `os.environ` reads or settings dicts outside config model.
- Versioned request-response contracts with generated clients between services.
- Emitting effects before constructing proof.
- A reply parser beside modeled shapes: a function, `match`, or `isinstance` deciding a foreign reply's case; the ordered union selects by construction (Pattern 19).
- A capture that converts: an except arm constructing the answer, defaulting, or catching broadly; the capture makes the raise a value, once, and nothing else.
- A `match` whose arms differ only in which client they call: a destination is data the variant derives (Pattern 18), never a code branch. The `match` is for reactions that diverge in behavior.
- A variant-carried effect *description* (a command object a "uniform" emitter interprets): that relocates the consumer's reaction into the domain type. The variant carries facts (its subject, its notification); the consumer owns what it does about them.

## Purity Check

A section in this document is valid only if all are true:

- It names one legal construct or edge from the closed set.
- Its example places meaning in declared shape, not procedural sequence.
- Constructed values are sufficient proof; no post-proof guard is needed.
- Branching is principled: a variant's own fact is a derivation read off the selected variant; a consumer's reaction is one exhaustive `match` over the narrowed root in the consumer; nothing branches via `if`/`elif` chains, `isinstance`, or a boolean.
- Output leaves only as a projection of a structured value; no derivation flattens fields into a string.
- Any crossing is boundary or projection, never mapper code.
