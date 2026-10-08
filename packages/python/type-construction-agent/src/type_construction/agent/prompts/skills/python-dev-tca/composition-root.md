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
from domain.shop.order import (
    Order,
    OrderOutcome,
    PaidOrder,
    RecommendedOrder,
)
from domain.shop.support import AnsweredRequest, SupportRequest
from domain.shop.type import PromptLibrary, PromptLocation, SkillLibrary
from domain.shop.value import SupportValues
from integration.catalog_index.interpreter import FindRelatedInterpreter
from integration.model_provider.interpreter import AnsweringInterpreter
from integration.model_provider.model import SupportReply
from integration.payments.interpreter import ChargeInterpreter
from integration.promotions.interpreter import ReadDiscountInterpreter


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
async def recommend(order: PaidOrder) -> RecommendedOrder:
    return (
        await FindRelatedInterpreter(
            action=order.related,
            client=ShopConfig().catalog.client,
        ).interpret()
    ).recommended


def recommend_sync(order: PaidOrder) -> RecommendedOrder:
    return asyncio.run(recommend(order))
```

```python
# shop/__init__.py
async def answer(request: SupportRequest) -> AnsweredRequest:
    return await AnsweringInterpreter(
        action=request.answering,
        client=Agent(
            ShopConfig().support.client,
            deps_type=SupportValues,
            output_type=SupportReply,
            instructions=TemplateStr(
                (Path(__file__).parent / PromptLibrary.PROMPTS / PromptLocation.SUPPORT).read_text()
            ),
            capabilities=(
                LocalWorkspace(Path(__file__).parent / PromptLibrary.PROMPTS, read_only=True),
                Skills(SkillLibrary.SKILLS),
                FileSystem(tools=("read_file", "list_directory")),
            ),
        ),
    ).interpret()


def answer_sync(request: SupportRequest) -> AnsweredRequest:
    return asyncio.run(answer(request))
```
