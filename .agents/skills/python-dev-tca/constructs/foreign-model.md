---
type: Construct
description: "Shape and configuration of another system's representation, lifted whole by aliases."
---

# Foreign model

Named for the other system's thing, with the other system's names as aliases:

```python
class ClearingAcknowledgement(BaseModel):
    """The clearing house's reply accepting a record, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence


class ClearingRefusal(BaseModel):
    """The clearing house's reply declining a record, with its reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reason: RefusalReason = Field(alias="error")


ClearingReply = ClearingAcknowledgement | ClearingRefusal
ClearingReplyConstructor: TypeAdapter[ClearingReply] = TypeAdapter(ClearingReply)
```

Where a fact sits, and the field that lifts it:

| In the source | The field |
|---|---|
| under another name | `reason: RefusalReason = Field(alias="error")` |
| nested under wrappers | `fill: Fill = Field(validation_alias=AliasPath("data", "payload"))` |
| at a position | `bid: Bid = Field(validation_alias=AliasPath("root", 0))` |
| on an attribute of an attribute | `net_quantity: NetQuantity = Field(validation_alias=AliasPath("position", "net_quantity"))` |
| under the same name, with the same meaning | `sequence: ClearingSequence` |

The source, and the constructor it is given to:

| The source is | Give it to |
|---|---|
| a JSON string holding one thing | `FillRoute.receive(raw)`, which is `cls.model_validate_json(raw)` |
| a JSON string that is one of several things | `ClearingReplyConstructor.validate_json(raw)` |
| a constructed thing with attributes | `PositionOutcomeConstructor.validate_python(self, from_attributes=True)` |

`extra` is the source's contract: `"forbid"` where the source sends exactly these fields, `"ignore"` only where the source says a consumer may ignore the rest.

Constructed:

`ClearingReplyConstructor.validate_json('{"sequence": 7}')` is a `ClearingAcknowledgement` whose `sequence` is `ClearingSequence(7)`.

`ClearingReplyConstructor.validate_json('{"error": "halted"}')` is a `ClearingRefusal` whose `reason` is `RefusalReason.HALTED`.

`ClearingReplyConstructor.validate_json('{"error": "halted"}').model_dump_json(by_alias=True)` is `'{"error":"halted"}'`.

`ClearingReplyConstructor.validate_json('{"error": "unknown"}')` raises `ValidationError`: `RefusalReason` has `halted` and `stale`.

In the file:

- The class is named for the other system's thing: `ClearingAcknowledgement`, `ClearingRefusal`.
- It has one field for each fact of the source the program uses.
- Each field's type is the domain type where the meaning agrees: `ClearingSequence`, `RefusalReason`.
- Names and nesting are lifted by the aliases on the fields.
- Under `from_attributes=True` the alias is the attribute read: `Field(alias="error")` reads `source.error`.
- Where the source's meaning differs, such as a quantity in another unit, the field has a source-owned scalar, and a transformation model converts it.
- The domain holds the lifted fact: `RecordedPosition.sequence` is a `ClearingSequence`.
- Placement: `integration/clearing/model.py`.
