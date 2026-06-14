# Construct Patterns

This document is the pattern source of truth: every construct's rules, required forms, and worked examples. All examples share one domain, venue fills, positions, and orders, and every example is correct to copy verbatim. Each construct's section is mirrored by its `tca-construct-*` skill card, identical text plus the card's row grammar and halt rule.

## Naming

Name every structure for the domain thing or domain fact it carries. Do not name a structure for a pipeline stage, a data direction, or a processing step, and do not give a domain structure a name that fits every program: not `Record`, `Item`, `Data`, `Payload`, `Result`, `Entry`, or `Info`, no `Handler`, `Manager`, `Processor`, `Incoming`, `Outgoing`, `Processed`, or `Enriched`, and no `Event` suffix. The naming test: the name is understandable without describing the data flow, and a domain expert recognizes the thing it names.

## Construction Rules

Construction replaces validation as a separate step: a value that fails construction does not exist as a domain value. Do not write a check after construction to prove the value again, do not move an unproven value forward, and do not store, pass, or branch on unmodeled data. Do not compute a domain fact in a free function when the fact is implied by a model's fields, and do not sequence domain work in a function, handler, processor, manager, pipeline, or orchestrator. The dependency graph between constructed values determines construction order.

## binding

### Definition

The class whose `connect` method binds transport clients to the consistency model. Its entire meaning is the binding it performs: it owns no domain type, holds no domain logic, and makes no domain decision.

### Required Form

```python
class PositionBinding:
    def connect(self, bus: BusClient, ledger: LedgerClient, opening: PositionState) -> PositionConsistencyModel:
        return PositionConsistencyModel(bus=bus, ledger=ledger, latest=opening)
```

### Sorting Rules

Domain state and domain transitions belong to the consistency model; the binding only constructs it. Client instantiation and configuration belong to the composition root; the binding receives constructed clients. Transport ingress belongs to the route; the binding handles no request.

### Replaced Forms

A repository is a fetch surface given a class name; consumers read facts the consistency model's transitions establish. A computing service is domain logic that escaped the consistency model. A manager is sequencing the construction graph already owns.

### Transport Setup

`connect` may perform transport setup whose signal has no domain meaning: connection, authentication, subscription, and the idempotent create-or-bind that binds the same client either way. If the domain reacts to a transport signal, the signal is modeled through the ordered union, never caught here.

### Allowed Patterns

- one class whose `connect` accepts constructed transport clients and any opening state, and returns the constructed consistency model
- connection, authentication, and subscription setup inside `connect`

### Forbidden

- a method that computes a domain fact
- a catch that converts a transport signal into a domain answer
- a domain type defined in the binding's file
- a repository, manager, or computing service

## collection

### Definition

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, for a sequence that is itself a domain thing with its own name, constraint, or derivation. A sequence with no meaning of its own is a `tuple[T, ...]` field on a model, not a collection.

### Required Form

```python
class FillList(RootModel[tuple[Fill, ...]], frozen=True):
    root: tuple[Fill, ...] = Field(min_length=1)


fills = FillList(tuple(Fill.model_validate(report) for report in venue_reports))
```

The collection constructs whole, one expression producing the tuple the `RootModel` proves.

### Sorting Rules

An element that is a bare primitive is an undeclared semantic scalar: build the scalar first. A sequence with no name, constraint, or derivation of its own is a plain `tuple[T, ...]` field on a value object or concept model. A fact the sequence implies as a whole is a derivation on the named collection.

### Replaced Forms

A `list`, `set`, or `dict` field is an unconstrained mutable container where a proven sequence belongs. A loop appending into a container is construction performed as procedure; the comprehension inside the construction call is the whole build.

### Association

A mapping keyed by a domain value is three structures, never a `dict` field: an entry model with declared key and value fields, a collection of entries, and a frozen query model holding the collection and the key, whose derivation returns a found-or-missing union. A repeated-key question is another query model with a derivation.

```python
class Quotation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    product: ProductId
    price: Price


class PriceBook(RootModel[tuple[Quotation, ...]], frozen=True):
    root: tuple[Quotation, ...]


class PriceQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    book: PriceBook
    product: ProductId

    @cached_property
    def answer(self) -> PriceFound | PriceMissing:
        return next(
            (PriceFound(quotation=q) for q in self.book.root if q.product == self.product),
            PriceMissing(product=self.product),
        )
```

### Allowed Patterns

- `field: tuple[T, ...]` on a value object or concept model, `T` a declared type
- `class Xs(RootModel[tuple[T, ...]], frozen=True)` with a `Field(...)` constraint when the sequence carries its own bound
- derivations on the named collection returning declared types
- the collection constructed whole in one expression
- an entry model, a collection of entries, and a query model as the shape of any association

### Forbidden

- a `list`, `set`, or `dict` field on a domain model
- a collection element typed as a bare primitive
- a loop appending domain values into a collection
- `KeyError` or a default value as domain miss behavior

## composition root

### Definition

The program entrypoint. It constructs config, instantiates concrete clients, passes them to bindings, constructs the consistency model, and registers or invokes routes. It holds no domain logic and defines no domain model.

