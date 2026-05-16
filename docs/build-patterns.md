# TCA Build Patterns

These patterns describe how construction computes, but more importantly they describe how to actually build in TCA. They are not a closed taxonomy. They are the moves an architect actually needs to reach for, in dependency order: name the domain vocabulary, let fields prove themselves at construction, own the foreign schema, absorb transport wrappers on that same boundary, hand live input to it, lift into domain truth, build richer semantic worlds, let other models read declared surfaces, derive intrinsic facts, route structurally, and finally render a terminal result from owned proof.

To keep the build path legible, the examples below all use the same world: a structural smell detector that walks Python source. The running types — `LineNumber`, `ClassName`, `MethodName`, `SourceLocation`, `Smell`, `FileContext`, plus the AST-classification types from `tca/building_block.py` (`TypeAnnotation`, `AnnotationShape`, `BlockShape`, `ClassifiedNode`, `ModelTree`, `TreeReport`) — all live in this repo. The patterns are domain-agnostic; the running example just keeps the build path coherent.

### Name The Domain Scalars First

First, own the domain values themselves before any larger model starts using them.

**Bad Procedural Pattern**

```python
class Smell(BaseModel, frozen=True):
    invariant_name: str
    message: str
    line: int
    class_name: str | None
    method_name: str | None
```

**Why it is bad:** The model has field names, but the values are still flat unowned primitives, so the domain is only half modeled.

**TCA Pattern**

```python
class LineNumber(RootModel[int], frozen=True):
    root: int

class InvariantName(RootModel[str], frozen=True):
    root: str

class Message(RootModel[str], frozen=True):
    root: str

class Smell(BaseModel, frozen=True):
    invariant_name: InvariantName
    message: Message
    location: SourceLocation
```

This is correct because the domain vocabulary exists as owned scalar types before larger models start composing with it, and the first composed model closes the contrast pair completely. The same scalar move is what later legitimizes `ClassName`, `MethodName`, and the closed vocabulary `Block`.

### Let Fields Declare Their Own Constraints

Once the domain fields exist, let their declarations carry as much proof as possible before you reach for procedure.

**Bad Procedural Pattern**

```python
class SmellPayloadNormalizer:
    def normalize(self, raw: dict[str, object]) -> dict[str, object]:
        normalized: dict[str, object] = {}

        name = str(raw["invariant_name"]).strip()
        if not name:
            raise ValueError("invariant_name is required")
        normalized["invariant_name"] = name

        message = str(raw["message"]).strip()
        if not message:
            raise ValueError("message is required")
        normalized["message"] = message

        line = int(raw["line"])
        if line < 1:
            raise ValueError("line must be positive")
        normalized["line"] = line

        return normalized
```

**Why it is bad:** Field-level proof has escaped into a procedural normalizer layer, so every new field becomes more parser code, more staging dicts, and more hand-written cleanup before the model gets to own its own boundary.

**TCA Pattern**

```python
class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)

class InvariantName(RootModel[str], frozen=True):
    root: str = Field(min_length=1, pattern=r"^[A-Z][A-Za-z0-9_]*$")

class Message(RootModel[str], frozen=True):
    root: str = Field(min_length=1)
```

This is correct because the constraints now live directly on the fields that own them, and Pydantic enforces them at construction without forcing the program to grow a separate normalizer service. Reach for validators later only when the proof cannot be expressed declaratively on the field itself.

### Mirror The Foreign Schema

Next, own the foreign payload shape declaratively at the boundary instead of translating it procedurally.

**Bad Procedural Pattern**

```python
class HookPayloadAdapter:
    def translate_hook_message(self, payload: dict[str, object]) -> dict[str, object]:
        tool_name = str(payload["tool_name"])
        tool_input = payload["tool_input"]
        file_path = str(tool_input["file_path"])

        translated: dict[str, object] = {}
        translated["tool_name"] = tool_name
        translated["file_path"] = file_path
        return translated
```

**Why it is bad:** The foreign field translation is now trapped in a procedural adapter layer that rebuilds an unowned payload shape by hand.

**TCA Pattern**

```python
class HookToolInput(BaseModel, frozen=True):
    file_path: FilePath

class HookEvent(BaseModel, frozen=True):
    tool_name: ToolName
    tool_input: HookToolInput
```

