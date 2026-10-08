---
type: Construct
description: "One intended external effect, as a value that performs nothing, carrying every rule its effect must follow. Holds semantic scalars, value objects, and concept models. Lives in domain/<context>/<concept>.py, beside the fact that authorizes it."
---

```python
# domain/shop/order.py
class ReadDiscount(BaseModel):
    """The intended reading of the discount the promotions system holds for an order's customer."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: Order


class Charge(BaseModel):
    """The intended charging of a priced order's amount to its card."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: PricedOrder
```

```python
# domain/shop/order.py
class FindRelated(BaseModel):
    """The intended search of the catalog for products close to the ones a paid order bought."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: PaidOrder
    closeness: Closeness
    per_aisle: GroupSize
    limit: MatchLimit
```

```python
# domain/shop/support.py
class Answering(BaseModel):
    """The intended answering of a customer's question by the support agent."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    request: SupportRequest
```
