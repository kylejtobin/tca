# Type Construction Architecture

## Technical Specification v0.3

**Runtime:** Python 3.12+
**Construction Language:** Pydantic v2

---

## 1. Core Thesis

Pydantic is a programming language. Python is its runtime.

This is not analogy. A Pydantic model is not a passive container that holds data in named slots — Python dataclasses do that. A Pydantic model is an active machine with an execution pipeline that fires every time data enters it. That pipeline — translation, interception, coercion, invariant proving, derivation — is real computation. One call to `model_validate` executes the program. If the object exists at the end, the program succeeded and the result is proven. If construction fails, no object exists. There is no third outcome.

Type Construction Architecture is the discipline of writing programs this way. Define the types. Wire their construction pipelines. Let `model_validate` execute. The types are not a model of the program. They are the program. Everything else — services, routes, CLI entry points — is plumbing that hands raw data to a construction machine and receives a proven object.

---

## 2. The Construction Machine

Every Pydantic model is a machine with five wired layers. You do not call these layers in sequence. You wire logic into them by declaring fields, aliases, validators, and computed fields. When `model_validate(raw)` fires, the machine executes all layers automatically:

**Translation.** `mode="before"` validators and field-level aliases reshape raw input before field construction begins. Foreign structure becomes domain structure. `Field(alias="user_id")` maps external vocabulary to domain vocabulary at the field declaration. A `mode="before"` validator flattens nested payloads or restructures mismatched shapes. Translation is the machine's ingestion preprocessor — as native to the model as its fields, not an escape hatch for messy data.

```python
class Trade(BaseModel, frozen=True):
    counterparty: CounterpartyID = Field(alias="cp_id")
    notional: Decimal = Field(alias="notional_usd", ge=0)
    trade_date: date = Field(alias="trd_dt")
    maturity: date = Field(alias="mat_dt")

    @model_validator(mode="before")
    @classmethod
    def flatten_wire_format(cls, data: dict) -> dict:
        if "trade_details" in data:
            data.update(data.pop("trade_details"))
        return data
```

**Interception.** `mode="wrap"` validators receive the raw input and the inner constructor as a callable. They control whether and how construction proceeds — the only layer with that power. A wrap validator can inspect the input, decide if construction should happen at all, reshape the input, and call the inner constructor exactly once. This is how abstract base types seal themselves so only concrete variants construct, and how machines reshape input when a `mode="before"` validator would cause infinite recursion by re-triggering itself.

```python
class EventBase(BaseModel, frozen=True):
    timestamp: datetime

    @model_validator(mode="wrap")
    @classmethod
    def _seal(cls, data: object, handler: Callable[..., EventBase]) -> EventBase:
        result = handler(data)
        if type(result) is EventBase:
            raise TypeError("Construct a concrete event variant, not EventBase")
        return result
```

`handler(data)` fires the full construction pipeline. The wrap validator inspects the result: if the concrete type is `EventBase` itself, construction fails. Subclasses like `UserCreated(EventBase)` pass through. The wrap validator decides what may exist. In the building block classifier, `ModelTree` uses a wrap validator to reshape a `BaseModel` class into a dict of classified fields — a `mode="before"` validator would recurse infinitely because returning a `ModelTree` instance re-triggers the validator. Wrap avoids this because the handler is called exactly once.

**Coercion.** Every field's type annotation is a construction instruction. Pydantic reads the incoming data and constructs each field value through the type's own pipeline. A raw string becomes a `CounterpartyID`. A nested dict becomes a `RiskProfile`. When `from_attributes=True` is set, Pydantic reads attributes from the input object by name — properties included — so one model's projection surface feeds another model's construction. When a field is a discriminated union, Pydantic reads the tag and routes to the correct variant automatically. Nested models fire their own machines recursively. This is where the two fundamental mechanisms (Section 3) execute. Coercion is the heart of the construction machine — where 90% of the work happens. If construction isn't working, the fix is almost always a missing intermediary model, a smarter alias, or a discriminated union — not a validator.

