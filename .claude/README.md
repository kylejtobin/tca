# Claude Architecture

This directory defines how Claude Code should operate in this repository.
It is also intended to travel as part of reusable TCA project scaffolding.

It exists because the main challenge is not whether an LLM can explain Type Construction Architecture in chat. The real challenge is whether it continues to build in that mode while generating code. Left to default training, LLMs drift toward two failures:

1. procedural fallback
2. flat modeling

Procedural fallback means writing helper functions, services, mapping layers, and branching logic where stronger types should have carried the work.

Flat modeling means collapsing named domain meaning into generic shapes like `str`, `dict`, `Any`, `object`, and other loose primitives.

This `.claude/` setup exists to push against those defaults.

## Design

The architecture is rules-first and hook-driven.

The important idea is that repeating "do TCA" in more prompts is not enough. A model can describe the correct TCA approach and still emit procedural code when token generation begins. So this setup does not depend on instruction alone. It uses a feedback loop.

The pattern is:

- shared rules hold the project's reasoning frame
- agent hooks audit actual edits after generation
- prompts stay short
- duplication stays low

This keeps the cognitive frame in one place and makes every edit answer to it.

This is meant to be reusable. A good TCA project template should include both a compact root `CLAUDE.md` and a minimal `.claude/` directory like this one. The root file carries the charter. This directory carries the machinery that helps Claude actually obey it during generation.

## What Lives Here

### `rules/`

`rules/` contains the project's shared reasoning frame.

These files should capture what "correct" means in this repository at the level of architecture and structural judgment. They are not meant to be a duplicate of the full TCA docs, and they are not meant to be generic coding standards.

The current core rule names the two dominant failure modes and tells Claude what to look for in code:

- free procedure where stronger structure should exist
- flat primitive modeling where sharper domain types should exist

### `settings.json`

`settings.json` contains the hook configuration.

The current hook is a `PostToolUse` audit on `Edit|Write`. It uses an agent hook rather than a prompt hook because judging TCA drift requires reading the actual edited code, not just the hook event metadata.

The hook prompt stays short on purpose. The rules carry the frame. The hook points at the task: inspect this edit and decide whether it introduced procedural fallback or flat modeling.

## Why There Is No More Here Yet

This directory is intentionally minimal.

There is no giant `CLAUDE.md`, no large custom subagent prompt, and no pile of skills. That is deliberate. We are avoiding the same failure mode in the Claude architecture that TCA avoids in application architecture: duplication, indirection, and procedural sprawl.

If the rules are correct and the hook is placed well, that gives us the core self-correcting loop. Additional skills or subagents should only be added when they serve a distinct role that cannot be handled by shared rules plus edit auditing.

Minimal does not mean local-only. Minimal means this package can travel cleanly to other TCA repositories without bringing a pile of duplicated prompts and one-off workflow surfaces with it.

## Relationship To The TCA Docs

The TCA docs in `docs/` explain the paradigm itself.

This directory does something different. It explains and configures how Claude Code should operate under that paradigm. The docs define the architecture we believe in. `.claude/` defines the agent architecture we use to keep the model aligned with it during generation.

## Practical Standard

When extending this directory, prefer this order:

1. strengthen a shared rule
2. improve the audit hook
3. add a narrowly-scoped skill only if a reusable workflow clearly exists
4. add a subagent only if isolated specialization is genuinely needed

The default answer should be stronger shared cognition, not more surfaces.

## Reuse Standard

When starting another TCA repository, copy the minimal package first:

1. root `CLAUDE.md`
2. `.claude/rules/`
3. `.claude/settings.json`
4. `.claude/README.md`

Then adapt the project identity, local reading pointers, and any domain-specific rule content. Keep the anti-drift architecture unless the new project has a stronger proven alternative.
