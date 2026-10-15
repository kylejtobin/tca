---
type: Construct
description: "The callbacks whose returned expression is the whole program for one message, over the deployment's config. Holds nothing; the config is the program. Lives in main.py for a process, constructing the config at module level with one callback; in a package, in its public __init__.py, with one callback per public function taking the config."
---

```python
# main.py
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from api.shop import CheckoutRoute, ReplyRoute
from config import ShopConfig
from integration.payments.interpreter import ChargeInterpreter
from integration.promotions.interpreter import ReadDiscountInterpreter

config = ShopConfig()  # pyright: ignore[reportCallIssue]


async def checkout(request: Request) -> Response:
    return Response(
        ReplyRoute.model_validate(
            await ChargeInterpreter(
                action=(
                    await ReadDiscountInterpreter(
                        action=CheckoutRoute.model_validate_json(
                            await request.body()
                        ).order.pricing,
                        provider=config.promotions,
                    ).interpret()
                ).charge,
                provider=config.payments,
            ).interpret()
        ).model_dump_json(),
        media_type="application/json",
    )


app = Starlette(routes=(Route("/checkout", checkout, methods=("POST",)),))
```

```python
# shop/__init__.py
import asyncio

from config import ShopConfig
from domain.shop.order import FindRelated, Order, OrderOutcome, PaidOrder, RecommendedOrder
from integration.catalog_index.interpreter import FindRelatedInterpreter
from integration.payments.interpreter import ChargeInterpreter
from integration.promotions.interpreter import ReadDiscountInterpreter


async def checkout(config: ShopConfig, order: Order) -> OrderOutcome:
    return (
        await ChargeInterpreter(
            action=(
                await ReadDiscountInterpreter(
                    action=order.pricing, provider=config.promotions
                ).interpret()
            ).charge,
            provider=config.payments,
        ).interpret()
    ).outcome


def checkout_sync(config: ShopConfig, order: Order) -> OrderOutcome:
    return asyncio.run(checkout(config, order))
```

```python
# shop/__init__.py
async def recommend(config: ShopConfig, order: PaidOrder) -> RecommendedOrder:
    return (
        await FindRelatedInterpreter(
            action=FindRelated(order=order, tuning=config.recommending),
            provider=config.catalog,
        ).interpret()
    ).recommended


def recommend_sync(config: ShopConfig, order: PaidOrder) -> RecommendedOrder:
    return asyncio.run(recommend(config, order))
```
