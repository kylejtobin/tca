# TCA Build Patterns

These patterns describe how construction computes, but more importantly they describe how to actually build in TCA. They are not a closed taxonomy. They are the moves an architect actually needs to reach for, in dependency order: name the domain vocabulary, let fields prove themselves at construction, own the foreign schema, absorb transport wrappers on that same boundary, hand live input to it, lift into domain truth, build richer semantic worlds, let other models read declared surfaces, derive intrinsic facts, route structurally, and finally render a terminal result from owned proof.

To keep the build path legible, the examples below all use the same world: a stock exchange feed entering a trading domain.

### Name The Domain Scalars First

First, own the domain values themselves before any larger model starts using them.

**Bad Procedural Pattern**

```python
class TradeRecord(BaseModel, frozen=True):
    trade_id: str
    symbol: str
    price: Decimal
    quantity: int
    venue: str
```

**Why it is bad:** The model has field names, but the values are still flat unowned primitives, so the domain is only half modeled.

**TCA Pattern**

```python
class Symbol(RootModel[str], frozen=True):
    root: str

class Price(RootModel[Decimal], frozen=True):
    root: Decimal

class Quantity(RootModel[int], frozen=True):
    root: int

class DomainTrade(BaseModel, frozen=True, from_attributes=True):
    symbol: Symbol
    price: Price
    quantity: Quantity
```

This is correct because the domain vocabulary exists as owned scalar types before larger models start composing with it, and the first composed model closes the contrast pair completely. The same scalar move is what later legitimizes `VenueName`, `Spread`, `BasketName`, and the closed vocabulary `HaltReason`.

### Let Fields Declare Their Own Constraints

Once the domain fields exist, let their declarations carry as much proof as possible before you reach for procedure.

**Bad Procedural Pattern**

```python
class TradePayloadNormalizer:
    def normalize(self, raw_trade: dict[str, object]) -> dict[str, object]:
        normalized_trade: dict[str, object] = {}

        symbol = str(raw_trade["symbol"]).strip().upper()
        if not symbol:
            raise ValueError("symbol is required")
        normalized_trade["symbol"] = symbol

        price = Decimal(str(raw_trade["price"]))
        if price <= 0:
            raise ValueError("price must be positive")
        normalized_trade["price"] = price

        quantity = int(raw_trade["quantity"])
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        normalized_trade["quantity"] = quantity

        return normalized_trade
```

**Why it is bad:** Field-level proof has escaped into a procedural normalizer layer, so every new field becomes more parser code, more staging dicts, and more hand-written cleanup before the model gets to own its own boundary.

**TCA Pattern**

```python
class Symbol(RootModel[str], frozen=True):
    root: str = Field(min_length=1, pattern=r"^[A-Z]+$")

class Price(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0)

class Quantity(RootModel[int], frozen=True):
    root: int = Field(gt=0)

class DomainTrade(BaseModel, frozen=True, from_attributes=True):
    symbol: Symbol
    price: Price
    quantity: Quantity
```

This is correct because the constraints now live directly on the fields that own them, and Pydantic enforces them at construction without forcing the program to grow a separate normalizer service. Reach for validators later only when the proof cannot be expressed declaratively on the field itself.

### Mirror The Foreign Schema

Next, own the foreign payload shape declaratively at the boundary instead of translating it procedurally.

**Bad Procedural Pattern**

```python
class NasdaqTradeAdapter:
    def translate_trade_message(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        symbol = str(payload["sym"]).strip().upper()
        price = Decimal(str(payload["px"]))
        quantity = int(payload["qty"])

        translated_payload: dict[str, object] = {}
        translated_payload["symbol"] = symbol
        translated_payload["price"] = price
        translated_payload["quantity"] = quantity
        return translated_payload
```

**Why it is bad:** The foreign field translation is now trapped in a procedural adapter layer that rebuilds an unowned payload shape by hand.

**TCA Pattern**

```python
class NasdaqTradeWire(BaseModel, frozen=True, populate_by_name=True):
    symbol: Symbol = Field(alias="sym")
    price: Price = Field(alias="px")
    quantity: Quantity = Field(alias="qty")

# Same move, different exchange schema.
class NyseTradeWire(BaseModel, frozen=True, populate_by_name=True):
    symbol: Symbol = Field(alias="ticker")
    price: Price = Field(alias="last")
    quantity: Quantity = Field(alias="size")
```