**Integrity.** `mode="after"` validators and `field_validator` prove that the constructed fields, individually and in combination, satisfy the machine's invariants. These are proof obligations: conditions that must hold for the object to exist. A `DateRange` whose `start >= end` does not "fail validation." It fails to construct. The machine will not produce it.

```python
class DateRange(BaseModel, frozen=True):
    start: date
    end: date

    @model_validator(mode="after")
    def start_precedes_end(self) -> Self:
        if self.start >= self.end:
            raise ValueError("start must precede end")
        return self
```

**Projection.** Derived values are the machine's knowledge about itself — what it can determine from what it already holds. If calling code ever derives something from a machine's fields, that derivation is a wiring defect: it belongs on the machine's projection surface. Projection has three forms:

`@computed_field` with `@cached_property` — derived, cached, and serialized. These appear in `model_dump()` and JSON output. Use when the projection is part of the model's public contract.

```python
@computed_field
@cached_property
def days_to_maturity(self) -> int:
    return (self.maturity - self.trade_date).days
```

Bare `@cached_property` — derived and cached, but not serialized. Use for expensive projections like indexes that shouldn't appear in JSON output.

Bare `@property` — trivial delegation, not cached. This is how self-classifying wrappers expose derived attributes that downstream models read via `from_attributes`. A `TypeAnnotation` wrapping a raw Python annotation exposes `.kind` as a property. Pydantic reads `.kind` during coercion, routes a discriminated union, and the variant's `Literal` fields settle the classification. The property is the bridge between a wrapped value and the construction machinery that consumes it.

```python
class TypeAnnotation(RootModel[object], frozen=True):
    @property
    def kind(self) -> AnnotationKind:
        o = get_origin(self.root)
        if o is types.UnionType: return AnnotationKind.OPTIONAL
        if o is tuple: return AnnotationKind.TUPLE
        if isinstance(self.root, TypeAliasType): return AnnotationKind.ALIAS
        return AnnotationKind.DIRECT
```

One `model_validate` call ignites the entire pipeline. A proven, self-aware object emerges, or a construction failure is raised. The calling code does not participate in construction. It ignites the machine with raw input and receives a proven result.

### Construction as Proof

The machine's existence IS the proof of its validity. If a `Trade` object exists, you know: every field has the correct type, the notional is non-negative, the maturity follows the trade date, and all nested types constructed successfully. There is no separate validation step. There is no "invalid but present" state. There is nothing behind the curtain to be out of sync with.

This is Alexis King's "Parse, Don't Validate" realized as a programming paradigm. Construction is parsing. The unconstructed data is not a value in the system.

---

## 3. Two Fundamental Mechanisms

TCA rests on two Pydantic mechanisms that are equally foundational. Each eliminates an entire category of procedural code.

### 3.1 `from_attributes=True` — Ingestion Without Extraction

When a model declares `from_attributes=True`, it constructs by reading attributes from another object by name. Field names are the wiring. Properties count — Pydantic reads them via `getattr`. No mapping code, no adapter functions, no intermediate dictionaries. One object's surface becomes another object's input.

```python
class RawSensor(BaseModel, frozen=True):
    temperature_celsius: float
    pressure_kpa: float

    @property
    def temperature_fahrenheit(self) -> float:
        return self.temperature_celsius * 9/5 + 32

class DisplayReading(BaseModel, frozen=True, from_attributes=True):
    temperature_fahrenheit: float   # Reads the property from RawSensor
    pressure_kpa: float             # Reads the stored field
```

`DisplayReading.model_validate(raw_sensor)` constructs by reading attributes from the `RawSensor` instance. The property is read by `getattr`, the same as stored fields. This enables construction chaining: one model's projection surface becomes another model's input ports. The chain fires automatically because name agreement IS the wiring.

This mechanism is how data gets INTO machines. External data arrives with external names and external structure. `from_attributes` lets a machine read what it needs from any object whose attributes match its field names. Combined with aliases, this subsumes the entire category of "data mapping" code that proliferates in conventional architectures — adapter classes, DTO converters, serialization layers. In TCA, the field declaration IS the mapping.

### 3.2 Discriminated Unions — Dispatch Without Branching

