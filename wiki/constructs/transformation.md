---
type: Construct
description: A pure implication from proven inputs to a constructed output, within a closed one-expression algebra.
---

# Transformation

## Definition

Constructed inputs determine one constructed output without reading time, randomness, environment, mutable state, or an external capability. The derivation is the proof that its inputs imply its output, so its body is one returned expression from a closed algebra.

## Required Forms

When one model owns every input, the transformation lives on that model, as with [Position.net_quantity](./state-transition.md). Its fills carry the side needed to net buys against sells:

```python
class Fill(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order_id: OrderId
    account: AccountId
    instrument: InstrumentId
    side: Side
    price: Price
    quantity: Quantity
```

When several meanings provide the inputs, a transformation model holds them:

```python
class FillNotional(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    fill: Fill
    multiplier: ContractMultiplier

    @property
    def amount(self) -> Notional:
        return Notional(self.fill.price.root * self.fill.quantity.root * self.multiplier.root)
```

The fill and the contract multiplier determine its notional amount. The model is named for that meaning and its derivation for the output, never for a program operation with an unnamed `result`. A second price-times-quantity derivation on `Fill` would duplicate the meaning and be wrong for instruments with a multiplier; the position's own fact is net quantity, not notional.

- Every input is a field on the frozen owner, and every semantic output is explicitly constructed.
- Equal constructed inputs produce equal outputs.
- `@property` only; the returned constructor proves the output on every evaluation. `@cached_property` is assignable on a frozen model, so a cached derivation is a proof that can be replaced.
- `@computed_field` only when the output belongs to a serialized contract and derives from the contract's own fields.
- A derivation takes only `self` and its body is exactly one returned expression. A parameterized question is a frozen model holding its inputs, not a parameterized method.
- Behavior that differs by union variant is a same-named derivation on each variant, consumed without case selection.
- A [state-transition](./state-transition.md) fact that authorizes effects owns their action derivation; that authorization is never split into a caller-selected transformation or a verb-shaped wrapper around the successor constructor.

## The Closed Algebra

The algebra admits composition of Pydantic constructors, declared field and derivation reads, arithmetic over those values, a fold over a declared collection, an extremum along a declared ranked value space, selection by a proven key, a failure-exhaustive [ordered-union](./ordered-union.md) construction, and lookup of a closed vocabulary value through a total case table. A comprehension or generator is admitted only within the returned construction expression for collection construction, folding, or extrema, with no filtering `if` clause. Recursion follows declared recursive constituents through their derivations.

A case table maps every member of a closed value vocabulary to its declared value. It is not a registry of classes, callables, union variants, or workflow steps. Membership evidence is constructed through an ordered union when the present variant's sole possible refusal over the proven collection is the declared missing case; attempt order also absorbs constraint failures, so any form where a present but invalid member could read as missing is rejected. An operation outside this algebra is a reported construction gap, not permission for free code.

## Forbidden

- a free transformation function
- a read of a clock, random source, environment, global, client, cache, database, or current-state pointer
- mutation of an input or output
- the output stored beside the fields that determine it
- a bare primitive returned when the output has semantic meaning
- a transformation hidden in a validator, route, interpreter, or composition-root expression
- `@cached_property` on a semantic model
- local assignments, statement loops, `if`, `match`, `try`, mutation, or multiple statements in a derivation
- branching disguised as a ternary, `and`, `or`, a filtered comprehension, `isinstance`, a discriminator comparison, or a dispatch dictionary
- a lambda, private helper, callback, or uninspected method hiding an operation outside the algebra
- a foreign lift when annotations, aliases, and nested construction already express the same meaning