This is correct because the seam models foreign truth faithfully while the rest of the program keeps speaking owned domain language. This is still foreign ownership, not domain truth yet.

### Normalize The Payload

After mirroring the foreign schema, absorb any outer transport wrapper on that same boundary model.

**Bad Procedural Pattern**

```python
class NasdaqFeedRouter:
    def route_trade(self, message: dict[str, object]) -> None:
        payload = message["payload"]
        self._trade_service.handle_trade(payload)

    def route_correction(self, message: dict[str, object]) -> None:
        payload = message["payload"]
        self._correction_service.handle_trade_correction(payload)
```

**Why it is bad:** The wrapper-removal logic now leaks into procedural handlers, so the seam stops being terminal and the outer transport shape keeps spreading.

**TCA Pattern**

```python
class NasdaqTradeWire(BaseModel, frozen=True, populate_by_name=True):
    # Same boundary model as above, now grown to absorb the wrapper too.
    symbol: Symbol = Field(alias="sym")
    price: Price = Field(alias="px")
    quantity: Quantity = Field(alias="qty")

    @model_validator(mode="before")
    @classmethod
    def unwrap_payload(cls, data: dict[str, object]) -> dict[str, object]:
        return data["payload"] if "payload" in data else data
```

This is correct because the same boundary model now absorbs the outer wrapper once instead of forcing procedural code to peel it open over and over.

### Capture Live Input

Once that boundary model is ready, keep the live seam thin: catch raw transport input and hand it off immediately.

**Bad Procedural Pattern**

```python
async for raw_message in nasdaq_socket:
    envelope = json.loads(raw_message)
    payload = envelope["payload"]

    if payload["event_type"] != "trade":
        continue

    trade = {
        "symbol": payload["sym"],
        "price": Decimal(payload["px"]),
        "quantity": int(payload["qty"]),
    }
    trade_store.publish(trade)
```

**Why it is bad:** The socket loop now owns parsing, wrapper access, field extraction, and business meaning instead of handing raw transport reality off immediately.

**TCA Pattern**

```python
async for raw_message in nasdaq_socket:
    trade = NasdaqTradeWire.model_validate_json(raw_message)
    yield trade
```

This is correct because the live edge does one job only: catch unstable input and hand it straight to the boundary model that already knows how to absorb the wrapper and own the payload. The socket loop is now just an intake edge.

### Lift Into Domain Truth

Once the foreign object is proven, cross directly into owned domain truth by construction.

**Bad Procedural Pattern**

```python
class TradeTranslator:
    def __init__(self, symbol_formatter) -> None:
        self._symbol_formatter = symbol_formatter

    def to_domain_trade(self, exchange_trade: NasdaqTradeWire) -> DomainTrade:
        translated_payload: dict[str, object] = {}
        translated_payload["symbol"] = self._symbol_formatter.format(
            exchange_trade.symbol
        )
        translated_payload["price"] = exchange_trade.price
        translated_payload["quantity"] = exchange_trade.quantity
        return DomainTrade(**translated_payload)
```

**Why it is bad:** The foreign-to-domain crossing is now trapped in a procedural translation step that manually rebuilds domain values one field at a time.

**TCA Pattern**

```python
exchange_trade = NasdaqTradeWire.model_validate_json(raw_message)
domain_trade = DomainTrade.model_validate(exchange_trade)
```

This is correct because the foreign object is already proven, and because the foreign model already exposes domain names, the crossing into owned semantics stays declarative and becomes another construction step instead of a mapper layer. This is the first point where owned domain truth begins.

### Compose Proven Models

Now construct a richer semantic world by owning already-proven models as fields.

**Bad Procedural Pattern**

```python
class SpreadService:
    def build_context(
        self,
        nasdaq_trade: DomainTrade,
        nyse_trade: DomainTrade,
        nasdaq_quote: VenueQuote,
        nyse_quote: VenueQuote,
    ) -> dict[str, object]:
        context_payload: dict[str, object] = {}
        context_payload["nasdaq_trade"] = nasdaq_trade
        context_payload["nyse_trade"] = nyse_trade
        context_payload["nasdaq_quote"] = nasdaq_quote
        context_payload["nyse_quote"] = nyse_quote
        context_payload["alert_threshold"] = Decimal("0.50")
        return context_payload
```