This is correct because the seam models foreign truth faithfully while the rest of the program keeps speaking owned domain language. This is still foreign ownership, not domain truth yet.

### Normalize The Payload

After mirroring the foreign schema, absorb any outer transport wrapper on that same boundary model.

**Bad Procedural Pattern**

```python
class FieldSlotRouter:
    def route_field(self, item: dict[str, object]) -> None:
        name = item["name"]
        info = item["info"]
        self._field_handler.handle_field(name, info)
```

**Why it is bad:** The wrapper-removal logic now leaks into procedural handlers, so the seam stops being terminal and the positional tuple shape keeps spreading.

**TCA Pattern**

```python
class FieldSlot(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    field_name: str = Field(alias="name")
    annotation: TypeAnnotation

    @model_validator(mode="before")
    @classmethod
    def _from_tuple(cls, data: tuple[str, FieldInfo]) -> dict[str, object]:
        return {"field_name": data[0], "annotation": data[1].annotation}
```

This is correct because the same boundary model now absorbs the positional `(name, FieldInfo)` tuple once instead of forcing procedural code to unpack it over and over. (Real example: `FieldSlot` in `tca/building_block.py`.)

### Capture Live Input

Once that boundary model is ready, keep the live seam thin: catch raw transport input and hand it off immediately.

**Bad Procedural Pattern**

```python
raw = sys.stdin.read()
envelope = json.loads(raw)
tool_input = envelope["tool_input"]
if not tool_input["file_path"].endswith(".py"):
    sys.exit(0)
path = tool_input["file_path"]
process(path)
```

**Why it is bad:** The hook entry point now owns parsing, wrapper access, field extraction, and business meaning instead of handing raw transport reality off immediately.

**TCA Pattern**

```python
event = HookEvent.model_validate_json(sys.stdin.read())
yield event
```

This is correct because the live edge does one job only: catch unstable input and hand it straight to the boundary model that already knows how to absorb the envelope and own the payload. The hook intake is now just an edge.

### Lift Into Domain Truth

Once the foreign object is proven, cross directly into owned domain truth by construction.

**Bad Procedural Pattern**

```python
class HookEventTranslator:
    def to_file_context(self, event: HookEvent) -> FileContext:
        translated: dict[str, object] = {}
        translated["path"] = event.tool_input.file_path.root
        translated["source"] = Path(event.tool_input.file_path.root).read_text()
        return FileContext(**translated)
```

**Why it is bad:** The foreign-to-domain crossing is now trapped in a procedural translation step that manually rebuilds domain values one field at a time.

**TCA Pattern**

```python
event = HookEvent.model_validate_json(raw_message)
ctx = FileContext(path=event.tool_input.file_path, source=event.tool_input.file_path.read_text())
```

This is correct because the foreign object is already proven, and the domain construction reads from it directly without a translator layer. This is the first point where owned domain truth begins.

### Compose Proven Models

Now construct a richer semantic world by owning already-proven models as fields.

**Bad Procedural Pattern**

```python
class ClassificationService:
    def build_context(
        self,
        field_name: str,
        annotation_shape: AnnotationShape,
        block_shape: BlockShape,
    ) -> dict[str, object]:
        context_payload: dict[str, object] = {}
        context_payload["field_name"] = field_name
        context_payload["shape"] = annotation_shape
        context_payload["block_shape"] = block_shape
        return context_payload
```

**Why it is bad:** The semantic world gets rebuilt procedurally on demand instead of existing as one owned proven object.

**TCA Pattern**

```python
class ClassifiedNode(FieldEntry, frozen=True, from_attributes=True):
    block_shape: BlockShape = Field(alias="resolved_type")

    @property
    def block(self) -> Block:
        return self.block_shape.block_kind

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return self.block_shape.children
```

This is correct because the richer semantic world now exists as one proven object instead of a temporary coordination payload. `ClassifiedNode` is introduced here in its final shape: inherits `FieldEntry`, adds `BlockShape`, exposes flat delegation properties for downstream readers. (Real example: `ClassifiedNode` in `tca/building_block.py`.)

### Read Another Model's Surface

