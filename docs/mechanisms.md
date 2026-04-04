# Three Mechanisms

Three construction mechanisms describe how types compose through the pipeline. Each replaces a whole family of procedural code.

| Mechanism | Pydantic feature | What it replaces |
|:---|:---|:---|
| **Wiring** | `from_attributes`, aliases | Adapter classes, DTO converters, mapping layers |
| **Dispatch** | Discriminated unions, smart enums | `if/elif` chains, `match/case` blocks |
| **Orchestration** | `@cached_property` + `model_validate` | Service-layer orchestration code |

---

## Why Mechanisms Matter

A single model proves one thing. Mechanisms are what scale construction from one model to a graph of models. They explain how data flows between machines, how the correct type is selected, and how proven objects drive further proof. Without them, TCA proves individual objects. With them, TCA composes proofs into programs.

---

## Wiring: `from_attributes`

When a model declares `from_attributes=True`, it constructs by reading attributes from another object by name. Field names are the wiring. Properties count — Pydantic reads them via `getattr`. No mapping code, no adapter functions, no intermediate dictionaries. One object's surface becomes another object's input.

```python
Celsius = Annotated[float, Ge(-273.15)]
Fahrenheit = Annotated[float, Ge(-459.67)]
PressureKPa = Annotated[float, Gt(0)]

class RawSensor(BaseModel, frozen=True, extra="forbid"):
    temperature_celsius: Celsius
    pressure_kpa: PressureKPa

    @property
    def temperature_fahrenheit(self) -> Fahrenheit:
        return self.temperature_celsius * 9/5 + 32

class DisplayReading(BaseModel, frozen=True, extra="forbid", from_attributes=True):
    temperature_fahrenheit: Fahrenheit  # reads RawSensor's property via getattr
    pressure_kpa: PressureKPa           # reads RawSensor's stored field
```

`DisplayReading.model_validate(raw_sensor)` reads attributes by name. Properties and stored fields are both readable. Name agreement IS the wiring.

Wiring is how data gets INTO machines. External data arrives with external names and external structure. `from_attributes` lets a machine read what it needs from any object whose attributes match its field names. Combined with aliases, this subsumes the entire category of "data mapping" code that proliferates in conventional architectures: adapter classes, DTO converters, serialization layers. In TCA, the field declaration is the mapping. Where bounded contexts maintain deliberately distinct vocabularies, aliases and before-validators declare the translation on the model itself rather than in an external adapter layer.

---

## Dispatch: Discriminated Unions and Smart Enums

Instead of branching on raw data to decide which type to construct, declare a variant for each case. Each variant carries a `Literal` tag. Pydantic reads the tag and routes to the correct variant automatically. The variant's fields ARE the result.

```python
class Shipped(BaseModel, frozen=True, extra="forbid"):
    kind: Literal["shipped"] = "shipped"
    tracking: TrackingNumber
    carrier: CarrierName

class Cancelled(BaseModel, frozen=True, extra="forbid"):
    kind: Literal["cancelled"] = "cancelled"
    reason: CancellationReason
    refund: RefundAmount

OrderStatus = Annotated[
    Shipped | Cancelled,
    Field(discriminator="kind")
]

status = TypeAdapter(OrderStatus).validate_python(raw)
```

A discriminated union dispatches INTO a type whose fields already contain the answer. A `match/case` block dispatches and then you write the logic for each case. Here, selecting the variant IS the determination. Construction replaces computation.

**Enum-first classification.** When classification produces a member of a closed vocabulary, the enum owns the classification logic. A smart enum (`StrEnum` with classmethods and properties) classifies inputs into its members. The enum is the authority on which of its members an input belongs to. Wrappers expose the result via a property that delegates to the enum. Consumers ask the enum; they do not replicate its logic.

```python
class TenorBucket(StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

    @classmethod
    def from_days(cls, days: DaysToMaturity) -> TenorBucket:
        if days <= 90: return cls.SHORT
        if days <= 365: return cls.MEDIUM
        return cls.LONG
```

The [building block classifier](building-block-classifier.md) demonstrates enum-first classification at scale: `AnnotationKind.from_annotation` classifies a type annotation, a wrapper exposes the result as a property, and a discriminated union routes on it. Both are dispatch. The construction pipeline selects the correct case and the answer is baked into the type.

---

## Orchestration: Projection-Driven Construction

The first two mechanisms describe how values flow between models (wiring) and how the correct type is selected (dispatch). The third mechanism describes how proven objects drive further proof.

A `@cached_property` that calls `model_validate` is a lazy construction trigger. The projection fires on first access, constructs a new proven object, and caches it permanently on the frozen model. Each step produces a proven object from a proven object. The chain is: construction, derivation, construction, derivation, terminal.

```python
class ClassifierRun(BaseModel, frozen=True, extra="forbid"):
    target: ImportPath

    @cached_property
    def model_class(self) -> type[BaseModel]:
        return self.target.resolve()

    @cached_property
    def tree(self) -> ModelTree:
        return ModelTree.model_validate(self.model_class)

    @cached_property
    def report(self) -> TreeReport:
        return TreeReport.model_validate(self.tree)

    @cached_property
    def text(self) -> str:
        return self.report.text
```

`run.text` forces `report`, which forces `tree`, which forces `model_class`. Nothing fires until demanded.

Orchestration is what separates TCA from a validation framework. It replaces the service-layer coordination code that normally connects proven inputs to proven outputs through procedural steps. In a well-shaped TCA program, that coordination collapses into projections on frozen models.

---

## How The Mechanisms Compose

Real TCA programs do not use the mechanisms in isolation. They interlock:

1. **Wiring feeds dispatch.** A model reads another's surface via `from_attributes`. One of the attributes it reads is a tag property. That tag drives a discriminated union during coercion. Wiring delivers the data; dispatch selects the type.

2. **Dispatch settles shape.** The selected variant's fields carry the answer. `Literal` fields on the variant are proof obligations validated during construction. The variant IS the classification result.

3. **Shape triggers orchestration.** A variant with a `children` field causes Pydantic to read `.children` from the source — which fires `model_validate` on the inner type. A variant without that field stops recursion. The shape IS the orchestration decision.

The construction graph has two kinds of edges that correspond to this composition:

**Field edges** are eager. A field annotation creates a dependency that must be satisfied at construction time. If the child fails, the parent cannot exist.

**Derivation edges** are lazy. A `@cached_property` that calls `model_validate` creates a dependency that fires on first access. The parent exists whether or not the derivation is ever demanded.

Inheritance is not a graph edge in this operational sense. When `Bond` inherits from `Instrument`, Bond's pipeline includes Instrument's fields and validators, but Bond does not depend on an Instrument instance. Inheritance defines machine families — related types that share construction logic. The type families from which discriminated unions select.

The full proof graph is the union of field edges and derivation edges. The three mechanisms are how those edges fire.