**Why it is bad:** The semantic world gets rebuilt procedurally on demand instead of existing as one owned proven object.

**TCA Pattern**

```python
class VenueQuote(BaseModel, frozen=True):
    venue: VenueName
    symbol: Symbol
    bid: Price
    ask: Price

class CrossVenueContext(BaseModel, frozen=True):
    nasdaq_trade: DomainTrade
    nyse_trade: DomainTrade
    nasdaq_quote: VenueQuote
    nyse_quote: VenueQuote
```

This is correct because the richer semantic world now exists as one proven object instead of a temporary coordination payload. `VenueQuote` is introduced here in its final shape, and `CrossVenueContext` is the first actual semantic world in the story.

### Read Another Model's Surface

Once a model exposes a declared surface, let downstream construction read it directly instead of rebuilding it.

**Bad Procedural Pattern**

```python
class QuoteSummaryDTO(BaseModel, frozen=True):
    venue: VenueName
    symbol: Symbol
    best_bid: Price
    best_ask: Price

class QuoteSummaryMapper:
    def from_quote(self, quote: VenueQuote) -> QuoteSummaryDTO:
        return QuoteSummaryDTO(
            venue=quote.venue,
            symbol=quote.symbol,
            best_bid=quote.bid,
            best_ask=quote.ask,
        )
```

**Why it is bad:** The mapping layer duplicates a surface that already exists, so the program pays procedural cost to restate what one model was already declaring.

**TCA Pattern**

```python
class QuoteSummary(BaseModel, frozen=True, from_attributes=True):
    venue: VenueName
    symbol: Symbol
    best_bid: Price = Field(alias="bid")
    best_ask: Price = Field(alias="ask")

summary = QuoteSummary.model_validate(quote)
```

This is correct because the next model reads the declared surface that already exists instead of forcing the program to rebuild it procedurally. This is borrowed truth, not newly derived truth.

### Derive On The Model

Once a model owns enough proven structure, extend that same model with a named intrinsic fact that belongs to it.

**Bad Procedural Pattern**

```python
class SpreadAlertService:
    def maybe_publish(self, context: CrossVenueContext) -> None:
        edge = context.nyse_quote.bid - context.nasdaq_quote.ask

        if edge > Decimal("0.50"):
            self._publisher.publish(
                {
                    "symbol": context.nasdaq_quote.symbol,
                    "edge": edge,
                }
            )
```

**Why it is bad:** The derivation is not owned at all. It is just inline arithmetic at the call site, so the program keeps rediscovering intrinsic truth instead of naming and owning it.

**TCA Pattern**

```python
class CrossVenueContext(BaseModel, frozen=True):
    nasdaq_trade: DomainTrade
    nyse_trade: DomainTrade
    nasdaq_quote: VenueQuote
    nyse_quote: VenueQuote

    @property
    def cross_venue_edge(self) -> Spread:
        return Spread(self.nyse_quote.bid - self.nasdaq_quote.ask)
```

This is correct because the same `CrossVenueContext` now owns the intrinsic fact that can be derived from the fields it already proved.

### Declare Cases Instead Of Branching

Once the domain world exists, let type selection replace branch-based control flow.

**Bad Procedural Pattern**

```python
class ExchangeEventRouter:
    def route(self, raw_event: dict[str, object]) -> None:
        if raw_event["event_type"] == "trade":
            event = {
                "event_type": "trade",
                "symbol": raw_event["symbol"],
                "price": raw_event["price"],
                "quantity": raw_event["quantity"],
            }
            self._trade_handler.handle(event)
        elif raw_event["event_type"] == "halt":
            event = {
                "event_type": "halt",
                "symbol": raw_event["symbol"],
                "reason": raw_event["reason"],
            }
            self._halt_handler.handle(event)
        else:
            event = {
                "event_type": "auction",
                "symbol": raw_event["symbol"],
                "auction_price": raw_event["auction_price"],
            }
            self._auction_handler.handle(event)
```

**Why it is bad:** The procedure is doing dispatch that structure already knows how to do, so the case logic lives in branch code instead of in the types that own the cases.