### Required Form

```python
def main() -> None:
    config = PositionConfig()
    bus = BusClient(config.url.root, config.token.get_secret_value())
    ledger = LedgerClient(config.url.root, config.token.get_secret_value())
    model = PositionBinding().connect(bus=bus, ledger=ledger, opening=Flat())
    run_ingress(lambda raw: fill_route(raw, model))
```

A long-running program's root is the same shape made async; signal handling and graceful teardown are wiring and live here, nowhere else.

```python
async def main() -> None:
    config = PositionConfig()
    bus = BusClient(config.url.root, config.token.get_secret_value())
    ledger = LedgerClient(config.url.root, config.token.get_secret_value())
    model = PositionBinding().connect(bus=bus, ledger=ledger, opening=Flat())
    shutdown = asyncio.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(sig, shutdown.set)
    await shutdown.wait()
    await bus.drain()
```

`.root` and `get_secret_value()` are legal here because the composition root is a client binding site, one of the two places the program meets the wire.

### Sorting Rules

Domain construction belongs to the consistency model and its verbs; the root only wires. Client binding belongs to the binding; the root instantiates clients and hands them over. Request handling belongs to routes; the root registers or invokes them. Environment reads belong to config; the root constructs it once.

### Replaced Forms

A runner, pipeline, orchestrator, or step list is a hand-kept copy of an order the construction graph already determines: a value cannot construct before its inputs, so evaluation order is the sequence. A function that calls everything in order means the terminal object has not been named; name it and construct it.

### Allowed Patterns

- one `main()` that constructs config, instantiates clients, binds through bindings, constructs the consistency model, and registers or invokes routes
- the async form with signal handlers, a shutdown event, and client drain
- `.root` and `get_secret_value()` at client instantiation
- input read and output emitted only at the edges of `main`

### Forbidden

- an orchestrator, pipeline, or step-runner sequencing domain work
- a domain computation in the entrypoint
- a domain model defined in the entrypoint's file
- an environment read outside config

## concept model

### Definition

A frozen `BaseModel` composing declared types into one full domain thing or domain fact. The product type whose sum-type sibling is the union: the type is the concept, each field a relation to another concept.

### Required Form

```python
class Fill(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    order_id: OrderId
    account_id: AccountId
    fill_price: Price
    filled_quantity: Quantity


class Position(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PositionKind.OPEN] = PositionKind.OPEN
    prior: PositionState
    fill: Fill

    @cached_property
    def exposure(self) -> Exposure:
        return Exposure(self.prior.exposure.root + self.fill.exposure.root)
```

Every field is a declared type: never a bare primitive, never `T | None`, and never a value derivable from other fields. A concept model that pins a `kind` is a union variant.

### Sorting Rules

A small identity-less composition of scalars, equal by value, is a value object. A single value is a semantic scalar. A choice among concept models is a union, and a concept model pinning one axis member is that union's variant. Another system's shape is a foreign model; this program's API shape is a contract model; mutable state is the consistency model.

### Replaced Forms

A dataclass, `NamedTuple`, `TypedDict`, or dict-shaped value carries the shape without the proof. A validator that asserts a relation is a check performed inside construction; the relation reparameterizes. A base class created only to share fields is a second structure for one meaning; the shared field is already shared as the leaf both models compose.

### Construction Discipline

A composite constructs whole in one call: constituents are proven by coercion inside it, never pre-constructed one at a time beside it. Keywords express the lift from a foreign result's attributes; `from_attributes` lifts a whole object; `model_validate_json` lifts serialized data. A dict assembled by hand and fed to `model_validate` where keywords express it is a mapper in miniature. A coalesce on the way in (`x or default`) manufactures a value nothing proved. A check after construction un-proves the value it guards.

### Absence

"May be missing" is never a field. Absence that means something is a union variant named for what absence means, or separate models when absence changes the state shape. When constructing from foreign data, an omitted key resolves to a default that states what omission means, or a variant when omission means a different fact; bare `None` never crosses into the domain.

```python
class PositionKind(StrEnum):
    OPEN = "open"
    FLAT = "flat"


class Flat(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PositionKind.FLAT] = PositionKind.FLAT

    @property
    def exposure(self) -> Exposure:
        return Exposure(Decimal("0"))


class QuoteSubscription(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    product: ProductId
    depth: BookDepth = BookDepth(50)
```

`Flat` is the account with no position, and it carries no position fields: absence changed the state shape, so absence is its own variant. `QuoteSubscription.depth` defaults to the venue default, so an omitted foreign key never enters as `None`.

