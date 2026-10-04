# String formatting

- **Step kind:** string formatting that assembles a value a type should hold.
- **Hard type:** one customer's discount address.
- **Source:** `semantic-scalar.md`, `foreign-model.md`, `config.md` and `composition-root.md`.

## Incorrect

```python
class DiscountRequest(BaseModel):
    """The promotions system's question for a customer's discount."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    customer: CustomerId

    @property
    def path(self) -> ProviderPath:
        return ProviderPath(f"/discounts/{self.customer.root}")
```

## Correct

```python
class CollectionUrl(RootModel[str]):
    """The address of a collection another system holds; each thing in it is named relative to it."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")


class DiscountAddress(BaseModel):
    """The place of one customer's discount within the promotions system's discounts, named there by that customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId


class ShopConfig(BaseSettings):
    """The deployment's addresses for the promotions system and the payment provider, and the provider's key."""

    model_config = SettingsConfigDict(
        frozen=True, extra="forbid", strict=False,
        validate_default=True, revalidate_instances="never",
        env_prefix="SHOP_",
    )
    promotions_url: CollectionUrl
    payments_url: ProviderUrl
    payments_key: ProviderKey
```

```python
promotions = httpx.AsyncClient(base_url=config.promotions_url.root)
```

```python
await self.client.get(
    DiscountAddress.model_validate(self.action.order).customer.root
)
```
