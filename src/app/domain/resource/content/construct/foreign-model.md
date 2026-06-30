---
name: tca_authorized_construct_foreign_model
description: Build a foreign model, the only legal shape for another system's data. MUST be invoked before touching any foreign payload, file format, message, or client reply. Replaces the forbidden forms; if a mapper, adapter, DTO, translator, json.loads dict, a field-copying function, or a before-validator that indexes or renames is about to appear, stop and model the foreign thing instead.
---
# Foreign Model

## Definition

A frozen `BaseModel` of another system's data shape, named for the other system's thing: its aliases hold that system's keys, and its fields are this program's domain meanings. It exists only when the foreign shape differs from the domain shape, and it carries every field the program uses from the foreign data.

## Required Form

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

## Sorting Rules

If the foreign shape already matches the domain model, construct the domain model directly; the constructor does the entire job and no foreign model exists. This program's own API shape is a contract model, never a foreign model. Foreign data that carries no identity and is expected to fail constructs through the ordered union. A live client is held by the consistency model, never on a foreign model.

## Replaced Forms

A mapper, adapter, translator, DTO, or field-copying function restates work the constructor owns: the foreign model lifts whole in one call. A `json.loads` dict carries unproven data through the program. A before-validator that indexes, renames, routes, or computes is an alias, a path, or a nested model not yet written.

## Construct-Specific Doctrine

The crossing takes the foreign data whole: `model_validate` on an arrived object, `model_validate_json` on arrived bytes, or keyword construction lifting a result's attributes. The foreign model carries every field the program uses, and nothing reads the foreign object after a model has been constructed from it. An omitted foreign key resolves at lifting: a default naming what omission means, or a union variant when omission means a different fact; bare `None` never crosses in. No coalesce mints data the wire did not carry. A foreign key holding a raw primitive validates into its semantic-scalar field: `model_validate` wraps the value and applies the scalar's constraint. Type the field as the scalar, never the primitive; never pre-wrap.

A foreign object graph you must walk yourself is a reported gap, but a converter that renders the graph whole as a tagged dict tree (an `ast` tree dumped to dicts, each tagged by its node kind) is a crossing: `model_validate` lifts the dict into a discriminated union keyed on the foreign tag, one frozen variant per node kind, with `extra="ignore"` for keys outside the modeled set. The walk is the converter's, not the program's.

## Allowed Patterns

- a frozen `BaseModel`, `extra="forbid"`, every field a declared type, named for the foreign thing
- `Field(alias=...)` for every rename, the aliases holding the foreign keys
- a nested foreign model for every nested foreign structure
- `validation_alias` and `AliasPath` for transport wrappers, the wrapper modeled, never indexed past
- `from_attributes=True` for objects; `model_validate_json` for serialized data
- an omitted key resolved by a named default or a variant

## Forbidden

- a mapper, adapter, translator, DTO, or field-copying function
- a `json.loads` result carried as a dict
- a before-validator that indexes, renames, routes, or computes; any `mode="after"` validator
- a model named for a pipeline stage instead of the foreign thing
- an attribute read on a foreign object after its model was constructed
- a live client or handle retained as a field

## Halt Rule

Halt when the foreign shape cannot be lifted by the declarative inventory, when lifting it would need a walk or computation you must write yourself (a converter that renders the graph whole is not that walk), or when the shapes match and a foreign model is still demanded. Report the row and the shape: the crossing is either unnecessary or unmodelable as declared, and the table is not finished.
