---
type: construct
---

# Collection

## Definition

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, for a sequence that is itself a domain thing with its own name, constraint, or derivation; or a frozen `RootModel[dict[K, V]]` over a declared key `K` and value `V`, for a namespace whose key-uniqueness is the domain fact. A sequence with no meaning of its own is a `tuple[T, ...]` field on a model, not a collection.

## Required form

```python
class FillList(RootModel[tuple[Fill, ...]], frozen=True):
    root: tuple[Fill, ...] = Field(min_length=1)


fills = FillList(tuple(Fill.model_validate(report) for report in venue_reports))
```

The collection constructs whole, one expression producing the tuple the `RootModel` proves.

## Association

A namespace keyed by a domain value, key-uniqueness the domain fact, is the keyed form: a frozen `RootModel[dict[K, V]]` whose key `K` is a declared scalar and value `V` a declared type, paired with a frozen query model holding the collection and a key, whose derivation returns a found-or-missing union.

```python
class PriceBook(RootModel[dict[ProductId, Price]], frozen=True):
    root: dict[ProductId, Price]


class PriceQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    book: PriceBook
    product: ProductId

    @cached_property
    def answer(self) -> PriceFound | PriceMissing:
        return next(
            (PriceFound(price=price) for key, price in self.book.root.items() if key == self.product),
            PriceMissing(product=self.product),
        )
```

The dict holds one slot per key, so a duplicate key has no representation. The query model carries the miss, so a `dict[key]` `KeyError` or a `.get` `None` never appears. This is the named keyed form, never a bare `dict` field. Any semantic scalar used as the key defines canonical string rendering (`__str__` returning its root), proven by a substrate round-trip: a JSON object key is a string, and an unrendered scalar key corrupts on reload. When keys repeat or order is the fact, the sequence form holds instead: an entry model with declared key and value fields, a collection of those entries, and the same query model. A repeated-key question is another query model with a derivation.

## Sorting

- A sequence that is itself a domain thing, with its own name, constraint, or derivation → this construct.
- A namespace keyed by a domain value, key-uniqueness the domain fact → this construct, the keyed form under Association.
- An element that is a bare primitive → an undeclared [semantic scalar](semantic-scalar.md); build the scalar first.
- A sequence with no name, constraint, or derivation of its own → a plain `tuple[T, ...]` field on a [value object](value-object.md) or [concept model](concept-model.md).
- A fact the sequence implies as a whole → a [derivation](derivation.md) on the named collection.

## Allowed

- `field: tuple[T, ...]` on a value object or concept model, `T` a declared type
- `class Xs(RootModel[tuple[T, ...]], frozen=True)` with a `Field(...)` constraint when the sequence carries its own bound
- `class Xs(RootModel[dict[K, V]], frozen=True)` over a declared key and value when key-uniqueness is the domain fact, paired with a query model returning a found-or-missing union
- a key scalar defining canonical string rendering (`__str__` returning its root), proven to round-trip
- derivations on the named collection returning declared types
- the collection constructed whole in one expression
- a keyed collection, or an entry model with a collection of entries, plus a query model as the shape of any association

## Forbidden

- a bare `list`, `set`, or `dict` field on a domain model
- a collection element typed as a bare primitive
- a loop appending domain values into a collection
- `KeyError` or a default value as domain miss behavior
- a keyed-collection key scalar without canonical string rendering, which corrupts on round-trip
