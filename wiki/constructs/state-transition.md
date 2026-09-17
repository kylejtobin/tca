---
type: Construct
description: The concept-model shape whose self-typed prior field represents immutable succession.
---

# State Transition

## Definition

A [concept model](./concept-model.md) with a self-typed `prior` field and an opening alternative where needed. The constructed object is the successor, not a command to change an existing object; its fields establish the transition, so no consistency holder or transition procedure exists. This is a named shape, not a separate declaration form.

A position is one account's holding in one instrument, the fold of its fills. Without both identities the declaration names only a fold shape, not a position.

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

The holding is the net of buys and sells: the opening quantity is zero, buys add, sells subtract. [NetQuantity](./semantic-scalar.md) derives from the prior holding and the fill's side and quantity, never stored as a second copy. The new position authorizes its own persistence: the `persistence` derivation constructs the [action](./action.md), not an observed success. The action and the concept share their domain module with a forward-declared return annotation; constructing either performs no I/O.

Construction gap: agreement between `fill.instrument` and `prior.instrument` has no structural form on this substrate. These fields do not establish that agreement, and the gap is stated, not disguised with a validator or a post-construction check.

- `Position(prior=previous_position, fill=fill)` constructs directly; its annotations construct nested input.
- At the boundary, `prior` is the read interpreter's outcome nested in the [terminal expression](./composition-root.md), never a retained local snapshot. The in-memory current position would be a second structure for a fact the ledger already holds.
- Compatible alternatives are modeled in the field types; arbitrary pairs are never accepted and checked afterward.
- No verb-shaped model exists whose only purpose is to call the successor's constructor: the constructor is the proof of the implication, and a transition model restating it is the duplicated break.
- Every predecessor is preserved. Succession is a relation between immutable values, not a mutable slot pointing at the latest one.

## Forbidden

- a current-state holder or reference owned, mutated, or advanced
- a client, repository, cache, clock, random source, or environment held or called
- persistence, publication, logging, retry, or serialization performed
- action authorization delegated to a caller or a separately selected transformation
- `model_copy(update=...)`
- a transition rule as procedural branching inside or outside the model
- a successor published before its construction completes
- a custom validator, constructor override, or `model_post_init` to enact the transition
- a duplicate successor stored beside the inputs that determine it