### Allowed Patterns

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`
- every field a declared type: a scalar, a value object, a collection element form, a concept model, or a union
- `from_attributes=True` in the config when the model lifts from objects
- a defaulted field whose default states what omission means
- derivations implying the model's facts
- the kind pin `kind: Literal[Axis.MEMBER] = Axis.MEMBER` when the row declares a variant

### Forbidden

- a bare primitive field
- a `T | None` field
- a stored field derivable from the others
- a validator that computes, normalizes, or asserts
- a `Present` or `Absent` wrapper
- subclassing a domain model for field reuse
- a constituent constructed in a separate statement beside its composite
- an unfrozen model that is not the consistency model

## config

### Definition

A frozen `BaseSettings` model, the only structure that reads environment values. Every field is a declared scalar or secret type, and it is constructed once by the composition root and injected.

### Required Form

```python
class VenueUrl(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class PositionConfig(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="forbid", env_prefix="VENUE_")
    url: VenueUrl
    token: SecretStr
```

### Sorting Rules

A configured value used in the domain is carried as its declared scalar, never re-read from the environment. Client instantiation from config values belongs to the composition root. A value that is domain state rather than environment fact belongs on the consistency model.

### Replaced Forms

An `os.environ` read scatters the environment through the program; config proves it once at startup. A settings dict carries unproven values; a config singleton hides the read behind import order.

### Secrets

A secret is never a bare `str`: `SecretStr` keeps it out of every dump, repr, and log. `get_secret_value()` is called exactly once, at client instantiation in the composition root.

`BaseSettings` lives in the `pydantic-settings` package; if it is not installed, that is a gap to report, not a reason to read the environment directly.

### Allowed Patterns

- one frozen `BaseSettings` model per program with `SettingsConfigDict(frozen=True, extra="forbid")`
- an `env_prefix` naming the program's environment namespace
- every field a declared scalar or `SecretStr`
- constructed once in the composition root and injected

### Forbidden

- an `os.environ` read anywhere
- a settings dict or config singleton
- a secret typed as bare `str`
- `get_secret_value()` outside the composition root

## consistency model

### Definition

The single unfrozen `BaseModel` of a context, the one node where live clients and mutable state converge. Every state it holds is a proven fact, and state evolution is a field re-pointing to a newer proven value.

### Required Form

```python
PositionState = Annotated[Position | Flat, Field(discriminator="kind")]


class PositionConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bus: BusClient
    ledger: LedgerClient
    latest: PositionState

    def book(self, report: VenueFill) -> None:
        self.latest = Position(prior=self.latest, fill=report)
        self.bus.publish(self.latest)
        self.ledger.append(self.latest)
```

`PositionState` is the state union: `Position` and `Flat` are the concept models declared in their own sections, each carrying the same-named `exposure` derivation, so exposure reads off `latest` with no branch. Clients are fields, state fields are declared types, and every method is a verb. `arbitrary_types_allowed` is legal on this class and nowhere else.

### Sorting Rules

A second unfrozen model means the context is two contexts: stop and report it. Client binding belongs to the binding; the consistency model receives constructed clients as fields. A fact the state implies is a derivation on the state's model, not a method here. A frozen domain composite is a concept model.

### Replaced Forms

A manager or engine is domain logic with a technology name and no proof obligation. A module-level client is the live edge escaped from the one node that may hold it. A second unfrozen model is a second convergence point for state, which is two contexts fused into one.

### State Evolution

State evolution is reassignment of proofs, never mutation of their contents: construct the newer proven fact and re-point the field to it. The consistency model never holds an unproven value, not even for one statement. Every non-client field is a declared type; no bare primitives, no `T | None`, no `bool` gates. Selection never happens here: construction selected the variant, the checker narrows it, and what differs by variant is read from the union value.

### Allowed Patterns

- one unfrozen `BaseModel` per context with `arbitrary_types_allowed=True`, clients as fields
- every non-client field a declared type holding a proven value
- state evolution by re-pointing a field to a newly constructed fact
- verbs as the only methods

### Forbidden

- a second unfrozen model in one context
- a module-level client
- `match`, `if`/`elif`, or `isinstance` anywhere in the class
- a hand-assembled dict where a constructed type belongs
- an unproven or unmodeled value held in any field
- `arbitrary_types_allowed` on any other class

## contract model

### Definition

A frozen `BaseModel` of this program's own API request or reply, composed of declared types in this program's vocabulary. No alias to another system's key appears on it.

### Required Form

```python
class OrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    product: ProductId
    side: OrderSide
    quantity: Quantity
    price: Price


class OrderReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    order_id: OrderId
```

A request that does not conform fails construction at the surface; nothing behind the route sees it. The reply leaves whole: the route serializes the contract model itself.

### Sorting Rules

Composition direction separates the edge's two models: the contract model is ours, built of our types and names, projecting outward; the foreign model is theirs, named for their thing, its aliases holding their keys, lifting inward. A composite that is a domain fact rather than a surface shape is a concept model.

### Replaced Forms

One model serving as both our API shape and another system's shape fuses our surface with their shape; build one of each. A hand-built response dict is an unproven shape leaving the program; the reply is the contract model itself, serialized at the route.

### Allowed Patterns

- a frozen `BaseModel`, `extra="forbid"`, every field a declared type from this context or its peers
- a request contract a route constructs from raw transport data
- a reply contract constructed from proven facts and serialized whole in the route
- `@computed_field` derivations when a derived fact is part of the published shape

### Forbidden

- an alias to another system's key
- a foreign shape modeled as a contract
- `include`, `exclude`, or `by_alias` on the reply's serialization; a different wire shape is its own contract model
- a contract field whose type is not one of this program's declared types

## derivation

### Definition

A fact that is a pure function of a frozen value's already-proven fields, written on the model that owns them. It takes only `self`, its body is one returned expression, and it returns a declared type, model, or union. The same fields yield the same fact every time, because the value they compose never changes.

### Required Form

```python
class Exposure(RootModel[Decimal], frozen=True):
    root: Decimal = Field(ge=0)


class Fill(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    order_id: OrderId
    account_id: AccountId
    fill_price: Price
    filled_quantity: Quantity

    @cached_property
    def exposure(self) -> Exposure:
        return Exposure(self.fill_price.root * self.filled_quantity.root)
```

Because a derivation is a pure function of frozen fields, `@property` and `@cached_property` return the same fact and differ only in substrate: `@property` recomputes it on each read, `@cached_property` computes it once and remembers. The choice is cost, never meaning: `@property` for a cheap fact (a constant, a single lookup), `@cached_property` when the fact is expensive, recursive, or read repeatedly, where the cache is what lets a recursion settle in one pass and a materialization happen once. `@computed_field` above `@cached_property` is the only one of the three that changes meaning: it writes the derived fact into every serialization, so it is used exactly when the fact is part of a contract shape.

Construction recurses, so a derivation over a recursive model reaches arbitrary depth with no loop: the comprehension inside the one returned expression is the whole traversal.

```python
class Portfolio(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    exposure: Exposure
    children: tuple["Portfolio", ...] = ()

    @cached_property
    def total_exposure(self) -> Exposure:
        return Exposure(self.exposure.root + sum(c.total_exposure.root for c in self.children))
```

The contract-shape form:

```python
class Quote(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    bid: Price
    ask: Price

    @computed_field
    @cached_property
    def mid(self) -> Price:
        return Price((self.bid.root + self.ask.root) / 2)
```

### Sorting Rules

A fact that differs by which union variant holds is each variant's own same-named derivation, read from the union value. A question with an input is a query model, not a parameterized method. A state transition belongs to a verb on the consistency model; a derivation stores nothing and changes nothing. The line between a derivation and a field is structural: if a pure function of the model's own fields yields the value, it is a derivation and is never also stored, since a stored copy of a derivable fact is one meaning in two structures. A value that no function of the fields can yield, because it depends on the clock, a foreign read, a random source, or input the model does not keep, is not a derivation at all; it is a field, computed once where the value is born and passed into construction. On `Quote`, `mid` is a derivation, a function of `bid` and `ask`; the moment the quote was observed would be a field, because no function of `bid` and `ask` yields it.

### Replaced Forms

A fact you are about to compute in a function, a step, or a loop is a derivation that has not found its model yet: name it on the value whose fields imply it, and the procedure is gone, the work done by the construction the derivation returns. A standalone function computing from a model's fields is that derivation escaped from its owner. A stored derivable field is a second copy of a fact kept in agreement by hand. A `bool`-returning check is an undeclared union: a staleness check returns `Fresh | Stale`, each variant carrying its own facts.

### The Computation

A derivation is a function from the model's proven fields to the fact it returns, which is a proof that those fields imply that fact. The computation is the proof term, and it is determined meaning, not the builder's to invent: that exposure is price times quantity and not over it is a domain decision, made once where the model lives, never at build time. The operations that compose the proof are a closed algebra, the way the constructs are a closed set: arithmetic over the fields, a fold over a collection (the catamorphism that carries the one recursion), selection of an element by its key, and a lookup of a closed value through a total case table. A computation that needs an operation the algebra does not hold is a reported gap, never free code. The only part of a derivation the builder decides is cost, not meaning: whether the fact is recomputed on each read or memoized once.

### Query Model

A question with an input is a composite fact: a frozen `BaseModel` holding the input and the value being queried, with the answer as a derivation on it, returning a constructed choice.

```python
class PriceQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    book: PriceBook
    product: ProductId

    @cached_property
    def answer(self) -> PriceFound | PriceMissing:
        return next(
            (PriceFound(quotation=q) for q in self.book.root if q.product == self.product),
            PriceMissing(product=self.product),
        )
```

### Allowed Patterns

- a derivation taking only `self`, body one returned expression, returning a declared type, model, or union
- `@property` to recompute a cheap fact, `@cached_property` to compute a costly, recursive, or repeatedly-read fact once, both pure over the fields
- `@computed_field` above `@cached_property` when the fact belongs to a contract's serialized shape
- a comprehension or generator expression inside the one returned expression
- the same-named derivation on every variant of a union, read from the union value
- a frozen query model holding the input and the queried value, its derivation returning the answer

### Forbidden

- a free function computing from a model's fields; a helper or utils entry
- a parameterized method on a frozen value
- a derivable field stored on a model
- a body that reads anything but the model's own fields (the clock, a client, a random source); a `@cached_property` freezes its first-read value and a `@property` returns a different value each call, so neither is a fact of the fields
- a derivation returning bare `bool`, `str`, or `int`
- a ternary, `and`, `or`, `match`, or private helper call inside the body
- serialization inside a derivation

## foreign model

### Definition

A frozen `BaseModel` of another system's data shape, named for the other system's thing: its aliases hold that system's keys, and its fields are this program's domain meanings. It exists only when the foreign shape differs from the domain shape, and it carries every field the program uses from the foreign data.

### Required Form

```python
class VenueFill(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    order_id: OrderId = Field(alias="ordId")
    account_id: AccountId = Field(alias="acct")
    fill_price: Price = Field(alias="px")
    filled_quantity: Quantity = Field(alias="qty")


class VenueFillMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    fill: VenueFill = Field(validation_alias="data")


class VenueStreamMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    fill: VenueFill = Field(validation_alias=AliasPath("data", "payload"))
```

The declarative inventory: `Field(alias=...)` for a key rename, `validation_alias` for data wrapped at one key, `AliasPath` for data under nested wrapper keys, nested foreign models for nested structure, `from_attributes=True` for objects, `model_validate_json` for serialized data.

### Sorting Rules

If the foreign shape already matches the domain model, construct the domain model directly; the constructor does the entire job and no foreign model exists. This program's own API shape is a contract model, never a foreign model. Foreign data that carries no identity and is expected to fail constructs through the ordered union. A live client is held by the consistency model, never on a foreign model.

### Replaced Forms

A mapper, adapter, translator, DTO, or field-copying function restates work the constructor owns: the foreign model lifts whole in one call. A `json.loads` dict carries unproven data through the program. A before-validator that indexes, renames, routes, or computes is an alias, a path, or a nested model not yet written.

### Whole Lift

The crossing takes the foreign data whole: `model_validate` on an arrived object, `model_validate_json` on arrived bytes, or keyword construction lifting a result's attributes. The foreign model carries every field the program uses, and nothing reads the foreign object after a model has been constructed from it. An omitted foreign key resolves at lifting: a default naming what omission means, or a union variant when omission means a different fact; bare `None` never crosses in. No coalesce mints data the wire did not carry.

A foreign object graph (an `ast` walk, a DOM traversal, a reflection sweep) is not a foreign model crossing: a shape that needs a walk is a meaning no construct carries, and its one legal output is a reported gap.

### Allowed Patterns

- a frozen `BaseModel`, `extra="forbid"`, every field a declared type, named for the foreign thing
- `Field(alias=...)` for every rename, the aliases holding the foreign keys
- a nested foreign model for every nested foreign structure
- `validation_alias` and `AliasPath` for transport wrappers, the wrapper modeled, never indexed past
- `from_attributes=True` for objects; `model_validate_json` for serialized data
- an omitted key resolved by a named default or a variant

### Forbidden

- a mapper, adapter, translator, DTO, or field-copying function
- a `json.loads` result carried as a dict
- a before-validator that indexes, renames, routes, or computes; any `mode="after"` validator
- a model named for a pipeline stage instead of the foreign thing
- an attribute read on a foreign object after its model was constructed
- a live client or handle retained as a field

## ordered union

### Definition

`Annotated[A | B, Field(union_mode="left_to_right")]` over variants in attempt order, for foreign data that carries no identity and is expected sometimes to fail or to say no. The stronger construction is attempted first, the failure variant is last and composes from the input itself, and construction selects the case.

### Required Form

```python
class TapeText(RootModel[str], frozen=True):
    """The venue tape's frame text as received. Unconstrained on purpose: an unparseable frame is any text."""

    root: str


class FrameKind(StrEnum):
    TICK = "tick"
    UNPARSEABLE = "unparseable"


class Tick(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[FrameKind.TICK] = FrameKind.TICK
    price: Price
    quantity: Quantity


class Unparseable(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[FrameKind.UNPARSEABLE] = FrameKind.UNPARSEABLE
    raw: TapeText

    @model_validator(mode="before")
    @classmethod
    def _wrap(cls, data: object) -> object:
        return {"raw": data}


Frame = Annotated[Json[Tick] | Unparseable, Field(union_mode="left_to_right")]

FrameConstructor = TypeAdapter(Frame)


class TapeEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    frame: Frame
```

Fed bytes that parse, `Json` decodes and `Tick` constructs; fed garbage, `Json` refuses and `Unparseable` composes from the input itself. As a field, `frame: Frame` admits garbage as a declared value.

A raising client, modeled the same way:

```python
class LedgerKind(StrEnum):
    BOOKED = "booked"
    UNBOOKED = "unbooked"


class Booked(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    kind: Literal[LedgerKind.BOOKED] = LedgerKind.BOOKED
    exposure: Exposure


class Unbooked(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    kind: Literal[LedgerKind.UNBOOKED] = LedgerKind.UNBOOKED


LedgerReply = Annotated[Booked | Unbooked, Field(union_mode="left_to_right")]

LedgerReplyConstructor = TypeAdapter(LedgerReply)
```

Fed the reply object, `Booked` constructs from its attributes. Fed the exception, `Booked` refuses, and `Unbooked` constructs from its pinned kind.

### Sorting Rules

One question routes every failure: did the domain say no, or did the proof fail? A construction refusal proves nothing, is never modeled, and propagates; catching `ValidationError` manufactures the unproven value. A domain no is a value: this construct. An omission that means a fact is the absence doctrine at a foreign lift, not a failure. A transport-setup signal nothing in the domain reacts to belongs to the binding. Identity-carrying data constructs through the union's discriminator, never by attempt order.

### Replaced Forms

A `try`/`except` producing a default, flag, or partial object manufactures the unproven value construction refused to make. A reply parser inspecting a foreign reply to choose a case restates the selection construction performs. A coalesce (`x or default`) manufactures a value nothing proved.

### The Wrap

The one `mode="before"` validator the architecture admits: a single wrapping line on the failure variant that places the bare input under its field name, legal only with a recorded substrate run showing the declarative inventory refuses the shape. One return, constant keys, the input as every value. A marker handed back where it means a fact constructs an identity-only variant the same way.

### The Constructor

The constant beside the alias is the alias's declared constructor, the substrate's `TypeAdapter`, named for the alias it constructs. It defines no structure and decides nothing. As a field on a foreign model, the alias needs no constant: `frame: Frame` admits garbage as a declared value, the `TapeEntry` form above.

### The Capture

Python raises must be captured before construction can receive them. The capture lives in a verb: one call assigned, each declared exception assigned to the same variable, then ordered-union construction from that variable. The capture does not choose a variant, does not construct in an `except` arm, and an undeclared raise propagates as the refusal it is.

### Allowed Patterns

- the `Annotated` alias with `union_mode="left_to_right"`, variants in attempt order, failure last
- the failure variant composing from the input itself through the proven one-line wrap
- `Json[...]` as the stronger construction when the input is serialized
- the `TypeAdapter` constant named for the alias
- the alias as a field on a foreign model
- the capture in a verb feeding the constructor

### Forbidden

- `except ValidationError`, anywhere
- a `try`/`except` producing a default, flag, partial object, or domain variant
- a broad `except` or a second statement in an `except` arm
- `x or default`
- a reply parser: a function, `match`, or `isinstance` deciding a reply's case
- a `RootModel` class created to construct the alias

## route

### Definition

The function at transport ingress. It constructs a contract model or foreign model from raw transport data, unwraps transport wrapper structure, dispatches the value the verb consumes, and serializes the reply. It defines no types and computes no domain fact.

### Required Form

```python
def fill_route(raw: str, model: PositionConsistencyModel) -> str:
    message = VenueFillMessage.model_validate_json(raw)
    model.book(message.fill)
    return OrderReceipt(order_id=message.fill.order_id).model_dump_json()
```

The route dispatches `message.fill`, the innermost value the verb consumes, never the transport wrapper. The reply is one of the two legal serialization sites.

### Sorting Rules

The shape the route constructs belongs to whoever owns it: a contract model when this program publishes the API, a foreign model when the caller's shape is another system's. Domain work belongs to the verb the route dispatches to. Wiring and registration belong to the composition root.

### Replaced Forms

A handler that parses fields by hand restates the construction the model performs in one call. A handler that computes or decides is domain meaning escaped to the edge; the route turns transport into a construction and back, nothing more.

### Allowed Patterns

- one function per ingress: one construction from raw transport data, one dispatch of the innermost value, one serialized reply
- contract and foreign models imported from the files that declare them
- `model_dump_json` on the reply contract, the route being a legal serialization site

### Forbidden

- parsing transport fields by hand
- transforming or computing domain data
- branching on a domain case
- dispatching a transport wrapper into a verb
- defining any type in the route's file

## semantic scalar

### Definition

A frozen `RootModel[P]` over one primitive or one closed value space, carrying a `Field(...)` constraint or a docstring stating why the open range is the domain fact. The atomic domain value: it references no domain type.

### Required Form

```python
class Price(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0, decimal_places=8)


class Quantity(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0)


class OrderId(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderSide(RootModel[Side], frozen=True):
    root: Side

    @property
    def opposite(self) -> "OrderSide":
        return OrderSide({Side.BUY: Side.SELL, Side.SELL: Side.BUY}[self.root])


class OrderNote(RootModel[str], frozen=True):
    """A trader's free-text note on an order. Unconstrained on purpose: any text, including empty, is a legal note."""

    root: str
```

The allowed primitives are `str`, `int`, `float`, `Decimal`, `bool`, `bytes`, and `date`. A closed vocabulary wraps a `StrEnum` or `Literal` value space; the `StrEnum` is the value space, the role `gt=0` plays. A scalar derivation on a closed value space selects by data lookup, never by a ternary or a branch.

### Sorting Rules

One axis, every member the same kind of thing: a scalar. A member needing a field or behavior a sibling lacks: two axes, a union. A value composed of other values: a value object or concept model.

### Replaced Forms

A bare primitive standing for a domain value holds its meaning in a variable name no downstream reader receives. A vocabulary scattered as string literals is unnamed and unproven. An unconstrained `RootModel[str]` with no docstring and no genuine name is a structure with no meaning.

### Root Discipline

A scalar constructs where its composite is proven: a raw value passed where the scalar field stands constructs it inside the composite's own call. Pass the declared value onward. `.root` is read in exactly two settings: inside a derivation's one returned expression, where the bare value immediately feeds the construction of the declared type the derivation returns, and where the program meets the wire, at a client binding or a route reply. A bare `.root` value is consumed by the construction or the client call that reads it, never assigned, stored, or passed onward.

### Allowed Patterns

- `class X(RootModel[P], frozen=True)` over one allowed primitive with a `Field(...)` constraint stating the domain's bound
- `class X(RootModel[E], frozen=True)` over a `StrEnum` or `Literal` value space
- an unconstrained scalar whose docstring states why the open range is the domain fact
- a derivation on the scalar returning a declared type, selecting by data lookup on a closed space

### Forbidden

- a bare primitive used as a domain value
- string literals used as a closed vocabulary
- a standalone enum used as a field type
- an unconstrained `RootModel` without a stated openness
- a ternary or branch inside a scalar derivation
- a bare `.root` value assigned, stored, or passed onward; `.root` is read only inside a derivation's returned construction, at a client binding, or at a route reply

## union

### Definition

A closed set of two or more frozen variants over one domain axis, the axis a `StrEnum`, each variant pinning exactly one member with a defaulted `kind: Literal[Axis.MEMBER]` field. The structural form of a choice: a decision with consequences is a union of result variants, and identity-carrying data constructs it through the discriminator on its alias.

### Required Form

```python
class OrderOutcomeKind(StrEnum):
    FILLED = "filled"
    REJECTED = "rejected"


class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.FILLED] = OrderOutcomeKind.FILLED
    fill_price: Price
    filled_quantity: Quantity

    @property
    def headline(self) -> Headline:
        return Headline("order filled")


class Rejected(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.REJECTED] = OrderOutcomeKind.REJECTED
    reason: RejectionReason

    @property
    def headline(self) -> Headline:
        return Headline("order rejected")


OrderOutcome = Annotated[Filled | Rejected, Field(discriminator="kind")]
```

The defaulted pin puts the identity in every serialization of the value. A fact that differs by variant is each variant's own same-named derivation, read from the union value: a consumer reads `outcome.headline`, and the static checker requires every variant to define `headline`.

Variants with identical payloads differ in nothing but identity, so identity is a field or it is nowhere:

```python
class HaltKind(StrEnum):
    HALTED = "halted"
    RESUMED = "resumed"


class Halted(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[HaltKind.HALTED] = HaltKind.HALTED
    at: Timestamp


class Resumed(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[HaltKind.RESUMED] = HaltKind.RESUMED
    at: Timestamp
```

A yes-or-no decision with consequences is a two-variant union, never `bool`, because each outcome carries its own facts:

```python
class ReviewKind(StrEnum):
    APPROVED = "approved"
    REFUSED = "refused"


class Approved(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ReviewKind.APPROVED] = ReviewKind.APPROVED
    terms: ApprovalTerms


class Refused(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ReviewKind.REFUSED] = ReviewKind.REFUSED
    reason: RefusalReason
```

### Sorting Rules

A uniform one-axis vocabulary, every member the same kind of thing, is a semantic scalar over a `StrEnum`; the moment a member needs a field or behavior a sibling lacks, it is this construct. Foreign data that carries no identity and is expected to fail constructs through the ordered union, never by discriminator. A single variant on its own is a concept model pinning a kind.

### Replaced Forms

A `match`, `if`/`elif` chain, or `isinstance` ladder over variants is selection re-implemented after construction already selected; what differs by variant is the variant's derivation. A `bool` decision fuses both outcomes and drops both payloads. A raw-string kind or an unpinned `kind: Axis` admits every member on every variant and identifies nothing. A `RootModel` wrapped around a union is a class created only to provide `model_validate` the alias already provides.

### The Alias

The discriminator is declared on the union's own alias: `Annotated[A | B, Field(discriminator="kind")]`, one alias, one name, everywhere. In the graph the annotation is inert and the checker narrows through it. Where identity-carrying raw data constructs the union, the alias is the constructor: as a field on a foreign or contract model, or through one module-level `TypeAdapter` named for the alias when the data arrives with no surrounding modeled structure. Discriminated construction fails on the claimed variant's own fields, never across all variants.

```python
OrderOutcomeConstructor = TypeAdapter(OrderOutcome)

outcome = OrderOutcomeConstructor.validate_json(transport_bytes)
```

### Probes

Before building on a union, construct one variant and read the pin back:

```python
filled = Filled(fill_price=Price("101.50"), filled_quantity=Quantity("3"))
```

`filled.kind` is `OrderOutcomeKind.FILLED`, and `kind` appears in the serialized data. Before building on the alias, serialize a constructed variant and re-prove it: `OrderOutcomeConstructor.validate_json(filled.model_dump_json())` returns a `Filled`, because the identity was carried in the data. Never author a dict input object as a probe.

### Allowed Patterns

- one `StrEnum` axis declared beside the variants
- two or more frozen variants, each pinning exactly one member with `kind: Literal[Axis.MEMBER] = Axis.MEMBER`
- the alias `Annotated[A | B, Field(discriminator="kind")]` as the union's one rendered form
- the alias as a field's type, a derivation's return, or a verb parameter
- a same-named derivation on every variant for any fact that differs by variant
- one `TypeAdapter` named for the alias, only for bare arrivals

### Forbidden

- a raw-string kind or `kind: Axis` unpinned
- an untagged union selected by field shape
- `match`, `if`/`elif`, or `isinstance` over variants
- `bool` returned as a domain decision
- a `RootModel` class wrapped around a union
- a routing validator selecting a variant
- a hand-written dict input passed to discriminated construction

## value object

### Definition

A frozen `BaseModel` composing scalars into a small value with no identity, equal by value: a measurement, a description, an amount. The composition layer between the semantic scalar and the concept model.

### Required Form

```python
class Spread(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    best_bid: Price
    width: SpreadWidth

    @cached_property
    def best_ask(self) -> Price:
        return Price(self.best_bid.root + self.width.root)
```

### Sorting Rules

A single value is a semantic scalar. A full domain thing or fact, anything with domain identity or a kind pin, is a concept model. A value object never holds a client, never pins a kind, and two value objects with equal fields are the same value.

### Replaced Forms

A tuple or dict of primitives carries the parts without the proof or the name. A dataclass pair carries the shape without construction as proof. A validator asserting a relation between fields is a check performed inside construction; the relation is reparameterized instead.

### Reparameterization

A relation no single field constrains is part of the composite proof, never a guard after it: reparameterize so the relation collapses into a single-field constraint and a derivation. `Spread` holds `best_bid` and a non-negative `width` and derives `best_ask`, so an inverted spread has no representation. A reparameterization that seems to distort the model is the signal that the related fields are their own concept, not yet factored.

### Allowed Patterns

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`, fields scalars or value objects
- a cross-field relation reparameterized into one constrained field plus a derivation
- derivations implying the value's facts

### Forbidden

- a bare primitive field
- a `T | None` field
- a kind pin or any identity field
- a client or handle as a field
- a validator asserting a relation between fields
- a stored field derivable from the others

## verb

### Definition

A state-transition method on the consistency model. Its parameter is the innermost constructed value it consumes; its body contains at most one construction statement, with constituents constructing inside that call; it may capture a foreign reply before the construction, re-point a state field to the constructed fact, and emit the constructed fact through a client field.

### Required Form

```python
    def book(self, report: VenueFill) -> None:
        self.latest = Position(prior=self.latest, fill=report)
        self.bus.publish(self.latest)
        self.ledger.append(self.latest)
```

`Position.fill` is typed `Fill`, so the `Fill` constructs from the `VenueFill` inside the `Position` construction call. The state field is the constructed value's only name, and every emit passes the proven value itself; serialization happens at the client binding or the route reply, never here.

A yielding verb yields constructed facts:

```python
    async def watch(self, account: AccountId) -> AsyncIterator[Fill]:
        async for report in self.feed.subscribe(account):
            yield Fill.model_validate(report)
```

A capturing verb feeds the ordered union's constructor:

```python
    async def reconcile(self, account: AccountId) -> None:
        try:
            raw: object = await self.ledger.position(account)
        except PositionNotFoundError as signal:
            raw = signal
        self.recorded = LedgerReplyConstructor.validate_python(raw)
```

### Sorting Rules

A fact implied by already-proven fields is a derivation, not a verb. A method that only retrieves and returns is not a verb; consumers read facts that transitions establish. Construction of the request shape belongs to the route; the verb receives the innermost value, never a transport wrapper.

### Replaced Forms

A multi-step body staging constructions in sequence is the work stolen from a constructor: a constituent constructed in a separate statement before the composite that holds it restates what the composite's call proves. A fetch-and-return method is a repository surface given a verb's name. Serialization in the body is the transport's concern restated in the domain.

### Verb Body

The body contains at most one construction statement; constituent values construct inside that one call. It may also: capture a foreign reply before the construction (one call assigned, each declared exception assigned to the same variable), assign the constructed fact to a state field, and emit the constructed fact through a client field. An effect is never emitted before the fact is constructed. A verb that constructs nothing, emits nothing, and yields nothing declares no transition.

### Allowed Patterns

- `-> None` transition: at most one construction, a state-field assignment, emits of the proven fact
- the capture before the construction, exactly the three-line form, feeding the ordered union's constructor
- a yielding verb constructing and yielding one fact per arrival
- a returning verb whose return is read from the fact its body constructs

### Forbidden

- more than one construction statement in a body
- a constituent constructed in a separate statement before its composite
- `model_dump`, `model_dump_json`, or `.root` in the body
- a parameter holding a transport wrapper
- a method that only retrieves and returns
- `match`, `if`/`elif`, or `isinstance` in the body
- a hand-assembled dict where a constructed type belongs
- a stub body: `raise NotImplementedError`, bare `...`, or `pass`

## Substrate Claims

A claim about Pydantic construction behavior requires a substrate run, a claim about gate coverage requires a gate run, and a claim about basedpyright behavior requires a basedpyright run. Do not add doctrine from analogy, idiom, or common Python practice.