Instead of branching on raw data to decide which type to construct, declare a variant for each case. Each variant carries a `Literal` tag. Pydantic reads the tag and routes to the correct variant automatically. The variant's fields ARE the result — no computation needed after dispatch.

```python
class Shipped(BaseModel, frozen=True):
    kind: Literal["shipped"] = "shipped"
    tracking: TrackingNumber
    carrier: CarrierName

class Cancelled(BaseModel, frozen=True):
    kind: Literal["cancelled"] = "cancelled"
    reason: CancellationReason
    refund: RefundAmount

OrderStatus = Annotated[
    Shipped | Cancelled,
    Field(discriminator="kind")
]

status = TypeAdapter(OrderStatus).validate_python(raw)
```

The runtime reads `kind`, selects the variant, constructs it. No `if raw["kind"] == "shipped":` exists anywhere. Calling code that inspects a raw discriminator to select a type is bypassing the construction machine.

Discriminated unions are how machines DISPATCH without procedural code. Where conventional programs use `if/elif` chains or `match/case` blocks to handle different cases, TCA declares a variant for each case and lets the construction pipeline route. The consumer of the union receives a proven variant and pattern-matches on the type, not on a raw field value.

These two mechanisms — `from_attributes` for ingestion and discriminated unions for dispatch — eliminate the two largest sources of procedural boilerplate in data-intensive programs. Together, they account for the majority of code that TCA removes.

---

## 4. The Construction Graph

Types compose by appearing in each other's field annotations. A parent type that declares a child type as a field requires the child to construct before the parent can exist. The child's machine fires first. If it fails, the parent fails. Proof cascades upward.

The construction graph is the directed acyclic graph formed by following field annotations from roots to leaves:

```
AppEnvironment
├── DatabaseConnection
├── FeatureFlags
├── CustomerIndex
│   └── Customer
│       ├── CustomerId
│       ├── RiskProfile
│       │   ├── RiskTier
│       │   ├── BehavioralSignal
│       │   └── Confidence
│       └── Segment

AnalyzeRetention
├── Customer (shared node)
├── AnalysisContext
└── AnalysisDepth

RetentionAnalysis
├── CustomerId (shared node)
├── RiskTier (shared node)
├── Intervention
├── ConfidenceFactor
└── AnalysisMetadata
```

Every type that is not a root exists because some root's field annotation references it, directly or transitively. Shared nodes appear under multiple roots — `Customer` appears under both `AppEnvironment` and `AnalyzeRetention` — but the positional meaning differs. Under `AppEnvironment`, a `Customer` is "who this system serves." Under `AnalyzeRetention`, a `Customer` is "whose retention is being analyzed." The field path from root to leaf is a sentence in the domain's language.

Roots are computable. Collect all `BaseModel` subclasses in a codebase, subtract every type that appears in another type's field annotations, and the remainder are the roots. This works in both directions: forward in greenfield development (name the roots, define their fields, everything cascades), and backward in existing code (compute roots, follow annotations, discover the construction graph).

---

## 5. The Program Triad

If construction is proof, then ask: what needs to be proven in any program that takes typed input and produces typed output within a typed context?

Three things. Always three things.

**That the preconditions hold.** The program can only act if its context is valid — connections live, configuration resolved, reference data indexed. This is a proof obligation. Construction discharges it. The root that discharges it is the **Environment**: the type whose fields name everything the program knows before it acts. An Environment is stable. Its fields describe what IS.

```python
class AppEnvironment(BaseModel):
    """If this constructs, the app can start."""
    database: DatabaseConnection
    feature_flags: FeatureFlags
    customer_index: CustomerIndex
```

**That the request is expressible.** The program can only act on requests its vocabulary can represent. A retention analysis request for a customer that doesn't parse into a `Customer`, with an analysis depth that isn't a valid `AnalysisDepth`, isn't a request the system can process. Construction discharges it. The root that discharges it is the **Action**: the type whose fields name what the program is being asked to do. An Action is volatile. Its fields describe what ARRIVES. Each instance is unique.

```python
class AnalyzeRetention(BaseModel):
    customer: Customer
    context: AnalysisContext
    depth: AnalysisDepth
```

