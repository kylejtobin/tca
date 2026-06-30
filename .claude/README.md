# The TCA Build System

This `.claude/` directory holds the human-directed build loop for Type Construction Architecture. The main agent never writes code. It turns a need into a validated construction Plan, decides where each construct lives, and dispatches narrow build agents that each make one construct from its card. Construction is proven before code is written, and building is constrained, card-driven assembly rather than freehand generation.

## The Loop

1. The operator states a need.
2. The main agent dispatches the **plan agent**, which models the need as a `Plan`: a typed worksheet of construct entries, one meaning per entry, selecting only whitelist constructs from the construct cards. The `tca_construction_plan` tool, served by the MCP server, validates the submitted worksheet into a proven Plan at the boundary; an entry that is not a legal construct fails there.
3. The main agent decides file targets (a construct's layer follows from its kind) and any context the plan does not carry.
4. The main agent dispatches **build agents**, one construct type per agent, per file. Each build agent reads its construct's card and makes exactly that one construct in that one file, refusing more than a single type. Types sharing a file are dispatched serially.
5. The operator verifies the result: `uv run basedpyright` and `uv run pytest` green, and the built constructs match the plan.

Subagents cannot spawn subagents. Completion is never an agent's assertion; it is the passing type check, the passing tests, and the constructs matching the plan.

## Agents

- [`agents/plan-agent.md`](agents/plan-agent.md): turns a need into a validated `Plan` through the construction-plan tool, selecting constructs only from the cards and reporting a gap when no construct carries a meaning. It writes no code and runs nothing.
- [`agents/build-agent.md`](agents/build-agent.md): takes one construct entry and a target file, reads that construct's card, and makes exactly that one construct. It refuses more than a single type and leaves an unrelated red linter alone.
- [`agents/tca-llm-content.md`](agents/tca-llm-content.md): edits LLM-facing text while preserving doctrine, rules, construct boundaries, and detection cues.

The main agent's frame is [`../CLAUDE.md`](../CLAUDE.md). It dispatches the agents, decides file targets, runs proofs, and escalates only what the record cannot settle. It does not write code.

## Authority Boundaries

- **Human operator** decides product judgment, doctrine changes, irreversible actions, and final acceptance.
- **Main agent** dispatches, decides file targets, runs proofs, and escalates what the record cannot settle. It writes no `.py` under `src/`; its only lever on code is dispatch.
- **Plan agent** owns the construction Plan. It selects constructs from the cards, reports a gap rather than inventing one, and writes no code.
- **Build agent** makes one construct of one type in one file, strictly to its card. It makes no design decisions and refuses anything broader.

## Construct Cards

The constructs are the constraint surface, served by the MCP server, one card per construct. The fifteen `tca_authorized_construct_*` cards carry each construct's required form and the shapes it forbids; the `tca_forbidden_pattern_*` cards are the detection cues; the `tca_required_reference_*` cards carry the topology, the vocabulary, and the documentation strategy. The plan agent selects a construct and reads its card to model an entry; the build agent reads the same card to make the construct to its required form. The `Plan` worksheet itself is modeled in `src/app/domain/construction/plan.py`, and the `tca_construction_plan` tool validates a submitted worksheet into a proven Plan.
