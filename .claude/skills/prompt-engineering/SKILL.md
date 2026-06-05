---
name: prompt-engineering
description: Use when writing or revising any prompt for a Claude model — a system prompt, a CLAUDE.md, a subagent or skill definition, an API prompt, or a prompt embedded in code — and when diagnosing why a prompt underperforms (ignored instructions, wrong verbosity or tone, over/under tool use, overthinking, persona drift, a constraint that keeps getting re-litigated). Also use when choosing effort or thinking settings for a Claude call.
---

The full guide lives beside this file at
`.claude/skills/prompt-engineering/prompt-engineering-guide.md`. It is the working
authority on how the current Claude models actually behave. This SKILL.md is the map to
it, not a summary of it — the findings live in the guide, and a recommendation rests on
the guide section it came from, not on recall.

## How to work

Open the guide section that fits the situation before recommending, and cite it so the
reasoning can be checked against the source. Recall of "what the guide probably says" is
how the last rebuild of this skill failed: it produced generic prompt-engineering
instinct instead of the guide's actual findings, because the guide was never read. The
map below makes the read cheap; the citation requirement makes it load-bearing.

Select the levers that fit the case rather than applying many. The guardrail usually
matters more than the technique — "most tasks need none of this" is itself the most
common correct answer, especially for identity and persona scaffolding. When evidence is
thin, say so: small samples, single-model results, high variance. Weigh a finding by
what it has earned on real prompts, not by where it sits — a project finding that proved
out can outrank an external result, even a published one, even one written into the
guide. "This is already right, change nothing" is a complete answer.

## Precedence