**That the output is complete and consistent.** The program's result must satisfy its own invariants — all required fields present, cross-field constraints holding, derived values coherent. Construction discharges it. The root that discharges it is the **Result**: the type whose fields name what the program produced. A Result is derived. Its fields describe what WAS PRODUCED.

```python
class RetentionAnalysis(BaseModel):
    customer_id: CustomerId
    risk_tier: RiskTier
    interventions: list[Intervention]
    confidence_factors: list[ConfidenceFactor]
    metadata: AnalysisMetadata
```

These are three roots because they are three distinct proof obligations, and TCA says proof is construction, and construction requires a root. The triad is a corollary of the core thesis, not an addition to it. The service that connects Environment + Action → Result is plumbing. The types are the program.

---

## 6. Worked Example: A Building Block Classifier

The following program classifies every field on any Pydantic `BaseModel` into a structural building block — what role that type plays in a Pydantic program (enum, newtype, record, collection, scalar, etc.). It does this with zero domain knowledge. It works on any model, anywhere.

It is a pure TCA program. No LLM. No external services. One `model_validate` at the root cascades the entire classification. It demonstrates every mechanism described in this specification.

### The Cascade

```python
tree = ModelTree.model_validate(Team)
```

One call. The machine fires:

1. `ModelTree`'s wrap validator iterates `Team.model_fields.items()` — the one irreducible procedural seam in the entire cascade, because `dict` keys are not attributes and someone must pair them with values.
2. Each `(name, FieldInfo)` pair constructs a `FieldSlot` via its `mode="before"` validator, which bridges positional data (tuple) into named data (dict).
3. Pydantic coerces each `FieldSlot` into a `ClassifiedNode` via `from_attributes=True`. This is construction chaining — `FieldSlot`'s attributes become `ClassifiedNode`'s inputs through name agreement alone.
4. During that coercion, the `annotation` field (a `TypeAnnotation` wrapper) routes through a discriminated union (`AnnotationShape`) that classifies the annotation's structural form — direct, optional, tuple, or alias — without a single `if` statement.
5. The result: a tuple of `ClassifiedNode` instances, each carrying the field's name, its structural shape, and all classification flags.

### The Self-Classifying Wrapper

`TypeAnnotation` is a `RootModel[object]` that wraps a raw Python type annotation. Its properties expose derived attributes that downstream models read via `from_attributes`:

```python
class TypeAnnotation(RootModel[object], frozen=True):
    @property
    def kind(self) -> AnnotationKind:
        o = get_origin(self.root)
        if o is types.UnionType: return AnnotationKind.OPTIONAL
        if o is tuple: return AnnotationKind.TUPLE
        if isinstance(self.root, TypeAliasType): return AnnotationKind.ALIAS
        return AnnotationKind.DIRECT

    @property
    def resolved_type(self) -> object:
        return self.root
```

The object knows what it is. No external classifier inspects it. The `.kind` property fires during downstream construction when the discriminated union reads it to select a variant. Self-classification through properties, consumed by `from_attributes`, is a pattern that eliminates external classification functions entirely.

### Discriminated Union as the Answer

The `AnnotationShape` union is the core of the classifier. Each variant represents one structural form a Python annotation can take:

```python
class DirectAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.DIRECT] = AnnotationKind.DIRECT
    nullable: Literal[False] = False
    collection: Literal[False] = False

class OptionalAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.OPTIONAL] = AnnotationKind.OPTIONAL
    nullable: Literal[True] = True
    collection: Literal[False] = False

class TupleAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.TUPLE] = AnnotationKind.TUPLE
    nullable: Literal[False] = False
    collection: Literal[True] = True

AnnotationShape = Annotated[
    DirectAnnotation | OptionalAnnotation | TupleAnnotation | AliasAnnotation,
    Field(discriminator="kind"),
]
```

The `Literal[True]` and `Literal[False]` constants are the key insight. `nullable` and `collection` are not computed — they are constants baked into the variant's type. Selecting `OptionalAnnotation` IS the determination that `nullable=True`. The dispatch IS the answer. No one reads the variant and then computes a flag. The flag was settled the moment Pydantic routed to the variant.

