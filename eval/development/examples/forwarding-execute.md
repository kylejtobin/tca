# Forwarding `execute`

- **Step kind:** an `execute` that forwards to another object's `execute`.
- **Hard type:** the settlement of an order outcome: a paid order ships; a declined or unsettled order is cancelled.
- **Source:** the pattern of `OrderOutcome` in `union.md`, applied as a new class.

## Incorrect

```python
class SettlementInterpreter(RootModel[ShipInterpreter | CancelInterpreter]):
    """The settlement of an order outcome."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    async def execute(self) -> Settlement:
        return await self.root.execute()
```

## Correct

```python
class Shipment(BaseModel):
    """A paid order released to ship."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PaidOrder


class Cancellation(BaseModel):
    """An order the payment provider did not charge, released to cancel."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: DeclinedOrder | UnsettledOrder


class Settlement(RootModel[Shipment | Cancellation]):
    """What an order outcome settles into."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def order(self) -> PaidOrder | DeclinedOrder | UnsettledOrder:
        return self.root.order
```
