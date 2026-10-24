# AGENTS.md

This repository is Type Construction Architecture (TCA): a developer declares a business as Pydantic types, and a framework carries those declarations through events, time and failure.

The old request runtime has been removed. Its replacement is not built. Most of the architecture below is a target, not behavior that exists.

## Source documents

- `docs/TCA_ARCHITECTURAL_FOUNDATIONS.md` is the target architecture. Its proposals are not verified decisions.
- `docs/REFACTOR_ACCEPTANCE.md` holds the behavioral acceptance requirements for the replacement. They are requirements, not implemented tests. Never report one as met without naming the executed test.
- `TODO.md` lists what is not done, in order.
- `README.md` states what exists today.

## Decision records and review authority

Only Kyle's designated independent Codex reviewer may create, modify, delete, rename or supersede files under `docs/decisions/**`. Implementing agents, including Claude, must not edit those files or delegate such edits. Being a Codex implementation agent does not grant reviewer authority. Do not change this rule or create competing authoritative records elsewhere.

Read [0003](docs/decisions/0003-construction-evidence-and-justified-execution.md) and [0004](docs/decisions/0004-review-authority-and-outcome-evidence.md). They bind architectural behavior and acceptance. Implementers may submit evidence-backed proposals in their handoff, but may not weaken requirements or mark TODO outcomes complete. Routine implementation and experiments within the contract should proceed without a documentation approval detour.

## Architectural principles

- Business types remain the declarative program.
- Apply the seven preservation laws in [0003](docs/decisions/0003-construction-evidence-and-justified-execution.md#laws-every-implementation-must-preserve): effect justification, no authority from ignorance, compositional meaning, scoped constraints, retained distinctions, useful safe progress, and semantics-preserving infrastructure. Passing an example does not waive these laws.
- Application scenarios exercise generic framework semantics. They must not become engine-specific branches or subsystems.
- An invocation's lifetime is independent of requests, connections, coroutines and worker attempts.
- Evaluation, external execution, durable recording, evidence admission and interface projection have separate responsibilities. Do not merge them to save a layer.
- The retained primitives in `packages/python/type-construction-world` are reusable components. They are not a commitment to the previous engine or its public API.

## Teardown and what follows

- During cleanup, remove the specified machinery and do not build its replacement.
- During later implementation, do not restore deleted abstractions to satisfy old APIs, tests or documentation. The previous implementation is in Git history for reference only.
- The designated reviewer records architectural decisions and explicit supersession. Implementers provide executable evidence and proposals without editing decision records. Do not rewrite history to imply a decision was always current.

## Tests and typing

- Test meaningful business behavior and failure boundaries independently of implementation helpers.
- Keep strict typing and native Pydantic value semantics. A checker rejection is not by itself a business requirement. Decide what the data means before narrowing a type to satisfy the checker.
- Testing Pydantic behavior does not establish distributed recovery, correlation or concurrency correctness.

## Reporting

Keep three kinds of claim apart:

- **Source inspection:** what you read in the code or documents.
- **Executed tests:** what you ran, with the recipe and its result.
- **Unverified proposals:** what is designed or required but not demonstrated.

Lead with what is not done and why.

## Checks

Use the `just` recipes. They are the ones CI and the commit hook run.

```
just check    # ruff check, ruff format --check, basedpyright strict, bandit, pytest
just audit    # lockfile, pip-audit, semgrep, image-pin check
just build    # build the development image
just lock     # re-resolve the lockfile in the container
just shell    # shell in the development container
```

Targeted test recipe, from the repository root:

```
uv run pytest packages/python/type-construction-world/tests/type_construction_world/test_computed.py -q
```

Run `git`, `just`, `uv` and `docker` as the bare command, not behind `cd`, `&&` or a pipe, because the sandbox rules match the command as typed.

## Commits

Fill in `.gitmessage`: the intended change, the reason, and the verification run. Name the relevant architecture section or acceptance requirement when one applies. Architectural proposals and their evidence belong in the implementation handoff; only the designated reviewer writes the decision record.
