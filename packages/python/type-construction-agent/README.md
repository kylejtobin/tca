# type-construction-agent

Type Construction Architecture's agent: a Pydantic AI agent that models a domain as types, and the reference for an agent under TCA.

```python
from type_construction.agent import AgentConfig, Opening, PromptText, answer_sync

reply = answer_sync(AgentConfig(), Opening(text=PromptText("Model a checkout domain.")))
print(reply.answer.text.root)
```

A caller holds a conversation; Pydantic AI performs runs. Every public name says which it hands you: `answer`, `follow_up` and a `Reply` are the conversation's, `run` and an `AgentRunResult` are the library's. In an async program, `await answer(config, prompt)` returns the same `Reply`, and `await run(config, prompt)` returns Pydantic AI's own `AgentRunResult[Answer]`, the answer with every message, the usage and the run's id; a graph or any other async caller uses these, never `answer_sync`, which starts its own event loop. A `FollowUp` crosses the same three ways, as `follow_up`, `follow_up_sync` and `run_follow_up`. All six take three optional keyword arguments, Pydantic AI's own execution resources: `usage`, a `RunUsage` the run accumulates into; `cancellation_token`, a `CancellationToken` the caller owns, which when cancelled raises Pydantic AI's `RunCancelled` and stays cancelled; and `toolsets`, a sequence of Pydantic AI's toolsets this one run may call beside the agent's own, as a program that orchestrates the agent hands it its own.

The agent is the library's object that holds this program's callbacks, so the interpreter that answers a prompt composes it for each crossing, as a server's app is composed from its routes: from the model the deployment names, the answer's type, the agent's provider's one derivation, the library's capability that is everything else the agent is, the workspace as the run's boundary, the file and shell tools inside it, the skills, the history, the check's schema and the prompt, and `CheckInterpreter` as its `check` tool. Its tools are Pydantic AI's file and shell tools, its skills, and `check`. The check interpreter holds the check and the workspace reached as a shell inside its boundary, a provider constructed from the workspace the deployment named; it runs the executable named `check` the workspace declares at its root and reads what came back once into `CheckResult`: `Clean` or `Failed` by the exit, each with its exit and everything the check said; the model sees that type's schema. The loop in the agent's instructions calls it after every file, and a failed check is not done. The agent carries the tool from construction, so every run has it, the terminal and a program that drives the interpreter itself included.

A prompt is the words a person gives: an `Opening`, which starts an exchange, or a `FollowUp`, which continues one after a reply, named by the run that produced it; each is its own action, answered by its own interpreter. An `Answer` is the words the agent gives back, and Pydantic AI constructs it as the agent's structured output: an answer that does not validate as one is sent back to the model, and one the model cannot form is refused with Pydantic AI's own `UnexpectedModelBehavior`. A `Reply` is the answer with the id Pydantic AI gave the run, `run`, after which a follow-up continues. Its instructions are `prompts/agents/tca-agent.md`. It works in the workspace the deployment names, and loads its skills from that directory's `.agents/skills`.

## Configuring it

A deployment names three things: the model; the workspace the agent models in, with the boundary it runs in; and the SQLite file its runs are recorded in, which defaults to `tca-agent.sqlite` where the program runs. It may also set the share of the model's context window a conversation fills before it is compacted, seven tenths unless named. The workspace and the history are providers whose one derivation is a library capability, each reached a second way by a provider constructed from it, the workspace as a shell and the history as a store, and the agent's provider holds all three and derives the one capability the agent is built with. Beyond these the agent has no setting of its own: Pydantic AI's own defaults govern a run, its request limit, its timeouts and how hard the model thinks, and the named provider reads its credentials and endpoint from its own variables. The agent's settings are read under `TCA_` from the process environment or from a `.env` file in its working directory, the environment winning; a key another system owns in that file is left to it, and a setting the agent does not have is refused.

The workspace is not the directory the program runs in. It holds the skills under `.agents/skills`, its check as an executable named `check` at its root, and the work, and nothing else: the agent reads and runs whatever is in it, and what it reads enters the model's context and its traces, so a key never lives there. Its kind is the boundary, as Pydantic AI draws it: `local` is the library's local workspace, which isolates nothing; `sandbox` is that workspace in the library's bubblewrap sandbox, where every command sees the host read-only, has no network, and writes only inside the directory. The sandbox needs `bwrap` on the machine. The check must exit zero only when the work is clean, and in a sandbox must write nothing outside the directory, so a linter's cache goes inside it or nowhere. A workspace that does not exist is refused on the first run with Pydantic AI's own `WorkspaceUnavailableError`.

