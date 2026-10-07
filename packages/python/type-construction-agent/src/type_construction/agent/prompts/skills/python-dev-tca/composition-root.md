---
type: Construct
description: "The config, the clients, and the callbacks whose returned expression is the whole program for one message. Holds no class. Lives in main.py for a process, with one callback; in a package, in its public __init__.py, with one callback per public function, constructing its config and clients inside that expression and never at import."
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
                        action=CheckoutRoute.model_validate_json(
                            await request.body()
                        ).order.pricing,
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

```python
# shop/__init__.py
import asyncio
from pathlib import Path

import httpx
from pydantic_ai import Agent, TemplateStr
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem, Skills

from config import ShopConfig
from domain.shop.order import DeclinedOrder, NotifiedOrder, Order, OrderOutcome
from domain.shop.type import SkillLibrary, SkillLocation
from domain.shop.value import DeclineNoticeValues
from integration.agent_skills.model import SkillDocument
from integration.model_provider.interpreter import WriteNoticeInterpreter
from integration.model_provider.model import NoticeReply
from integration.payments.interpreter import ChargeInterpreter
from integration.promotions.interpreter import ReadDiscountInterpreter
from parser.skill import read


async def checkout(order: Order) -> OrderOutcome:
    return (
        await ChargeInterpreter(
            action=(
                await ReadDiscountInterpreter(
                    action=order.pricing,
                    client=httpx.AsyncClient(base_url=ShopConfig().promotions_url.root),
                ).interpret()
            ).charge,
            client=ShopConfig().payments.client,
        ).interpret()
    ).outcome


def checkout_sync(order: Order) -> OrderOutcome:
    return asyncio.run(checkout(order))
```

```python
# shop/__init__.py
async def notify(order: DeclinedOrder) -> NotifiedOrder:
    return await WriteNoticeInterpreter(
        action=order.notice,
        client=Agent(
            ShopConfig().notices.client,
            deps_type=DeclineNoticeValues,
            output_type=NoticeReply,
            instructions=TemplateStr(
                SkillDocument.model_validate_json(read(SkillLocation.DECLINE_NOTICE)).body.root
            ),
            capabilities=(
                LocalWorkspace(Path(__file__).parent, read_only=True),
                Skills(SkillLibrary.SKILLS),
                FileSystem(read_only=True),
            ),
        ),
    ).interpret()


def notify_sync(order: DeclinedOrder) -> NotifiedOrder:
    return asyncio.run(notify(order))
```
