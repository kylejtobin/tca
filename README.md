# Type Construction Architecture

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Type Checked: basedpyright](https://img.shields.io/badge/type%20checked-basedpyright-cyan.svg)](https://github.com/DetachHead/basedpyright)

Pydantic is a programming language. Python is its runtime.

TCA is the discipline of writing programs as type construction graphs. Define the types. Wire their construction pipelines. Let `model_validate` execute. If the object exists, it's proven. If construction fails, no object exists. There is no third outcome.

**[The specification](tca.md)** defines the architecture: the construction machine and its five layers, the two fundamental mechanisms (`from_attributes` and discriminated unions), construction graphs, the program triad, and the principles that follow from treating construction as proof.

**[The construction lifecycle](construction-lifecycle.md)** describes the five phases of the construction machine with per-phase contracts, code examples from the reference architecture, and the priority principle: computation migrates toward earlier phases because earlier phases are more compositional, more testable, and reduce semantic surface area.

## The Building Block Classifier

**[`tca/building_block.py`](tca/building_block.py)** is a teaching resource, a live demonstration of every TCA mechanism in the spec, and a practical tool. Point it at any Pydantic model and it classifies every field into its structural building block — enum, newtype, record, collection, scalar — through pure construction. One `model_validate` at the root cascades the entire classification:

```python
tree = ModelTree.model_validate(Team)
print(TreeReport.model_validate(tree))
```

Here's what fires inside that single call:

```
ModelTree.model_validate(Team)              # YOU call this. One call.
│
├─► FieldSlot.model_validate( ("budget_authority", FieldInfo) )
│   │
│   │  ┌─ ANNOTATION SHAPE DU (#1: annotation form) ──────────────────┐
│   │  │  TypeAnnotation wraps the raw annotation. Pydantic reads     │
│   │  │  .kind (@property) → AnnotationKind.DIRECT                   │
│   │  │  DU selects DirectAnnotation:                                │
│   │  │    nullable = Literal[False]     (constant, not computed)    │
│   │  │    collection = Literal[False]   (constant, not computed)    │
│   │  └──────────────────────────────────────────────────────────────┘
│   │
│   │  ┌─ BLOCK SHAPE DU (#2: type classification) ───────────────────┐
│   │  │  ResolvedType wraps the inner type. Pydantic reads           │
│   │  │  .block_kind (@property) → Block.NEWTYPE                     │
│   │  │  DU selects LeafBlock:                                       │
│   │  │    No children field → recursion doesn't happen.             │
│   │  │    The shape decided.                                        │
│   │  └──────────────────────────────────────────────────────────────┘
│
│   For a RECORD field (a BaseModel):
│     DU selects RecordBlock → HAS children field
│     Pydantic reads .children → ModelTree.model_validate(inner type)
│     RECURSE. The children ARE the recursive result.
│     Construction IS descent.
│
│   For an Optional field like reports_to: RoleName | None:
│     DU selects OptionalAnnotation → nullable=Literal[True]
│     THE SHAPE IS THE ANSWER.
```

No `if` chains. No visitor pattern. No external classifiers. Two discriminated unions fire during construction — one classifies the annotation form, one classifies the type itself. The variant's `Literal` fields ARE the answer. Dispatch replaces computation.

## Why This Matters for LLMs

When a language model consumes a type schema, field names become instructions and construction becomes proof that the output is valid. TCA already preserves names, descriptions, and enum members as first-class structural elements — adding an LLM consumer activates a semantic dimension without architectural change. The same types that structure the construction graph become instructions to the model.

This phenomenon is formalized as **[Semantic Index Types](https://github.com/kylejtobin/sit)** — a companion research project exploring what happens when the compilation target reads natural language.

## Requirements

- Python 3.12+
- Pydantic 2.12+

## License

[MIT](LICENSE)
