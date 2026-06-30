---
name: tca_authorized_construct_derivation
description: Build a derivation, the only legal behavior on a frozen value. MUST be invoked before writing any method, property, or computed fact on a model. Replaces the forbidden forms; if a standalone function over a model's fields, a helper, a utils entry, a stored derivable field, a parameterized method, or a bool-returning check is about to appear, stop and build the derivation instead.
---
# Derivation

## Definition

A fact that is a pure function of a frozen value's already-proven fields, written on the model that owns them. It takes only `self`, its body is one returned expression, and it returns a declared type, model, or union. The same fields yield the same fact every time, because the value they compose never changes.

## Required Form

```python
class Exposure(RootModel[Decimal], frozen=True):
    root: Decimal = Field(ge=0)


class Fill(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    order_id: OrderId
    account_id: AccountId
    fill_price: Price
    filled_quantity: Quantity

    @cached_property
    def exposure(self) -> Exposure:
        return Exposure(self.fill_price.root * self.filled_quantity.root)
```

Because a derivation is a pure function of frozen fields, `@property` and `@cached_property` return the same fact and differ only in substrate: `@property` recomputes it on each read, `@cached_property` computes it once and remembers. The choice is cost, never meaning: `@property` for a cheap fact (a constant, a single lookup), `@cached_property` when the fact is expensive, recursive, or read repeatedly, where the cache is what lets a recursion settle in one pass and a materialization happen once. `@computed_field` above `@cached_property` is the only one of the three that changes meaning: it writes the derived fact into every serialization, so it is used exactly when the fact is part of a contract shape.

Construction recurses, so a derivation over a recursive model reaches arbitrary depth with no loop: the comprehension inside the one returned expression is the whole traversal.

```python
class Portfolio(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    exposure: Exposure
    children: tuple["Portfolio", ...] = ()

    @cached_property
    def total_exposure(self) -> Exposure:
        return Exposure(self.exposure.root + sum(c.total_exposure.root for c in self.children))
```

The contract-shape form:

```python
class Quote(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    bid: Price
    ask: Price

    @computed_field
    @cached_property
    def mid(self) -> Price:
        return Price((self.bid.root + self.ask.root) / 2)
```

## Sorting Rules

A fact that differs by which union variant holds is each variant's own same-named derivation, read from the union value. A question with an input is a query model, not a parameterized method. A state transition belongs to a verb on the consistency model; a derivation stores nothing and changes nothing. The line between a derivation and a field is structural: if a pure function of the model's own fields yields the value, it is a derivation and is never also stored, since a stored copy of a derivable fact is one meaning in two structures. A value that no function of the fields can yield, because it depends on the clock, a foreign read, a random source, or input the model does not keep, is not a derivation at all; it is a field, computed once where the value is born and passed into construction. On `Quote`, `mid` is a derivation, a function of `bid` and `ask`; the moment the quote was observed would be a field, because no function of `bid` and `ask` yields it.

## Replaced Forms

A fact you are about to compute in a function, a step, or a loop is a derivation that has not found its model yet: name it on the value whose fields imply it, and the procedure is gone, the work done by the construction the derivation returns. A standalone function computing from a model's fields is that derivation escaped from its owner. A stored derivable field is a second copy of a fact kept in agreement by hand. A `bool`-returning check is an undeclared union: a staleness check returns `Fresh | Stale`, each variant carrying its own facts.

## Construct-Specific Doctrine

**The computation.** A derivation is a function from the model's proven fields to the fact it returns, which is a proof that those fields imply that fact. The computation is the proof term, and it is determined meaning, not the builder's to invent: that exposure is price times quantity and not over it is a domain decision, made once where the model lives, never at build time. The operations that compose the proof are a closed algebra, the way the constructs are a closed set: arithmetic over the fields, a fold over a collection (the catamorphism that carries the one recursion), the extremum of a collection along a ranked closed value space (the same catamorphism choosing rather than summing), selection of an element by its key, and a lookup of a closed value through a total case table. A computation that needs an operation the algebra does not hold is a reported gap, never free code. The only part of a derivation the builder decides is cost, not meaning: whether the fact is recomputed on each read or memoized once.

**Query model.** A question with an input is a composite fact: a frozen `BaseModel` holding the input and the value being queried, with the answer as a derivation on it, returning a constructed choice.

```python
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

## Allowed Patterns

- a derivation taking only `self`, body one returned expression, returning a declared type, model, or union
- `@property` to recompute a cheap fact, `@cached_property` to compute a costly, recursive, or repeatedly-read fact once, both pure over the fields
- `@computed_field` above `@cached_property` when the fact belongs to a contract's serialized shape
- a comprehension or generator expression inside the one returned expression
- the same-named derivation on every variant of a union, read from the union value
- a frozen query model holding the input and the queried value, its derivation returning the answer

## Forbidden

- a free function computing from a model's fields; a helper or utils entry
- a parameterized method on a frozen value
- a derivable field stored on a model
- a body that reads anything but the model's own fields (the clock, a client, a random source); a `@cached_property` freezes its first-read value and a `@property` returns a different value each call, so neither is a fact of the fields
- a derivation returning bare `bool`, `str`, or `int`
- a ternary, `and`, `or`, `match`, or private helper call inside the body
- serialization inside a derivation

## Halt Rule

Halt when the fact will not reduce to one returned expression over the model's own fields, when the computation needs an operation the `compute` algebra does not hold, or when it needs an input no query model row declares. Report the row and the fact: the model is missing a field, a constituent model, or a query model, or the algebra is missing an operation, and the table is not finished.
