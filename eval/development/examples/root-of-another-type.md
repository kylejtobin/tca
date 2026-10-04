# Root of another type

- **Step kind:** the root of one type passed where another type's value is meant.
- **Hard type:** the address of one customer's discount, as handed to the client.
- **Source:** `foreign-model.md` and `effect-interpreter.md`.

## Incorrect

```python
await self.client.get(
    CustomerDiscount.model_validate(self.action.order).customer.root
)
```

## Correct

```python
class DiscountAddress(RootModel[str]):
    """The place of one customer's discount within the promotions system's discounts."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CustomerDiscount(BaseModel):
    """The discount the promotions system holds for one customer, named in its collection by that customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId

    @property
    def address(self) -> DiscountAddress:
        return DiscountAddress(self.customer.root)
```

```python
await self.client.get(
    CustomerDiscount.model_validate(self.action.order).address.root
)
```