Once a model exposes a declared surface, let downstream construction read it directly instead of rebuilding it.

**Bad Procedural Pattern**

```python
class FieldEntryDTO(BaseModel, frozen=True):
    field_name: str
    nullable: bool
    collection: bool

class FieldEntryMapper:
    def from_slot(self, slot: FieldSlot) -> FieldEntryDTO:
        return FieldEntryDTO(
            field_name=slot.field_name,
            nullable=slot.annotation.nullable,
            collection=slot.annotation.collection,
        )
```

**Why it is bad:** The mapping layer duplicates a surface that already exists, so the program pays procedural cost to restate what one model was already declaring.

**TCA Pattern**

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

    @property
    def collection(self) -> bool:
        return self.shape.collection

entry = FieldEntry.model_validate(slot)
```

This is correct because the next model reads the declared surface that already exists — `TypeAnnotation`'s `@property` outputs flow through `getattr` during `model_validate`. This is borrowed truth, not newly derived truth. (Real example: `FieldEntry` in `tca/building_block.py`.)

### Derive On The Model

Once a model owns enough proven structure, extend that same model with a named intrinsic fact that belongs to it.

**Bad Procedural Pattern**

```python
class SmellRendererService:
    def render(self, smell: Smell) -> str:
        return f"{smell.invariant_name}: {smell.message} ({smell.location.qualified})"
```

**Why it is bad:** The derivation is not owned at all. It is just inline string construction at the call site, so the program keeps rediscovering intrinsic truth instead of naming and owning it.

**TCA Pattern**

```python
class Smell(BaseModel, frozen=True):
    invariant_name: InvariantName
    message: Message
    location: SourceLocation

    @cached_property
    def rendered(self) -> str:
        return f"{self.invariant_name.root}: {self.message.root} ({self.location.qualified})"
```

This is correct because the same `Smell` now owns the intrinsic fact that can be derived from the fields it already proved. (Real example: `Smell.rendered` in `.claude/scripts/smell.py`.)

### Declare Cases Instead Of Branching

Once the domain world exists, let type selection replace branch-based control flow.

**Bad Procedural Pattern**

```python
class AnnotationRouter:
    def route(self, raw: dict[str, object]) -> None:
        if raw["kind"] == "direct":
            event = {
                "kind": "direct",
                "resolved_type": raw["resolved_type"],
                "nullable": False,
                "collection": False,
            }
            self._direct_handler.handle(event)
        elif raw["kind"] == "optional":
            event = {
                "kind": "optional",
                "resolved_type": raw["resolved_type"],
                "nullable": True,
                "collection": False,
            }
            self._optional_handler.handle(event)
        elif raw["kind"] == "tuple":
            event = {
                "kind": "tuple",
                "resolved_type": raw["resolved_type"],
                "nullable": False,
                "collection": True,
            }
            self._tuple_handler.handle(event)
```

**Why it is bad:** The procedure is doing dispatch that structure already knows how to do, so the case logic lives in branch code instead of in the types that own the cases.

**TCA Pattern**

```python
class DirectAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.DIRECT] = AnnotationKind.DIRECT
    resolved_type: object
    nullable: Literal[False]
    collection: Literal[False]

class OptionalAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.OPTIONAL] = AnnotationKind.OPTIONAL
    resolved_type: object
    nullable: Literal[True]
    collection: Literal[False]

class TupleAnnotation(BaseModel, frozen=True, from_attributes=True):
    kind: Literal[AnnotationKind.TUPLE] = AnnotationKind.TUPLE
    resolved_type: object
    nullable: Literal[False]
    collection: Literal[True]

AnnotationShape = Annotated[
    DirectAnnotation | OptionalAnnotation | TupleAnnotation,
    Field(discriminator="kind"),
]

shape = TypeAdapter(AnnotationShape).validate_python(raw)
```

This is correct because the cases are declared once as types, and construction selects the right one structurally. Construction is now the switch statement. (Real example: `AnnotationShape` in `tca/building_block.py` has six variants total.)

### Unfold Composite Inputs

Some declared cases are complete immediately, while others continue construction because their own shape still contains more of the same world.

**Bad Procedural Pattern**

```python
class TypeTreeBuilder:
    def build(self, raw: dict[str, object]) -> object:
        if raw["block_kind"] == "record":
            built_children = []
            for child in raw["children"]:
                built_children.append(self.build(child))
            return {
                "block_kind": "record",
                "children": built_children,
            }

        return {
            "block_kind": raw["block_kind"],
        }
