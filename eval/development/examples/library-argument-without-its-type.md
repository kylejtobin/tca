# Library argument without its type

- **Step kind:** a value handed to a library that was not read from a constructed instance of the type the argument means.
- **Hard type:** the address of one customer's discount, as handed to the client.
- **Source:** `foreign-model.md` and `effect-interpreter.md`.

## Incorrect

```python
await self.client.get(
    self.action.order.customer.root
)
```

## Correct

```python
class DiscountAddress(BaseModel):
    """The place of one customer's discount within the promotions system's discounts, named there by that customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId
```

```python
await self.client.get(
    DiscountAddress.model_validate(self.action.order).customer.root
)
```
