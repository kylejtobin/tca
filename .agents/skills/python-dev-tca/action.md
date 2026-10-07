---
type: Construct
description: "One intended external effect, as a value that performs nothing. Holds semantic scalars, value objects, and concept models. Lives in domain/<context>/<concept>.py, beside the fact that authorizes it."
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
class WriteNotice(BaseModel):
    """The intended writing of the notice that tells a customer their order was declined."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: DeclinedOrder
```
