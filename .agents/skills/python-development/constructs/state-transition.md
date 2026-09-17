---
type: Reference
description: How a concept model's prior field represents immutable succession. Read when using the state-transition shape without mutation or procedural state management.
---

# State Transition

## Use

Use a concept model with a self-typed `prior` field and an opening alternative where needed. Treat state transition as this named shape, not a separate declaration form or mutation command.

A position is one account's holding in one instrument, the fold of its fills. Without both identities, the declaration names only a fold shape, not a position.

## Required Form

```python
class FlatPosition(BaseModel):
    """The opening position contains no fills."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(Decimal(0))


class Position(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    prior: "FlatPosition | Position"
    fill: Fill

    @property
    def account(self) -> AccountId:
        return self.prior.account

    @property
    def instrument(self) -> InstrumentId:
        return self.prior.instrument

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(self.prior.net_quantity.root + {Side.BUY: 1, Side.SELL: -1}[self.fill.side] * self.fill.quantity.root)

    @property
    def persistence(self) -> "PersistPosition":
        return PersistPosition(position=self)


PositionState = FlatPosition | Position
PositionStateConstructor = TypeAdapter(PositionState)
```

The holding is the net of buys and sells: the opening quantity is zero, buys add, and sells subtract. Derive [NetQuantity](semantic-scalar.md) from the prior holding and the fill's side and quantity; do not store another copy of it.

Construction gap: agreement between `fill.instrument` and `prior.instrument` has no structural form on this substrate. These fields do not establish that agreement; do not disguise the gap with a custom validator or a post-construction check.

- Construct `Position(prior=previous_position, fill=fill)` directly; let its annotations construct nested input.
- At the boundary, obtain `prior` from the read interpreter nested in the [terminal expression](composition-root.md), never a retained local snapshot.
- Keep the action and concept declarations in their domain module; read the forward-declared derivation only after declarations are complete.
- Put the prior fact and the additional facts in the successor's declared fields.
- Model compatible alternatives in those field types; do not accept arbitrary pairs and check them afterward.
- Construct the successor directly. Do not add a verb-shaped model whose only purpose is to call the successor's constructor.
- Derive implied facts on their owner through the closed [transformation](transformation.md) algebra.
- Keep any effect authorization on the fact that establishes it; the interpreter alone executes the effect.
- Preserve every predecessor. Succession is a relation between immutable values, not a mutable slot pointing at the latest one.

## Do Not

- own, mutate, or advance a current-state holder or reference
- hold or call a client, repository, cache, clock, random source, or environment
- perform persistence, publication, logging, retry, or serialization
- delegate action authorization to a caller or a separately selected transformation
- use `model_copy(update=...)`
- represent a transition rule as procedural branching inside or outside the transition model
- publish a successor before its construction completes
- introduce a custom validator, constructor override, or `model_post_init` to enact the transition
- store a duplicate successor beside the inputs that determine it
