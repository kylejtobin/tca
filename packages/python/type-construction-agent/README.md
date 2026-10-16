# type-construction-agent

Type Construction Architecture's agent: a Pydantic AI agent that models a domain as types, and the reference for an agent under TCA.

```python
from type_construction.agent import AgentConfig, Prompt, PromptText, run_sync

answer = run_sync(AgentConfig(), Prompt(text=PromptText("Model a checkout domain.")))
print(answer.text.root)
```

In an async program, `await run(config, prompt)` returns the same `Answer`; a graph or any other async caller uses `run`, never `run_sync`, which starts its own event loop. Both take three optional keyword arguments, Pydantic AI's own execution resources: `usage`, a `RunUsage` the run accumulates into; `cancellation_token`, a `CancellationToken` the caller owns, which when cancelled raises Pydantic AI's `RunCancelled` and stays cancelled; and `toolsets`, a sequence of Pydantic AI's toolsets this one run may call beside the agent's own, as a program that orchestrates the agent hands it its own.

The agent's tools are Pydantic AI's own: its file and shell tools, and its skills. It carries no callback of this program. The workspace declares its check as an executable named `check` at its root, the loop in the agent's prompt runs it through the shell after every file, and nonzero is not done. `answer` returns Pydantic AI's own `AgentRunResult[Answer]`, the answer with every message, the usage and the run's id; `run` returns the answer alone.

A `Prompt` is the words a person gives; an `Answer` is the words the agent gives back, and Pydantic AI constructs it as the agent's structured output: an answer that does not validate as one is sent back to the model, and one the model cannot form is refused with Pydantic AI's own `UnexpectedModelBehavior`. One run is one answer: the agent holds no conversation between runs. Its prompt is `prompts/agents/tca-agent.md`, held as its instructions. It works in the workspace the deployment names, and loads its skills from that directory's `.agents/skills`.

## Configuring it

A deployment names three things: the model; the workspace the agent models in, with the boundary it runs in; and the SQLite file its runs are recorded in, which defaults to `tca-agent.sqlite` where the program runs. The agent has no other setting: Pydantic AI's own defaults govern a run, its request limit, its timeouts and how hard the model thinks, and the named provider reads its credentials and endpoint from its own variables. The agent's settings are read under `TCA_` from the process environment or from a `.env` file in its working directory, the environment winning; a key another system owns in that file is left to it, and a setting the agent does not have is refused.

The workspace is not the directory the program runs in. It holds the skills under `.agents/skills`, its check as an executable named `check` at its root, and the work, and nothing else: the agent reads and runs whatever is in it, and what it reads enters the model's context and its traces, so a key never lives there. Its kind is the boundary, as Pydantic AI draws it: `local` is the library's local workspace, which isolates nothing; `sandbox` is that workspace in the library's bubblewrap sandbox, where every command sees the host read-only, has no network, and writes only inside the directory. The sandbox needs `bwrap` on the machine. The check must exit zero only when the work is clean, and in a sandbox must write nothing outside the directory, so a linter's cache goes inside it or nowhere. A workspace that does not exist is refused on the first run with Pydantic AI's own `WorkspaceUnavailableError`.

| Variable | Holds |
|---|---|
| `TCA_AGENT__MODEL` | A model as Pydantic AI names it, its provider first: `anthropic:claude-opus-5-5`, `openai-chat:gpt-5`, `bedrock:…`; `test` is Pydantic AI's own offline model. |
| `TCA_AGENT__WORKSPACE__KIND` | The workspace's boundary: `local` or `sandbox`. |
| `TCA_AGENT__WORKSPACE__PATH` | The directory the agent models in. |
| `TCA_AGENT__HISTORY__DATABASE` | The SQLite file the agent's runs are recorded in; `tca-agent.sqlite` when unset. |
| the provider's own | `ANTHROPIC_API_KEY`; `OPENAI_API_KEY`, and `OPENAI_BASE_URL` for a model an OpenAI-compatible endpoint serves, as `openai-chat:@cf/zai-org/glm-5.3-flash` at Workers AI; `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY`; `AWS_DEFAULT_REGION` with an AWS access key, session or bearer token. |

A model Pydantic AI does not know, or one whose credentials are missing, is refused on the first run with Pydantic AI's own `UserError`, saying what to set.

## Testing it offline

`TCA_AGENT__MODEL=test` runs the agent on Pydantic AI's `TestModel`, with no credentials. A test that scripts the model's replies hands Pydantic AI its own `FunctionModel` or `TestModel` wherever the library would infer that name, by `monkeypatch.setattr(pydantic_ai.models, "infer_model", …)`; the package's tests show it.

## Seeing what a run did

`AnswerInterpreter(prompt=prompt, provider=config.agent).interpret()` returns Pydantic AI's own `AgentRunResult[Answer]`: the answer as `output`, every message, the usage and the run's id. Beside `usage` and `cancellation_token` it takes `event_stream_handler`, to which Pydantic AI streams the run's events as they happen, every part, tool call and tool result, while the run still holds its model; a handler that raises stops the run, and the model is released all the same.

## Remembering its runs

Every run is recorded by Pydantic AI's own step persistence in the SQLite file the deployment names, made when it is missing and used when it is there: the run under the agent's name, each model request and tool call as an event, and a continuable snapshot of the run's messages. Runs of one conversation share a conversation id, the run's own by default. A program continues a conversation with the library's own `continue_run` over the same store, handing what it returns to the next run as `message_history`, as the library documents; nothing of this program stands between.

## Talking to it at a terminal

`tca-agent` is the agent in Pydantic AI's own chat command line. The agent and its model are held for the whole conversation, and each prompt is a run. At the terminal the agent has every tool it has anywhere. From Python, `chat(config)` opens the same command line.

```sh
tca-agent
```

## Watching it in traces

Every run is traced by Pydantic AI's own instrumentation: a span per run, per model request and per tool call, with tokens, latency and the words. The words, every prompt, answer and tool result, are always in the spans, and nothing turns that off: whatever receives them holds application data. `tca-agent` exports its spans only when told where: `OTEL_EXPORTER_OTLP_ENDPOINT` names any OpenTelemetry collector, and `LOGFIRE_TOKEN` names Logfire. With neither, nothing leaves the process.

```sh
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 tca-agent
```

A program that runs the agent itself configures its own process once at startup, by `logfire.configure(send_to_logfire="if-token-present", console=False)`, or by running under `opentelemetry-instrument`. The repository's `compose.yaml` points the dev service at its Jaeger service, whose UI is at `http://localhost:16686`.
