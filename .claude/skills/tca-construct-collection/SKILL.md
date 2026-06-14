---
name: tca-construct-collection
description: Build a collection, the only legal shape for a domain sequence. MUST be invoked before writing any sequence-valued field or named sequence type, and before any mapping keyed by a domain value. Replaces the forbidden forms; if a list, set, or dict field, a collection of bare primitives, or a loop accumulating into a container is about to appear, stop and build the collection instead.
---
# Collection

## Definition

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, for a sequence that is itself a domain thing with its own name, constraint, or derivation. A sequence with no meaning of its own is a `tuple[T, ...]` field on a model, not a collection.

## Required Form

```python
class FillList(RootModel[tuple[Fill, ...]], frozen=True):
    root: tuple[Fill, ...] = Field(min_length=1)


fills = FillList(tuple(Fill.model_validate(report) for report in venue_reports))
```

The collection constructs whole, one expression producing the tuple the `RootModel` proves.

## Sorting Rules

An element that is a bare primitive is an undeclared semantic scalar: build the scalar first. A sequence with no name, constraint, or derivation of its own is a plain `tuple[T, ...]` field on a value object or concept model. A fact the sequence implies as a whole is a derivation on the named collection.

## Replaced Forms

A `list`, `set`, or `dict` field is an unconstrained mutable container where a proven sequence belongs. A loop appending into a container is construction performed as procedure; the comprehension inside the construction call is the whole build.

## Association

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

## The Row

```json
{"construct": "collection", "name": "FillList", "file": "fill.py", "element": "Fill", "constraint": "min_length=1"}
```

`element` names a declared row. `constraint` is the `Field(...)` argument list verbatim and is omitted when the sequence carries no bound. A plain `tuple[T, ...]` field gets no row; it is its model's field.

## Allowed Patterns

- `field: tuple[T, ...]` on a value object or concept model, `T` a declared type
- `class Xs(RootModel[tuple[T, ...]], frozen=True)` with a `Field(...)` constraint when the sequence carries its own bound
- derivations on the named collection returning declared types
- the collection constructed whole in one expression
- an entry model, a collection of entries, and a query model as the shape of any association

## Forbidden

- a `list`, `set`, or `dict` field on a domain model
- a collection element typed as a bare primitive
- a loop appending domain values into a collection
- `KeyError` or a default value as domain miss behavior

## Halt Rule

Halt when the element is not a declared row, or when a cross-element rule cannot be expressed as a constraint or a query model's derivation. Report the row and the rule: the element or the question is not yet modeled, and the table is not finished.
