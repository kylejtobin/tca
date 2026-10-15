# Temporal development probe

This probe tests Temporal's **existing Pydantic AI durability integration** without changing the TCA agent, its workspace, its dependency lockfile, or its orchestration design. It does not implement the final development workflow.

## Start the local service

Install the [Temporal CLI](https://docs.temporal.io/cli), then start the single-binary development server with on-disk persistence:

```sh
temporal server start-dev --db-filename /tmp/tca-temporal-dev.sqlite
```

Temporal Web UI: <http://localhost:8233>. Server address: `localhost:7233`.

## Run the integration probe

From the repository root:

```sh
uv run --no-project --with 'pydantic-ai-slim[temporal]>=2.54,<3' \
  python scripts/temporal_probe.py run 'Describe a customer as a domain type.'
```

The probe uses Pydantic AI's `TestModel`, so it requires no LLM credentials and incurs no model costs. It creates a named agent with `TemporalDurability()`, registers it with `PydanticAIPlugin()`, and executes `agent.run()` inside a Temporal workflow. Inspect the workflow and activities in Temporal Web UI.

To run the worker and client separately, start a worker in one terminal:

```sh
uv run --no-project --with 'pydantic-ai-slim[temporal]>=2.54,<3' \
  python scripts/temporal_probe.py worker
```

Then start a workflow from another terminal, preserving its printed ID:

```sh
uv run --no-project --with 'pydantic-ai-slim[temporal]>=2.54,<3' \
  python scripts/temporal_probe.py start 'Describe an order as a domain type.'

uv run --no-project --with 'pydantic-ai-slim[temporal]>=2.54,<3' \
  python scripts/temporal_probe.py result '<printed-workflow-id>'
```

The worker and client use the same stable task queue. A stopped worker can be restarted to serve pending workflow tasks. This **does not** prove that an interrupted in-flight activity resumes midway: Temporal retries incomplete activities; it replays completed ones from its event history.

## Scope

This is deliberately separate from the agent implementation on `agent`. Integrating its actual agent, filesystem workspace, and checks requires using the existing agent's model and capabilities with `TemporalDurability` at construction time. The experiment does not yet prove those work under Temporal or that crash recovery and human approval gates work end to end. No database, Redis, Docker Compose overlay, workflow framework, or permanent root dependency has been added.

References: [Pydantic AI Temporal](https://ai.pydantic.dev/durable_execution/temporal/) and [Temporal development server](https://docs.temporal.io/cli/server).