**TCA Pattern**

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

This is correct because the cases are declared once as types, and construction selects the right one structurally. Construction is now the switch statement.

### Unfold Composite Inputs

Some declared cases are complete immediately, while others continue construction because their own shape still contains more of the same world.

**Bad Procedural Pattern**

```python
class InstructionBuilder:
    def build(self, raw: dict[str, object]) -> object:
        if raw["kind"] == "basket":
            built_orders = []
            for child in raw["orders"]:
                built_orders.append(self.build(child))
            return {
                "kind": "basket",
                "name": raw["name"],
                "orders": built_orders,
            }

        return {
            "kind": "market",
            "symbol": raw["symbol"],
            "quantity": int(raw["quantity"]),
        }
```

**Why it is bad:** Traversal code is now deciding the program's shape procedurally instead of letting the selected variant declare whether construction stops or continues.

**TCA Pattern**

```python
class MarketOrder(BaseModel, frozen=True):
    kind: Literal["market"] = "market"
    symbol: Symbol
    quantity: Quantity

class BasketOrder(BaseModel, frozen=True):
    kind: Literal["basket"] = "basket"
    name: BasketName
    orders: tuple["TradeInstruction", ...]

TradeInstruction = Annotated[
    MarketOrder | BasketOrder,
    Field(discriminator="kind"),
]

class TradingSession(BaseModel, frozen=True):
    instructions: tuple[TradeInstruction, ...]
```

This is correct because the selected variant's shape determines whether construction is complete now or must continue into children. This is declared dispatch plus recursive continuation by shape.

### Let One Construction Trigger The Next

Once the seam and domain path are stable, introduce a dedicated root object whose job is to let one proven result trigger the next.

**Bad Procedural Pattern**

```python
class TicketWorkflowService:
    def __init__(self, parser, normalizer, translator, ticket_factory) -> None:
        self._parser = parser
        self._normalizer = normalizer
        self._translator = translator
        self._ticket_factory = ticket_factory

    def build_ticket(self, raw_message: str) -> TradeTicket:
        parsed_message = self._parser.parse(raw_message)
        normalized_payload = self._normalizer.normalize(parsed_message)
        domain_trade = self._translator.to_domain_trade(normalized_payload)
        return self._ticket_factory.create(domain_trade)
```

**Why it is bad:** The coordinator now owns the semantic path of the program, so construction becomes a script instead of a graph that extends itself through proven objects.

**TCA Pattern**

```python
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

This is correct because each proven result becomes the natural source for the next construction, and the path lives on the model instead of in a coordinator script. The new root type is justified here because the lesson is orchestration-by-construction.

### Render The Final Shape

Finally, let the terminal human-facing or machine-facing surface emerge from owned truth.

**Bad Procedural Pattern**

```python
class OpportunityPresenter:
    def render(self, context: CrossVenueContext) -> str:
        parts: list[str] = []
        parts.append(f"buy venue={context.nasdaq_quote.venue}")
        parts.append(f"buy ask={context.nasdaq_quote.ask}")
        parts.append(f"sell venue={context.nyse_quote.venue}")
        parts.append(f"sell bid={context.nyse_quote.bid}")
        parts.append(f"edge={context.nyse_quote.bid - context.nasdaq_quote.ask}")
        return " | ".join(parts)
```

**Why it is bad:** The output layer is rebuilding truth it does not own, so the final artifact is no longer emerging directly from the proof source.

**TCA Pattern**

```python
class SpreadOpportunity(BaseModel, frozen=True, from_attributes=True):
    buy_from: VenueQuote = Field(alias="nasdaq_quote")
    sell_to: VenueQuote = Field(alias="nyse_quote")
    edge: Spread = Field(alias="cross_venue_edge")

    @computed_field
    @cached_property
    def line(self) -> str:
        return (
            f"Buy on {self.buy_from.venue} at {self.buy_from.ask}; "
            f"sell on {self.sell_to.venue} at {self.sell_to.bid}; "
            f"edge={self.edge}"
        )

opportunity = SpreadOpportunity.model_validate(context)
```

This is correct because the terminal artifact now emerges directly from the semantic world already established above instead of being reconstructed in a presenter layer. The program is now emitting its final surface.
