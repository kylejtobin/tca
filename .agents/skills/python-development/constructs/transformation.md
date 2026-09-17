---
type: Reference
description: How a pure typed transformation maps proven inputs to a constructed output. Read when deriving, calculating, querying, folding, or converting program meanings.
---

# Transformation

## Use

Use when constructed inputs determine one constructed output without reading time, randomness, environment, mutable state, or an external capability.

## Required Forms

When one model owns every input, put the transformation on that model, as with [Position.net_quantity](state-transition.md). Its fills carry the side needed to net buys against sells:

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

When several meanings provide the inputs, construct a transformation model:

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

The fill and contract multiplier determine its notional amount. Name that meaning and output, not a program operation such as `ApplyDiscount` with an unnamed `result`; discounts are not part of this venue world.

Keep notional here, including the multiplier. A second price-times-quantity derivation on `Fill` duplicates that meaning and is wrong for instruments with a multiplier. The position's fact is net quantity, not notional.

- Every input is a field on the frozen owner.
- Every semantic output is explicitly constructed.
- Equal constructed inputs produce equal outputs.
- Use `@property`; the returned Pydantic constructor proves the output on every evaluation.
- Use `@computed_field` only when the output belongs to a serialized contract.
- A derivation takes only `self` and its body is exactly one returned expression. A parameterized question is a frozen model holding its inputs, not a parameterized method.
- Use only the closed algebra below. The expression's domain rule is declared by its owning meaning, not chosen by the caller.
- Behavior that differs by union variant is a same-named typed derivation on each variant, consumed without case selection.
- A [state-transition](state-transition.md) fact that authorizes effects owns their action derivation; do not split that authorization into a caller-selected transformation or a verb-shaped wrapper around the successor constructor.

The closed algebra admits composition of Pydantic constructors, declared field and derivation reads, arithmetic over those values, a fold over a declared collection, an extremum along a declared ranked value space, selection by a proven key, a failure-exhaustive ordered-union construction, and lookup of a closed vocabulary value through a total case table. A comprehension or generator is admitted only within the returned construction expression for collection construction, folding, or extrema; it has no filtering `if` clause. Recursion follows declared recursive constituents through their derivations.

A case table maps every member of a closed value vocabulary to its declared value. It is not a registry of classes, callables, union variants, or workflow steps. Construct membership evidence through an [ordered union](ordered-union.md) when the found variant's sole possible refusal over the proven collection is the declared missing case. Attempt order also absorbs constraint failures, so reject any form where a present but invalid member could become missing. Do not ban this construction merely because it is in the domain, or replace it with `.get()` returning `None` or a caught `KeyError`. An operation outside this algebra is a reported construction gap, not permission for free code.

## Do Not

- define a free transformation function
- read a clock, random source, environment, global, client, cache, database, or current-state pointer
- mutate an input or output
- store the output beside the fields that determine it
- return a bare primitive when the output has semantic meaning
- hide a transformation in a validator, route, interpreter, or composition root
- use `@cached_property` on a semantic model
- use local assignments, statement loops, `if`, `match`, `try`, mutation, or multiple statements in a derivation
- disguise branching as a ternary, `and`, `or`, a filtered comprehension, `isinstance`, discriminator comparison, or a dispatch dictionary
- call a lambda, private helper, callback, or uninspected method to hide an operation outside the algebra
- add a foreign lift when annotations, aliases, and nested construction already express the same meaning
