# Construction Cascade Graph (CCG)

Diagram view. The full specification (vocabulary, derivation discipline, structural integrity, invariants, deliverables, acceptance criteria) is in [ccg-spec.md](ccg-spec.md).

---

## Worked example: building_block.py

This is the CCG for the building block classifier. One `model_validate` call classifies every field on any `BaseModel` into a structural building block.

### Overview — decision structure

```mermaid
flowchart TD
    E(["ModelTree.model_validate"])
    E --> B["ModelTree._reshape<br/>boundary"]
    B --> DU1{"AnnotationShape<br/>kind"}
    B --> DU2{"BlockShape<br/>block_kind"}
    DU1 --> T1["Human text<br/>TreeReport.__str__"]
    DU2 --> T1
    DU1 --> T2["Machine JSON<br/>model_dump_json"]
    DU2 --> T2
```

### Construction flow

```mermaid
flowchart TD
    classDef boundary fill:#f4e6d0,stroke:#c9956b,stroke-width:2px
    classDef wrapper fill:#dce6f5,stroke:#6889b4,stroke-width:2px
    classDef du fill:#f5dce6,stroke:#b46889,stroke-width:2px
    classDef variant fill:#fff,stroke:#999
    classDef projection fill:#d8edd8,stroke:#6aaa6a,stroke-width:2px
    classDef recurse stroke:#c44,stroke-width:3px

    E(["ENTRY<br/>ModelTree.model_validate(SomeModel)"])
    E -->|"P2 WRAP"| B1

    B1{{"BOUNDARY P2<br/>ModelTree._reshape<br/>dict.items to FieldSlot tuples<br/>+ cycle guard (ContextVar)"}}:::boundary
    B1 -->|"P1 BEFORE (each FieldSlot)"| FS

    FS["PRODUCT<br/>FieldSlot (frozen)<br/>field_name + annotation"]:::boundary
    FS -->|"P3 COERCE<br/>raw annotation to TypeAnnotation"| W1
    FS -->|"P3 ATTR .resolved_type"| W2

    W1("WRAPPER<br/>TypeAnnotation (RootModel)<br/>.kind: AnnotationKind<br/>.resolved_type: inner type"):::wrapper
    W1 -->|"P3 ATTR .kind"| DU1

    DU1{"DU AnnotationShape<br/>discriminator=kind"}:::du
    DU1 -->|"DU_ROUTE direct"| VA1["DirectAnnotation<br/>nullable=Literal(False)<br/>collection=Literal(False)"]:::variant
    DU1 -->|"DU_ROUTE optional"| VA2["OptionalAnnotation<br/>nullable=Literal(True)<br/>collection=Literal(False)"]:::variant
    DU1 -->|"DU_ROUTE tuple"| VA3["TupleAnnotation<br/>nullable=Literal(False)<br/>collection=Literal(True)"]:::variant

    W2("WRAPPER<br/>ResolvedType (RootModel)<br/>.block_kind: Block<br/>.children: ModelTree"):::wrapper
    W2 -->|"P3 ATTR .block_kind"| DU2

    DU2{"DU BlockShape<br/>discriminator=block_kind"}:::du
    DU2 -->|"DU_ROUTE record"| VB1["RecordBlock<br/>children: tuple(ClassifiedNode,...)"]:::recurse
    DU2 -->|"DU_ROUTE enum/newtype/scalar"| VB2["LeafBlock<br/>no children field<br/>STOP"]:::variant

    VB1 -->|"RECURSE<br/>children field triggers<br/>ModelTree.model_validate"| E

    FS -->|"P3 from_attributes<br/>to FieldEntry to ClassifiedNode"| CN["PRODUCT<br/>ClassifiedNode (frozen)<br/>two DUs resolved"]

    CN -->|"P3 from_attributes"| FR[/"PROJECTION<br/>FieldReport<br/>.line .lines"/]:::projection

    FR -->|"P3 from_attributes"| TR[/"PROJECTION<br/>TreeReport<br/>.text / __str__<br/>.model_dump_json"/]:::projection
```
