---
name: tca-collection
description: Build a collection, the only legal shape for a domain sequence. MUST be invoked before writing any sequence-valued field or named sequence type. Replaces the forbidden forms; if a list/set/dict field, a collection of bare primitives, or a loop accumulating into a container is about to appear, stop and build the collection instead.
---

# collection

A collection is a homogeneous immutable sequence whose element is a declared type. As a
plain field it is `tuple[T, ...]` on a frozen model. When the sequence is a domain thing
in its own right, carrying its own constraint or implying a fact as a whole, it is a
named frozen `RootModel`, and the fact it implies is a derivation on it.

    class SmellList(RootModel[tuple[Smell, ...]], frozen=True):
        root: tuple[Smell, ...]

        @cached_property
        def smell_count(self) -> SmellCount:
            return SmellCount(len(self.root))

The element is always a declared type. A sequence of bare primitives is the element left
unforged: forge the scalar first (`tca-scalar`).

A collection with its own bound carries it as the constraint, and a collection is
constructed whole, one expression producing the tuple the `RootModel` proves;
accumulating into a mutable list first is construction in disguise and never appears:

    class FillList(RootModel[tuple[Filled, ...]], frozen=True):
        root: tuple[Filled, ...] = Field(min_length=1)

    fills = FillList(tuple(Filled.model_validate(raw) for raw in wire_rows))

An association ("price by product") is three structures, never a `dict` field, and this
is the complete shape, entry, collection, query, with the miss a constructed variant
the consumer must handle (the result variants pin their kinds per `tca-union`):

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
        def result(self) -> PriceFound | PriceMissing:
            return next(
                (PriceFound(quotation=q) for q in self.book.root if q.product == self.product),
                PriceMissing(product=self.product),
            )

Whether a key repeats is itself a question: another query model whose derivation reads
the multiplicity off the entries and returns a typed fact, never a validator.

## The row

The spec row this card expands. `element` is the tuple's element type and must
be a declared row. A plain `tuple[T, ...]` field gets no row of its own; it is
its model's field.

    {"construct": "collection", "name": "SmellList", "file": "smell.py", "element": "Smell", "constraint": "min_length=1"}

## Allowed patterns

- `field: tuple[T, ...]` on a frozen model, `T` a declared type
- `class Xs(RootModel[tuple[T, ...]], frozen=True)` with a `Field(...)` constraint
  (`min_length`, `max_length`) when the sequence carries its own bound
- derivations on the named collection returning declared types (`tca-derivation`)
- a comprehension as the transform over a collection, inside a derivation's one
  returned expression
- an entry model plus this collection plus a query model as the shape of any
  association; never a `dict` field; a cross-element question (a repeated key, an
  ordering) answered by a query model's derivation, never a validator

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
