---
name: tca-derivation
description: Build a derivation, the only legal behavior on a frozen value. MUST be invoked before writing any method, property, or computed fact on a model. Replaces the forbidden forms; if a standalone function over a model's fields, a helper, a utils entry, a stored derivable field, or a bool-returning check is about to appear, stop and build the derivation instead.
---

# derivation

A derivation is a fact a frozen model implies from its own already-proven fields: the
only behavior a frozen value has, an edge that stores nothing.

    class SmellList(RootModel[tuple[Smell, ...]], frozen=True):
        root: tuple[Smell, ...]

        @cached_property
        def smell_count(self) -> SmellCount:
            return SmellCount(len(self.root))

It takes only `self` and returns a constructed declared type, never a bare
`bool`/`str`/`int`: a `bool` that gates is an unforged union, a bare primitive an
unforged scalar. The body is one returned expression. The consumer reads the typed value
(`smells.smell_count`); serialization is projection's job at a boundary, never the
derivation's. When the fact differs by which variant a union holds, every variant
carries the same-named derivation (`tca-union`) and the envelope forwards
(`tca-discriminated-union`). Construction recurses, so a derivation over a recursive
model reaches arbitrary depth with no loop written: the comprehension inside its one
expression is the whole traversal.

When the fact must also cross the wire, `@computed_field` rides above
`@cached_property`, so the derivation projects into every dump; the choice among
`property`/`cached_property`/`computed_field` is only caching and serialization, never
what it returns:

    class Spread(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        best_bid: Price
        width: SpreadWidth

        @computed_field
        @cached_property
        def best_ask(self) -> Price:
            return Price(self.best_bid.root + self.width.root)

Construction recurses, so a derivation over a recursive model reaches arbitrary depth
with no loop written; the comprehension inside its one expression is the whole
traversal:

    class Node(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        weight: Weight
        children: tuple["Node", ...] = ()

        @cached_property
        def total_weight(self) -> Weight:
            return Weight(self.weight.root + sum(c.total_weight.root for c in self.children))

The contrast that fails the test, the bool gate: `def is_stale(self) -> bool` is an
unforged union. The derivation returns `Fresh | Stale`, each variant carrying its own
facts, and the consumer matches.

A question with a free variable is not a parameterized method; it is a composite fact.
Compose the free variable and the value it interrogates as the two fields of a frozen
query model; the answer is its derivation, taking only `self`, returning a choice.
Every parameterized helper is a query model not yet named.

    class PriceQuery(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        book: PriceBook
        product: ProductId

        @cached_property
        def result(self) -> Found | Missing:
            return next(
                (Found(quotation=q) for q in self.book.root if q.product == self.product),
                Missing(product=self.product),
            )

## The row

The spec row this card expands. `name` is the property, `on` the model row (the
derivation lives in its model's file), `returns` a declared row. A method the
table does not declare is denied at the write.

    {"construct": "derivation", "name": "smell_count", "file": "smell.py", "on": "SmellList", "returns": "SmellCount"}

## Allowed patterns

- `@cached_property` taking only `self`, body one returned expression, returning a
  declared type, union, or model
- `@computed_field` above `@cached_property`, only when the fact crosses the wire on a
  boundary contract or event
- `@property` for a trivial read
- a comprehension or generator expression inside the one returned expression as the
  transform over a collection
- the same-named derivation on each union variant, forwarded by the envelope
- a frozen query model composing the free variable with the value it interrogates, its
  derivation returning the answer as a constructed choice

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
