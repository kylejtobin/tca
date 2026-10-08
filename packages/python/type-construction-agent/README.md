# type-construction-agent

Type Construction Architecture's agent: a Pydantic AI agent that models a domain as types.

```python
from type_construction.agent import Prompt, run, run_sync

answer = await run(Prompt(text="Model a checkout domain."))
answer.text.root

answer = run_sync(Prompt(text="Model a checkout domain."))
```

The agent's prompt is `prompts/agents/tca-agent.md`. The skills it may load when a task needs them are in `prompts/skills/` (`python-dev-tca`, `docker-infra-tca`, `smell-check`), which the repo's `.agents/skills/` links to; it reads their pages read-only.

The deployment names its provider and model, and the provider's credentials, in the environment:

| Provider | Variables |
|---|---|
| any | `TCA_AGENT_PROVIDER` (`openai`, `anthropic`, `azure`, `aws`, `cloudflare`), `TCA_AGENT_MODEL` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Azure | `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY` |
| AWS (Bedrock) | `AWS_DEFAULT_REGION`, and `AWS_ACCESS_KEY_ID` with `AWS_SECRET_ACCESS_KEY` (and `AWS_SESSION_TOKEN` for a temporary key), or `AWS_BEARER_TOKEN_BEDROCK` |
| Cloudflare (Workers AI) | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |
