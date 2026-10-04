# Dispatch in place of a union

- **Step kind:** a method that dispatches to a variant instead of a union whose construction picks it.
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
    """A priced order the payment provider charged, released to ship."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PricedOrder
    payment: Approval


class Cancellation(BaseModel):
    """A priced order the payment provider did not charge, released to cancel."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PricedOrder
    payment: Decline | Failure


class Settlement(RootModel[Shipment | Cancellation]):
    """What an order outcome settles into."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def order(self) -> PricedOrder:
        return self.root.order
```

```python
Settlement.model_validate(outcome)
```