This is what distinguishes a discriminated union from a `match/case` block. A match block dispatches and then you write the logic for each case. A discriminated union dispatches INTO a type whose fields already contain the answer. Construction replaces computation.

### Construction Chaining Through `from_attributes`

The classifier chains three models: `FieldSlot` → `FieldEntry` → `ClassifiedNode`. Each reads from the previous via `from_attributes`:

```python
class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    field_name: str
    shape: AnnotationShape = Field(alias="annotation")

    @property
    def resolved_type(self) -> object:
        return self.shape.resolved_type

    @property
    def nullable(self) -> bool:
        return self.shape.nullable

class ClassifiedNode(FieldEntry, frozen=True, from_attributes=True):
    ...
```

`FieldEntry` declares `shape` with `alias="annotation"`, so it reads `FieldSlot.annotation` (a `TypeAnnotation`). Pydantic constructs the `AnnotationShape` DU from the `TypeAnnotation`'s properties via `from_attributes`. Then `FieldEntry` exposes properties (`resolved_type`, `nullable`, `collection`) that flatten the nested shape, so `ClassifiedNode` sees a flat attribute surface.

No intermediate dictionaries are built. No extraction functions run. No adapter code exists. The models read from each other through name agreement and property delegation. The type tree wires itself.

### The Irreducible Minimum

The entire cascade has one procedural seam: the wrap validator on `ModelTree` that iterates `model_fields.items()` and constructs `FieldSlot` instances from the `(key, value)` tuples. This is irreducible because Python's `dict` exposes keys as positional data in tuples, not as attributes on values. Someone must bridge that boundary. Everything else in the cascade — coercion, DU routing, construction chaining, property delegation — is pure construction.

Identifying the irreducible procedural minimum is a TCA discipline. In any program, some boundaries cannot be crossed with pure construction. Those boundaries get one small validator. Everything else is wired into the type tree.

---

## 7. Architectural Principles

**Shapes first.** Define the types before writing any procedural code. The types ARE the specification. If you cannot express the domain as types, you do not yet understand the domain. Development proceeds: domain types, then vocabularies (enums), then hardened constraints (validators), then plumbing (services, routes). Everything interesting lives in the types. Everything else is thin.

**Shape over procedure.** A well-shaped model with the right field names, types, and aliases does most of the work. Pydantic's default coercion, `from_attributes` reading, and discriminated union routing handle the rest. If you are reaching for a validator or helper function, ask first: can a better shape solve it? An intermediate model, a smarter alias, or a discriminated union almost always can. Validators are the last resort — the irreducible minimum where pure shape cannot bridge a boundary. Most models need none.

**Domain types are the program.** The domain directory — types, enums, validators, computed fields — is the program. Service layers wire plumbing. API layers expose projections. Neither contains domain logic. If domain logic lives outside the types, it is in the wrong place.

**Construction is proof.** Never validate after the fact. Never check a field "just in case." If the object exists, it is valid. If you find yourself writing defensive checks against a constructed model, you have a construction deficiency, not a validation gap. Strengthen the machine's wiring so the guarantee holds by construction.

**Name precisely.** Field names are the interface between domain knowledge and computation. Use domain vocabulary, not programmer vocabulary: `churn_risk_tier`, not `risk_level`. Disambiguate with docstrings: if two terms could be confused, the docstring resolves it. Enum members are a closed vocabulary, and each member carries meaning. Treat renames as you would changing a function's logic, because that is what they are.

**Compose through construction.** Types compose by appearing in each other's field annotations. A parent requires its children to construct first. Proof cascades upward automatically. Do not compose through inheritance for domain types — inheritance expresses "is-a" relationships; field annotations express "contains-and-requires" relationships. Domain models are almost always the latter.

**Derivation belongs on the machine.** If calling code computes something from a machine's fields, that computation is a wiring defect. It belongs on the machine's projection surface as a `@computed_field`. The machine owns its derived knowledge. External code consumes projections. Calling code that iterates a machine's collection to look something up, or that combines two of a machine's fields to produce a third value, is doing the machine's work outside the machine.