```

**Why it is bad:** Traversal code is now deciding the program's shape procedurally instead of letting the selected variant declare whether construction stops or continues.

**TCA Pattern**

```python
class RecordBlock(BaseModel, frozen=True, from_attributes=True):
    block_kind: Literal[Block.RECORD] = Block.RECORD
    children: tuple[ClassifiedNode, ...]

class LeafBlock(BaseModel, frozen=True, from_attributes=True):
    block_kind: Literal[
        Block.ENUM, Block.NEWTYPE, Block.COLLECTION, Block.SCALAR, Block.UNION
    ]
    # No children field — the variant's shape IS the decision not to recurse

BlockShape = Annotated[
    RecordBlock | LeafBlock,
    Field(discriminator="block_kind"),
]
```

This is correct because the selected variant's shape determines whether construction is complete now or must continue into children. `RecordBlock.children` reads `ResolvedType.children`, which fires `ModelTree.model_validate` recursively. `LeafBlock` has no children field, so the property never fires. The variant's shape IS the recursion decision. (Real example: `BlockShape` in `tca/building_block.py`.)

### Let One Construction Trigger The Next

Once the seam and domain path are stable, introduce a dedicated root object whose job is to let one proven result trigger the next.

**Bad Procedural Pattern**

```python
class ClassifierWorkflowService:
    def __init__(self, importer, classifier, reporter, renderer) -> None:
        self._importer = importer
        self._classifier = classifier
        self._reporter = reporter
        self._renderer = renderer

    def run(self, target: str) -> str:
        model_class = self._importer.resolve(target)
        tree = self._classifier.classify(model_class)
        report = self._reporter.build(tree)
        return self._renderer.render(report)
```

**Why it is bad:** The coordinator now owns the semantic path of the program, so construction becomes a script instead of a graph that extends itself through proven objects.

**TCA Pattern**

```python
class ClassifierRun(BaseModel, frozen=True):
    target: str
    json_output: bool = False

    @cached_property
    def model_class(self) -> type[BaseModel]:
        module_path, class_name = self.target.rsplit(":", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    @cached_property
    def tree(self) -> ModelTree:
        return ModelTree.model_validate(self.model_class)

    @cached_property
    def report(self) -> TreeReport:
        return TreeReport.model_validate(self.tree)
```

This is correct because each proven result becomes the natural source for the next construction, and the path lives on the model instead of in a coordinator script. The new root type is justified here because the lesson is orchestration-by-construction. (Real example: `ClassifierRun` in `tca/building_block.py`.)

### Render The Final Shape

Finally, let the terminal human-facing or machine-facing surface emerge from owned truth.

**Bad Procedural Pattern**

```python
class TreePresenter:
    def render(self, tree: ModelTree) -> str:
        parts: list[str] = []
        for node in tree.fields:
            parts.append(f"{node.field_name}: {node.block}")
            for child in node.children:
                parts.append(f"  {child.field_name}: {child.block}")
        return "\n".join(parts)
```

**Why it is bad:** The output layer is rebuilding truth it does not own, so the final artifact is no longer emerging directly from the proof source.

**TCA Pattern**

```python
class TreeReport(BaseModel, frozen=True, from_attributes=True):
    reports: tuple[FieldReport, ...] = Field(alias="fields")

    @computed_field
    @cached_property
    def text(self) -> str:
        def _indent(report: FieldReport, depth: int) -> tuple[str, ...]:
            prefix = "  " * depth
            return (
                f"{prefix}{report.line}",
                *(line for child in report.children for line in _indent(child, depth + 1)),
            )
        return "\n".join(line for r in self.reports for line in _indent(r, 0))

report = TreeReport.model_validate(tree)
```

This is correct because the terminal artifact now emerges directly from the semantic world already established above instead of being reconstructed in a presenter layer. The program is now emitting its final surface. (Real example: `TreeReport.text` in `tca/building_block.py`.)