| Variable | Holds |
|---|---|
| `TCA_AGENT__MODEL` | A model as Pydantic AI names it, its provider first: `anthropic:claude-opus-5-5`, `openai-chat:gpt-5`, `bedrock:…`; `test` is Pydantic AI's own offline model. |
| `TCA_AGENT__WORKSPACE__KIND` | The workspace's boundary: `local` or `sandbox`. |
| `TCA_AGENT__WORKSPACE__PATH` | The directory the agent models in. |
| `TCA_AGENT__HISTORY__DATABASE` | The SQLite file the agent's runs are recorded in; `tca-agent.sqlite` when unset. |
| `TCA_AGENT__COMPACTION` | The share of the model's context window a conversation may fill before Pydantic AI compacts it, above zero and at most one; `0.7` when unset. |
| the provider's own | `ANTHROPIC_API_KEY`; `OPENAI_API_KEY`, and `OPENAI_BASE_URL` for a model an OpenAI-compatible endpoint serves, as `openai-chat:@cf/zai-org/glm-5.3-flash` at Workers AI; `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY`; `AWS_DEFAULT_REGION` with an AWS access key, session or bearer token. |

A model Pydantic AI does not know, or one whose credentials are missing, is refused on the first run with Pydantic AI's own `UserError`, saying what to set.

## Testing it offline

`TCA_AGENT__MODEL=test` runs the agent on Pydantic AI's `TestModel`, with no credentials. A test that scripts the model's replies hands Pydantic AI its own `FunctionModel` or `TestModel` wherever the library would infer that name, by `monkeypatch.setattr(pydantic_ai.models, "infer_model", …)`; the package's tests show it.

## Seeing what a run did

`run(config, prompt)` and `run_follow_up(config, prompt)` return Pydantic AI's own `AgentRunResult[Answer]`: the answer as `output`, every message, the usage and the run's id. `OpeningInterpreter(action=prompt, provider=config.agent).interpret()` returns the same, as does `FollowUpInterpreter` for a follow-up; beside `usage`, `cancellation_token` and `toolsets`, it takes `event_stream_handler`, to which Pydantic AI streams the run's events as they happen, every part, tool call and tool result, while the run still holds its model; a handler that raises stops the run, and the model is released all the same.

## Remembering its runs

Every run is recorded by Pydantic AI's own step persistence in the SQLite file the deployment names, made when it is missing and used when it is there: the run under the id Pydantic AI gave it, which its reply carries as `run`, with the agent's name beside it; each model request and tool call as an event; and a continuable snapshot of the run's messages. A follow-up after that reply is answered after everything the run recorded, read back by the library's own `continue_run` and handed to the next run as its `message_history`, in this process or any later one that names the same file; the run inherits the conversation's id, and Pydantic AI records it as the conversation's next run. Nothing of this program stands between: the id the reply carries, the key the file records under and the run in the traces are one. A follow-up after a run the file does not hold is refused with Python's `LookupError`, as Pydantic AI raises it.

```python
from type_construction.agent import (
    AgentConfig,
    FollowUp,
    Opening,
    PromptText,
    answer_sync,
    follow_up_sync,
)

config = AgentConfig()
first = answer_sync(config, Opening(text=PromptText("Model a coin toss.")))
second = follow_up_sync(config, FollowUp(text=PromptText("Now a die."), after=first.run))
print(second.answer.text.root)
```

## Keeping a long conversation within the window

A conversation never dies on the model's context limit. Before each request, Pydantic AI Harness's tiered compaction measures the history against the window of the model the request goes to, resolved from the model itself, and when it fills more than the named share, seven tenths unless the deployment says otherwise, compacts it down to that share: the oldest tool results are cleared first, which costs nothing and reclaims what usually fills a modeling run, and only if that is not enough are the older messages summarized by the same model behind a recent tail. What is compacted stays compacted in the run's history and in the snapshot the file records, so a follow-up continues from the compacted conversation. Nothing of this program is in the way: the tiers, the measuring and the summary are the library's.

## Talking to it at a terminal

`tca-agent` is the agent in Pydantic AI's own chat command line. The agent is held for the whole conversation, and each prompt is a run. At the terminal the agent has every tool it has anywhere, `check` included. From Python, `chat(config)` opens the same command line.

```sh
tca-agent
```

## Watching it in traces

Every run is traced by Pydantic AI's own instrumentation: a span per run, per model request and per tool call, with tokens, latency and the words. The words, every prompt, answer and tool result, are always in the spans, and nothing turns that off: whatever receives them holds application data. `tca-agent` exports its spans only when told where: `OTEL_EXPORTER_OTLP_ENDPOINT` names any OpenTelemetry collector, and `LOGFIRE_TOKEN` names Logfire. With neither, nothing leaves the process.

```sh
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 tca-agent
```

A program that runs the agent itself configures its own process once at startup, by `logfire.configure(send_to_logfire="if-token-present", console=False)`, or by running under `opentelemetry-instrument`. The repository's `compose.yaml` points the dev service at its Jaeger service, whose UI is at `http://localhost:16686`.