**Progressively harden.** Start with contracts as field names and docstrings. Observe where soft compliance is insufficient. Promote those specific contracts to structural guarantees through validators. The construction pipeline grows by observation, not by speculation. Do not over-constrain prematurely.

**Minimize translation layers.** Every layer between domain knowledge and executable code is a source of information loss. In TCA, the domain expert names the fields, the docstrings are the specification, the construction pipeline is the logic, and construction is validation. The number of translation steps between "what the domain means" and "what the code does" is the primary metric of architectural quality. TCA drives it toward one.

---

## 8. Anti-Patterns

**Types at the exit.** The program operates in untyped space — raw dicts, string concatenation, ad hoc transformations — and types appear only at the output boundary as a retroactive check. This inverts the architecture. Types should be present at every layer, constraining computation from the start.

**God models.** A single model with forty fields that represents an entire entity across all contexts. A type that means everything means nothing. Break god models into focused types that each represent one coherent domain concept in one context.

**Stringly-typed fields.** Using `str` where a domain type should exist. Every unconstrained string field is an open invitation for arbitrary values. Replace with enums for closed vocabularies, constrained types for bounded values, pattern-validated strings for structured formats.

**Validation after construction.** Writing `assert`, `isinstance`, or conditional checks against a constructed model's fields. If these checks can fail, the construction pipeline is incomplete — add the constraint to the model. If they cannot fail, the checks are redundant — remove them. Either way, they should not exist.

**Procedure outside the machine.** Computing derived values from a machine's fields in calling code. Building lookup indexes over a machine's collections externally. Reformatting a machine's data for display. All of these are projections that belong on the machine's surface.

**Manual dispatch.** Branching on a raw discriminator value to decide which type to construct. This is the procedural implementation of what a discriminated union does structurally. Let the construction pipeline dispatch.

---

## 9. Relationship to Existing Work

TCA draws on and extends several traditions in programming language theory and software architecture.

**Parse, Don't Validate** (Alexis King, 2019): TCA is a direct realization of this principle. Construction is parsing. If it constructs, it's valid. There is no unvalidated representation. The unconstructed data is not a value in the system. TCA extends the principle from a design heuristic into a full programming paradigm with a concrete construction language.

**Domain-Driven Design** (Eric Evans, 2003): TCA shares DDD's emphasis on ubiquitous language, bounded contexts, and making the domain model central. TCA diverges in that the domain model is not a representation that application code operates on — the domain model IS the code. There is no application layer that "uses" the domain. The types, wired with construction pipelines, are the execution.

**Algebraic Data Types:** TCA's structural foundation is algebraic. Product types are `BaseModel` with multiple fields. Sum types are discriminated unions with `Literal` tags. Identity types are `NewType` and constrained primitives. These compose into construction graphs through field annotations. The algebraic structure provides the hard guarantees that bound all other computation.

**Type-Driven Development:** TCA shares the commitment to using types as the primary design tool. TCA extends it by treating types not merely as constraints on computation but as computation itself — the construction pipeline IS the program, not a safety net around it.

**Event Sourcing / CQRS:** The Program Triad (Environment, Action, Result) is structurally similar to State-Command-Event. TCA does not require event sourcing but is compatible with it. The distinction is that TCA's triad is derived from the proof obligations inherent in construction rather than from an architectural decision to separate reads from writes.

---

## 10. Compatibility with Semantic Index Types

TCA does not require an LLM consumer. The building block classifier demonstrates a complete TCA program with no LLM anywhere — a pure construction graph that classifies type annotations through structural dispatch and construction chaining. TCA is valuable whenever programs benefit from construction-as-proof, composition through types, and derivation owned by the objects that hold the data.

However, TCA is uniquely positioned to exploit what happens when the consumer of a type schema is a language model. Because TCA already preserves field names, docstrings, and enum members as first-class structural elements, and because the construction pipeline already proves results, adding an LLM consumer activates a semantic dimension without architectural change. The same types that structure the construction graph become instructions to the model. This phenomenon — semantic index types — is the subject of a companion paper.
