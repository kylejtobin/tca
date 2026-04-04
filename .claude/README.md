# Claude Architecture

This directory defines how Claude Code should operate under TCA.

It is designed to travel cleanly to any TCA project. The root `CLAUDE.md` carries the always-on charter. This directory carries the reusable machinery that helps Claude actually stay aligned while generating.

## Why This Package Exists

The main challenge is not whether an LLM can explain Type Construction Architecture in chat. The real challenge is whether it continues to build in that mode while generating code.

Left to default training, LLMs drift toward:

1. procedural fallback
2. flat modeling
3. unmodeled uncertainty expressed as strings, dicts, flags, and helper logic
4. seams, validators, or service logic growing where field declarations, aliases, discriminated unions, `from_attributes`, or projection should have carried the work

This package exists to push against those defaults without turning itself into a giant duplicated prompt surface.

The key design assumption is that Claude's own confidence is not a reliable safety mechanism. The package must repeatedly reintroduce the TCA frame during editing and before completion.

## Design

The architecture is rules-first, hook-driven, and modular.

The important idea is that repeating "do TCA" in more prompts is not enough. A model can describe the correct TCA approach and still emit procedural code when token generation begins. So this setup does not depend on instruction alone. It uses a feedback loop.

The pattern is:

- shared rules hold the reasoning frame
- a prompt-time hook reintroduces the TCA frame before generation begins
- hooks audit edits and force self-reflection before stopping
- skills stay few and role-based
- the root charter stays short
- project-local identity stays separate from universal TCA cognition

This keeps the cognitive frame in one place and makes every edit answer to it.

## What Lives Here

### `rules/`

`rules/` contains reusable TCA cognition split by concern:

- `tca-core.md` for construction-as-proof, model-as-program, and core anti-drift standards
- `tca-build-patterns.md` for the generic build path and its canonical Pydantic surfaces
- `tca-review.md` for review standards, dominant failure shapes, and preferred structural repairs

These files should capture what "correct" means at the level of architecture and structural judgment. They are not a copy of the full TCA docs and they are not generic coding standards. They should name the actual Pydantic constructs that carry proof: `RootModel`, focused `BaseModel`, `Field(...)`, `Annotated`, aliases, `Literal`, discriminated unions, `from_attributes`, `model_validate`, `model_validate_json`, `@computed_field`, `@cached_property`, and tightly justified validator modes.

### `settings.json`

`settings.json` contains the hook configuration.

The current hooks are:

- a `UserPromptSubmit` reminder that injects a short anti-procedural TCA frame into context
- a `PostToolUse` audit on `Edit|Write`
- a `Stop` self-reflection hook
- a `SubagentStop` self-reflection hook

The edit hook uses an agent hook rather than a prompt hook because judging TCA drift requires reading the actual edited code, not just the event metadata.

The hook prompts stay short on purpose. The rules carry the frame. The hooks cover three moments:

- before reasoning: inject a concise anti-procedural reminder into prompt-time context
- after edits: audit structural drift in actual code
- before stopping: force self-reflection if the answer or design drifted back toward default training

The edit and stop hooks should name the concrete failure shapes to audit for:

- free procedure
- flat modeling
- unmodeled uncertainty
- seam inflation
- validator overuse where `Field(...)`, `Annotated`, aliases, discriminated unions, `from_attributes`, or projection should carry the proof instead
- misuse of `field_validator` or `model_validator(mode="before" | "wrap" | "after")` outside legitimate irreducible seams or integrity checks

### `skills/`

`skills/` contains a very small set of reusable workflows that rules and hooks alone do not cover well.

These are not generic coding skills. They are TCA-specific workflows that recur across many projects.

They should be real Claude skills in native format:

- one directory per skill
- `SKILL.md` entrypoint
- YAML frontmatter
- descriptions written in language users naturally use before they know TCA terms
- descriptions front-loaded with the main use case, because Claude Code uses them for automatic loading and truncates long descriptions in the skill listing

If a skill is not reusable across many TCA repos, it should probably not live here.

## Why This Package Stays Small

This directory is intentionally minimal.

We are avoiding the same failure mode in the Claude architecture that TCA avoids in application architecture: duplication, indirection, and procedural sprawl.

Add surfaces in this order:

1. strengthen a shared rule
2. improve the audit hook
3. add a narrowly-scoped reusable skill
4. add repo-specific specialization only when the prior three are insufficient

The default answer should be a stronger shared TCA frame, not more surfaces.

## Relationship To The TCA Docs

The TCA docs explain the paradigm itself.

This directory does something different. It explains and configures how Claude Code should operate under that paradigm. The docs define the architecture we believe in. `.claude/` defines the agent architecture we use to keep the model aligned with it during generation.

## Adaptation Protocol

When starting another TCA repository, copy the minimal scaffold first:

1. root `CLAUDE.md`
2. `.claude/rules/`
3. `.claude/settings.json`
4. `.claude/README.md`
5. `.claude/skills/`

Then adapt it in this order:

1. rewrite `Project Identity` in the root `CLAUDE.md`
2. replace `Local Reading Pointers` with that repo's theory and example surfaces
3. keep the universal TCA anti-drift frame unless the new repo has a stronger proven alternative
4. add or sharpen project-specific rule content only when that repo has a sharper known drift than the defaults

The point is not to copy this repository's local context. The point is to copy a portable anti-drift cognitive architecture for building any TCA project.
