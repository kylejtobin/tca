---
type: Construct
description: Another system's representation lifted whole into a frozen typed boundary model.
---

# Foreign Model

## Definition

Another system owns a representation whose names, nesting, omission, or value meanings differ from this program's domain model. The foreign model is named for the other system's thing, its aliases hold that system's keys, and it lifts the source whole in one construction.

## Required Form

```python
class VenueFill(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order_id: OrderId = Field(alias="ordId")
    account: AccountId
    instrument: InstrumentId
    side: Side
    price: VenuePrice = Field(alias="px")
    quantity: VenueQuantity = Field(alias="qty")


class LedgerAcknowledgement(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    sequence: LedgerSequence
```

`LedgerAcknowledgement` is the ledger's reply, containing its assigned sequence. The [interpreter](./effect-interpreter.md) combines it with the position it submitted to construct the domain fact `PositionRecorded`; the foreign reply does not claim to carry that position.

- Nested annotations model nested source structure; domain types are reused where meaning and shape agree, and nested foreign models appear only where they differ.
- `validation_alias`, `AliasPath`, `model_validate_json`, and `from_attributes=True` lift the source whole. With `from_attributes=True` the aliases are the attribute names read from the object: `ordId`, `px`, `qty`.
- Every source field the program consumes is modeled, and no unconsumed field.
- Source-owned scalar meanings are used where the source's semantics differ.
- Names and nesting are lifted through annotations and aliases, never a field-copying transformation. A [transformation](./transformation.md) exists only for an actual semantic conversion, such as source quantities in a different unit; crossing the boundary alone justifies no lift.
- `extra` matches the source contract: forbid closed input, ignore only fields the source explicitly permits consumers to ignore.
- An alias-bearing source representation serializes with `by_alias=True`; `validation_alias` and `AliasPath` do not define output names.

## Forbidden

- foreign vocabulary copied into a domain concept
- raw dictionaries or SDK objects kept after the foreign model constructs
- fields read again from the source object
- any program-owned custom validator; annotations and aliases express construction
- a live client or resource held as a field
- a foreign model where the domain model already matches the source meaning and shape
- a transformation repeating construction already expressed by annotations, aliases, or `from_attributes=True`
