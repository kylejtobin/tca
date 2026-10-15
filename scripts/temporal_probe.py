"""Offline Pydantic AI / Temporal integration probe; no TCA agent changes."""

import argparse
import asyncio
from typing import ClassVar
from uuid import uuid4

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalDurability,
)
from pydantic_ai.models.test import TestModel
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "tca-temporal-probe"
AGENT = Agent(
    TestModel(),
    name="tca-temporal-probe",
    capabilities=[TemporalDurability()],
)


@workflow.defn
class ProbeWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__: ClassVar[list[Agent[None, str]]] = [AGENT]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await AGENT.run(prompt)
        return result.output


async def main(command: str, value: str) -> None:
    client = await Client.connect("localhost:7233", plugins=[PydanticAIPlugin()])

    if command == "worker":
        async with Worker(client, task_queue=TASK_QUEUE, workflows=[ProbeWorkflow]):
            print(f"Listening on task queue {TASK_QUEUE}", flush=True)
            await asyncio.Event().wait()
    elif command == "start":
        handle = await client.start_workflow(
            ProbeWorkflow.run,
            value,
            id=f"tca-temporal-probe-{uuid4()}",
            task_queue=TASK_QUEUE,
        )
        print(handle.id)
    elif command == "result":
        print(await client.get_workflow_handle(value).result())
    else:
        async with Worker(client, task_queue=TASK_QUEUE, workflows=[ProbeWorkflow]):
            result = await client.execute_workflow(
                ProbeWorkflow.run,
                value,
                id=f"tca-temporal-probe-{uuid4()}",
                task_queue=TASK_QUEUE,
            )
            print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "worker", "start", "result"))
    parser.add_argument(
        "value",
        nargs="?",
        default="Describe one domain concept as a type.",
        help="Prompt for run/start, workflow ID for result",
    )
    args = parser.parse_args()
    if args.command == "result" and args.value == "Describe one domain concept as a type.":
        parser.error("result requires a workflow ID from start")
    asyncio.run(main(args.command, args.value))
