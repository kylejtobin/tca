# type-construction-agent

Type Construction Architecture's agent: a Pydantic AI agent that models a domain as types, and the reference for an agent under TCA.

```python
from type_construction.agent import AgentConfig, Prompt, run, run_sync

config = AgentConfig()

answer = await run(config, Prompt(text="Model a checkout domain."))
answer.text.root

answer = run_sync(config, Prompt(text="Model a checkout domain."))
```

A `Prompt` is the words a person gives; an `Answer` is the words the agent gives back, and Pydantic AI constructs it as the agent's structured output. The agent's prompt is `prompts/agents/tca-agent.md`, held as its instructions. The skills it may load when a task needs them are in `prompts/skills/` (`python-dev-tca`, `docker-infra-tca`, `smell-check`), which the repo's `.agents/skills/` links to; it reads their pages read-only.

The deployment names the model in the environment, as Pydantic AI names it: its provider, a colon, and the provider's name for it. The provider reads its own credentials from the environment itself; this program never holds them.

| Variable | Holds |
|---|---|
| `TCA_AGENT__MODEL` | The model: `anthropic:claude-opus-5-5`, `openai:gpt-5`, `bedrock:…`, or for Workers AI, which speaks chat completions, `openai-chat:@cf/…` with `OPENAI_BASE_URL` set to the account's endpoint. |
| `TCA_AGENT__THINKING` | How hard the model is asked to think: `minimal`, `low`, `medium`, `high` or `xhigh`, as Pydantic AI names them; `low` unless named. It is a request, and the model decides what it honors. |
| `TCA_AGENT__LIMITS__REQUEST_LIMIT` | How many model requests one run may make before it is stopped; 20 unless named. The other fields of Pydantic AI's `UsageLimits` are named the same way. |
| the provider's own | `ANTHROPIC_API_KEY`; `OPENAI_API_KEY` and `OPENAI_BASE_URL`; `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY`; `AWS_DEFAULT_REGION` with an AWS access key, session or bearer token. |

Every run is traced: the agent emits an OpenTelemetry span per run, per model request and per tool call, with tokens and latency. The OpenTelemetry SDK reads where to send them from the environment (`OTEL_EXPORTER_OTLP_ENDPOINT`), which the repository's `compose.yaml` points at its Jaeger service at `http://localhost:16686`.