`What this project has learned` (the guide's first section) holds findings earned in practice and
**wins on conflict** with the Anthropic-derived baseline below it. Its entry bar is that
a claim predicted or fixed a real failure at least once; a claim that stops paying off
gets cut. Read it first when a question touches persistence, identity, or how to weigh a
piece of evidence — and treat the baseline sections as corroboration under it, not as
equal authority.

## Map to the guide

Each entry is *when to go there and the claim you'll find*. Headings match the guide.

### Project findings (read first, outranks the rest)
- **What this project has learned** — the four earned findings: persistence amplifies
  whatever you encode including what you meant to suppress; heavy identity scaffolding is
  for long contested sessions only; memory/hydration is a persistence vector you can't
  see in the prompt; weigh evidence by what it earned. The mechanism, not the
  literature, is load-bearing.

### Opus 4.8 model behavior (`Prompting Claude Opus 4.8`)
Reach here when tuning behavior of the current top model.
- **Response length and verbosity** — calibrates length to perceived complexity; tune
  with positive concision examples, not "don't" rules.
- **Calibrating effort and thinking depth** — the effort ladder (max/xhigh/high/medium/
  low), when each fits, and how to steer adaptive thinking on/off. Start here for any
  "it's too shallow / too slow / over-thinking" question.
- **Tool use triggering** — favors reasoning over tool calls; raise effort or describe
  when/why to use a tool rather than commanding it.
- **User-facing progress updates** — remove old "summarize every N calls" scaffolding;
  describe the update you want with an example instead.
- **More literal instruction following** — the model does not infer unstated scope, so
  state it ("every section, not just the first"); and it reads instructions about
  *itself* literally, so naming a topic to suppress it raises that topic's salience.
- **Tone and writing style** — direct, low-validation default; re-spec voice if your
  product needs warmth.
- **Controlling subagent spawning** — spawns fewer by default; give explicit when-to-fan-out guidance.
- **Design and frontend defaults** — the cream/serif/terracotta house style and why it's
  wrong for dashboards/fintech/dev-tools; the two reliable fixes (specify a concrete
  alternative, or have it propose directions first). Generic "don't use cream" just
  shifts it to another fixed palette.
- **Interactive coding products** — front-load task/intent/constraints in turn one;
  reduce required user turns; use xhigh/high.
- **Code review harnesses** — "be conservative / only high-severity" now suppresses real
  findings; prompt for coverage at the finding stage and filter separately.
- **Computer use** — resolution guidance; 1080p is the performance/cost sweet spot.

### Foundational levers (`General principles`)
Reach here for the technique that fits a need, and the scope guardrail on it.
- **Be clear and direct** — specificity and the colleague test; ask for "above and
  beyond" explicitly rather than hoping it's inferred.
- **Add context to improve performance** — give the motivation behind an instruction;
  **stating a fact outperforms issuing a rule**, because a bare imperative invites the
  model to relitigate it. The root of the disposition-over-imperative principle.
- **Use examples effectively** — 3–5 relevant, diverse, `<example>`-tagged shots; the
  highest-leverage steer for format/tone/structure.
- **Structure prompts with XML tags** — tag distinct content types so load-bearing
  instructions are distinguishable from context and input.
- **Give Claude a role** — one sentence suffices for bounded tasks; for long/adversarial
  ones, *how* you encode the role beats *how much* — points to the next section.
- **Encode durable traits as dispositions, not imperatives** — **the core section for
  CLAUDE.md / system-prompt / persona work.** When it applies (only when a trait must
  survive many turns, pushback, or context windows — most prompts need none of it) and
  the two mechanisms: salience (forceful writing raises a topic's prominence even when
  suppressing it) and stance-vs-behavior (instructions about the model's posture leak as
  self-justification; instructions about output comply cleanly). Has the imperative→fact
  before/after, and the inverse-trait trap: a suppression persona persists *harder* over
  a session. Go here for relitigation, persona drift, and "why did my 'never do X' make X
  worse."
- **Long context prompting** — 20k+ token inputs: data at top, XML-structured documents,
  quote-first grounding.
- **Model self-knowledge** — prompt strings to make Claude identify its model / pick a
  model string.

### Output and formatting (`Output and formatting`)
- **Communication style and verbosity** — concise/direct default; ask for post-tool
  summaries if you want visibility.
- **Control the format of responses** — positive over negative; XML format indicators;
  match prompt style to desired output; the full anti-markdown/anti-bullets snippet.
- **LaTeX output** — the snippet to force plain-text math.
- **Document creation** — prompt shape for decks/visual docs.
- **Migrating away from prefilled responses** — prefill on the last assistant turn is
  unsupported on 4.6+; per-scenario migrations (formatting→structured outputs, preamble,
  refusals, continuations, and **context hydration → system prompt as the durable home
  for identity**).

### Tool use (`Tool use`)
- **Tool usage** — explicit "make the change" beats "can you suggest"; the
  default_to_action / do_not_act_before_instructions snippets; and the **don't-over-prompt
  rule** — dial back "CRITICAL: you MUST," it over-triggers and the same applies to
  persona framing.
- **Optimize parallel tool calling** — the parallel-calls snippet, and how to dial it
  down.

### Thinking and reasoning (`Thinking and reasoning`)
- **Overthinking and excessive thoroughness** — replace blanket "default to X" with
  targeted triggers; lower effort as the fallback; the commit-to-an-approach snippet.
- **Leverage thinking & interleaved thinking capabilities** — adaptive thinking, guiding
  reflection after tool results, multishot `<thinking>` examples, self-check; the
  budget_tokens→effort migration.

### Agentic systems (`Agentic systems`)
Reach here for multi-turn, multi-window, or delegated work.
- **Long-horizon reasoning and state tracking** — incremental-progress discipline; the
  **Persona and disposition persistence** paragraph (system prompt survives compaction;
  audit memory/hydration for traits you don't want amplified).
- **Context awareness and multi-window workflows** — token-budget awareness; the
  don't-stop-early / save-state-before-refresh snippet.
- **Multi-context window workflows** — first-window-vs-later, tests.json, init.sh,
  fresh-start-vs-compaction, spend-the-whole-context.
- **State management best practices** — structured state vs freeform notes vs git.
- **Balancing autonomy and safety** — confirmation gates for destructive/irreversible/
  shared-system actions.
- **Research and information gathering** — success criteria, source verification, the
  competing-hypotheses structured-research snippet.
- **Subagent orchestration** — delegates well unprompted; watch overuse; the when-to-use-
  subagents guidance.
- **Chain complex prompts** — when explicit chaining still earns its place; the
  draft→review→refine self-correction pattern.
- **Reduce file creation in agentic coding** — the clean-up-temp-files snippet.
- **Overeagerness** — the anti-over-engineering snippet (scope, docs, defensive coding,
  abstractions).

### Capability-specific (`Capability-specific tips`)
- **Improved vision capabilities** — multi-image/extraction; the crop-tool uplift.
- **Frontend design** — the AI-slop problem and the frontend_aesthetics snippet
  (typography, color, motion, backgrounds).

### Migration (`Migration considerations`)
- **Migration considerations** — the 4.6 upgrade checklist; #6 ties anti-laziness tuning
  to persona over-defense.
- **Migrating from Claude Sonnet 4.5 to Claude Sonnet 4.6** — Sonnet 4.6 effort defaults,
  when to reach for Opus 4.8, and the thinking/budget_tokens migrations.
