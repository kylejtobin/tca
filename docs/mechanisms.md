# Core Mechanisms

These are not the whole TCA pattern language. They are the deep reusable mechanisms underneath many of the visible moves you see in the README: mirroring foreign schemas, reading another model's surface, declaring cases instead of branching, unfolding composite inputs, and letting one construction trigger the next.

Each mechanism replaces a whole family of procedural code.

| Mechanism | Pydantic feature | What it replaces |
|:---|:---|:---|
| **Wiring** | `from_attributes`, aliases | Adapter classes, DTO converters, mapping layers |
| **Dispatch** | Discriminated unions, enum-owned classification | `if/elif` chains, `match/case` blocks |
| **Orchestration** | `@cached_property` + `model_validate` | Service-layer coordination code |

---

## Why Mechanisms Matter

A single model proves one thing. Mechanisms are what scale construction from one proof to a graph of proofs. They explain:

- how one model can read another model's declared surface
- how a known set of cases can route into the right variant
- how a proven object can naturally trigger the next proven object

Without these mechanisms, TCA proves individual objects. With them, TCA composes proofs into programs.

To keep the teaching legible, the examples below all stay in one world: stock exchange data entering a trading domain.

---

## Wiring: Read Another Model's Surface

When a model declares `from_attributes=True`, it constructs by reading attributes from another object by name. Stored fields count. Properties count too. Field names are the wiring.

```python
class VenueQuote(BaseModel, frozen=True):
    venue: VenueName
    symbol: Symbol
    bid: Price
    ask: Price

    @property
    def mid(self) -> Price:
        return Price((self.bid + self.ask) / 2)

class QuoteSummary(BaseModel, frozen=True, from_attributes=True):
    venue: VenueName
    symbol: Symbol
    mid: Price
```

`QuoteSummary.model_validate(venue_quote)` reads `venue`, `symbol`, and `mid` from the `VenueQuote` surface. No mapper function. No intermediate dict. No DTO conversion pass.

This is why wiring matters: it replaces the reflex to copy data from one shape into another procedurally. In TCA, if one model is already exposing the surface another model needs, the next model should read that surface directly.

Aliases extend the same idea across boundaries. A foreign model can accept external names while still exposing owned names internally. A downstream domain model can then keep speaking domain language.

---

## Dispatch: Declare Cases Instead Of Branching

Instead of branching on raw data to decide which type to construct, declare a variant for each case. Each variant carries a `Literal` tag. Pydantic reads the tag and routes to the correct variant automatically. The variant's fields ARE the result.

```python
class TradeEvent(BaseModel, frozen=True):
    event_type: Literal["trade"] = "trade"
    symbol: Symbol
    price: Price
    quantity: Quantity

class HaltEvent(BaseModel, frozen=True):
    event_type: Literal["halt"] = "halt"
    symbol: Symbol
    reason: HaltReason

class AuctionEvent(BaseModel, frozen=True):
    event_type: Literal["auction"] = "auction"
    symbol: Symbol
    auction_price: Price

ExchangeEvent = Annotated[
    TradeEvent | HaltEvent | AuctionEvent,
    Field(discriminator="event_type"),
]

event = TypeAdapter(ExchangeEvent).validate_python(raw_event)
```

A discriminated union dispatches into a type whose fields already contain the answer. A `match` statement dispatches and then asks you to write the meaning for each branch by hand. Here, selecting `HaltEvent` already means "this is a halt and it carries a halt reason." Construction replaces branch code.

Dispatch also includes enum-owned classification. When the answer is a member of a closed vocabulary, the enum should own the classification logic.

```python
class SpreadSignal(StrEnum):
    NORMAL = "normal"
    WIDE = "wide"

    @classmethod
    def from_spread(cls, spread: Spread) -> SpreadSignal:
        if spread >= Spread("0.50"):
            return cls.WIDE
        return cls.NORMAL
```

The important point is ownership. Consumers should not replicate classification logic in scattered helpers. They should ask the union or the enum that owns the cases.

---

## Orchestration: Let One Construction Trigger The Next

The first two mechanisms describe how values flow between models and how the correct case is selected. The third mechanism describes how proven objects drive further proof.

A `@cached_property` that calls `model_validate` is a lazy construction trigger. The projection fires on first access, constructs a new proven object, and caches it permanently on the frozen model.

```python
class DomainTrade(BaseModel, frozen=True, from_attributes=True):
    symbol: Symbol
    price: Price
    quantity: Quantity

class TradeTicket(BaseModel, frozen=True, from_attributes=True):
    symbol: Symbol
    price: Price
    quantity: Quantity

class CapturedNasdaqTrade(BaseModel, frozen=True):
    raw_message: str

    @cached_property
    def foreign_trade(self) -> NasdaqTradeWire:
        return NasdaqTradeWire.model_validate_json(self.raw_message)

    @cached_property
    def domain_trade(self) -> DomainTrade:
        return DomainTrade.model_validate(self.foreign_trade)

    @cached_property
    def ticket(self) -> TradeTicket:
        return TradeTicket.model_validate(self.domain_trade)
```

`captured.ticket` forces `domain_trade`, which forces `foreign_trade`. Nothing fires until demanded. Once it fires, each stage is a proven object and the result is cached on the frozen root.

Orchestration is what makes TCA a programming paradigm instead of a validation library. It replaces the service-layer reflex to coordinate stages procedurally. In a well-shaped TCA program, that coordination collapses into projections on the model that owns the semantic path.

---

## How Mechanisms Produce Broader Patterns

The broader construction patterns are what architects usually feel first. The mechanisms are what make those patterns work.

- **Mirror the foreign schema** uses aliases and before-normalization at the boundary.
- **Read another model's surface** is wiring directly.
- **Declare cases instead of branching** is dispatch directly.
- **Unfold composite inputs** is dispatch plus shape-driven recursion.
- **Let one construction trigger the next** is orchestration directly.
- **Render the final shape** is usually a projection emerging from an already-proven world.

This is why the broader pattern language is larger than three, while the deep mechanism set can still remain small.

---

## How The Mechanisms Compose

Real TCA programs do not use the mechanisms in isolation. They interlock.

1. A foreign message is normalized into a mirror model with owned names.
2. A downstream model wires from that surface through name agreement.
3. If the input contains known cases, dispatch selects the right variant.
4. If the proven result naturally leads to another proof, orchestration triggers the next construction.

The construction graph has two kinds of edges that correspond to this composition:

**Field edges** are eager. A field annotation creates a dependency that must be satisfied at construction time. If the child fails, the parent cannot exist.

**Derivation edges** are lazy. A `@cached_property` that calls `model_validate` creates a dependency that fires only when demanded.

Inheritance is not a graph edge in this operational sense. Inheritance defines related machine families that share construction behavior. Composition and derivation are what build the proof graph.

The full proof graph is the union of eager field edges and lazy derivation edges. Wiring, dispatch, and orchestration are the primary ways that graph executes.
