# TODO

Not built, in order. The design for each is in `docs/decisions/`; the developer's side is `.agents/skills/tca-python-dev/SKILL.md`.

## Now

Usage: add one entry per task below this paragraph, in the shape of the schema, numbered in order. Set the status to `Not Done` when written, `Delivered for review` when the work is in, and `Done` when it is reconciled. When every entry is `Done`, delete the entries and leave this paragraph and the schema.

Schema:

```markdown
### Task <N>: <Title> - <Not Done | Delivered for review | Done>

**<One sentence: what to derive or build, and the constraint on how.>**

- <One checkable requirement per bullet.>

**Outcome:** <The observable result that makes the task done.>
```

## Next

1. Bind the feature files with pytest-bdd, so every scenario in `packages/python/*/tests/features/*.feature` and `tests/features/smell_check.feature` runs as a test. Step definitions live in each package's `tests/`, one module per feature file, with a parametrized step for each sentence shape that repeats, such as "ValidationError is raised with type {type} at loc {loc}". Add `pytest-bdd` to the dev group. Order of work: `scalar.feature` and `kinds.feature`, which need only the world; the other world features and `smell_check.feature`; then `engine.feature`; then `cli.feature`.

## Later

1. The HTTP kind (0015, 0016, 0023, 0045): `Http`, `Keyed`, `Post`, `Get` with `perform(self)` sending through the `httpx.AsyncClient` held in `self.party`'s `PrivateAttr` and returning `hear(self, response.text)`; one FastAPI path operation per route with `Q` as the body and `answered.reply` as the response, served inside `opened`; the standard OpenTelemetry instrumentations for httpx and FastAPI. Its scenarios in the http package's `tests/features/`, with httpx's `MockTransport` as the party.

