---
type: Construct
description: "The config, the clients, and the one callback whose returned expression is the whole program for one message. Holds no class. Lives in main.py."
---

```python
# main.py
import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from api.shop import CheckoutRoute, ReplyRoute
from config import ShopConfig
from domain.shop.type import BlankPassword, FieldName, MediaType
from integration.payments.interpreter import ChargeInterpreter
from integration.promotions.interpreter import ReadDiscountInterpreter

config = ShopConfig()
promotions = httpx.AsyncClient(base_url=config.promotions_url.root)
payments = httpx.AsyncClient(
    base_url=config.payments_url.root,
    auth=(config.payments_key.root, BlankPassword().root),
    headers=((FieldName.CONTENT_TYPE, MediaType.JSON),),
)


async def checkout(request: Request) -> Response:
    return Response(
        ReplyRoute.model_validate(
            await ChargeInterpreter(
                action=(
                    await ReadDiscountInterpreter(
                        action=CheckoutRoute.model_validate_json(await request.body()).order.pricing,
                        client=promotions,
                    ).interpret()
                ).charge,
                client=payments,
            ).interpret()
        ).model_dump_json(),
        media_type=MediaType.JSON,
    )


app = Starlette(routes=(Route("/checkout", checkout, methods=("POST",)),))
```
