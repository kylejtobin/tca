---
type: Playbook
description: The scan that finds the five procedural patterns LLMs write instead of modeling, required to pass before any TCA Python build is reported complete.
generated: { by: claude-code/claude-fable-5-1, at: 2026-10-01T00:00:00Z }
---

# Smell Check

The `smell-check` skill at `.agents/skills/smell-check/` is a ripgrep scan over Python for the five patterns that procedural code is made of. Every hit is a violation. Exit 1 means violations exist. Exit 0 is required before any build is reported complete.

```
.agents/skills/smell-check/smell-check src/
```

## Why these five

An LLM's default is procedural: get the input, parse it, check which case, build the result, with types added afterward as labels on the data moving through those steps. Under pressure it reaches for a helper function, a dict, `isinstance`, a parse step, or a loop because those feel like competent Python, and it rationalizes them as edge work or serialization. Each one is control flow holding what should be a value. The scan is grep rather than judgment so it cannot be argued with.

## The patterns

| Label | What was written | What it is |
|---|---|---|
| FREE-FUNCTION | a `def` at module level | a meaning that should be a type. The only admitted free function is the framework callback in `main.py`; a second `def` in `main.py` is a free function and fails. |
| ISINSTANCE | `isinstance(x, T)` | a question the value already answered by existing as its variant. Behavior that differs by variant is a same-named property on each variant. |
| LOOP | `for` or `while` | a fold whose result has no name. A fold is a comprehension inside the one returned expression of a derivation, with no `if`. |
| CONDITIONAL | `if`, `elif`, `else`, `match`, `case`, ternary, filtered comprehension | a branch. The only branch in TCA is Pydantic construction choosing a union variant. Zero conditionals in a domain package. |
| DICT | `dict[...]`, `dict(...)`, `{...}`, `JsonValue`, `Json[...]` | a shape nobody proved. A violation. |
| PARSE-METHOD | a method with parameters beyond `self`, a `staticmethod`, a validator, a `str()` call | procedure hung on a model. A derivation takes only `self` and its body is exactly one returned expression. |

## DICT hits

Every DICT hit is a violation. Fix the model.

The one exception is a case table: a dict literal whose keys are every member of one `StrEnum` or `Literal`, indexed directly. The script recognizes that shape, a literal whose every key is `Enum.MEMBER` followed by `[`, and prints it as `CASE-TABLE` without failing. Whether every member is present is not visible on the line; that is the judge's question. Any other dict is `DICT` and a violation. The case table is the [transformation](../constructs/transformation.md) algebra's total function on a closed vocabulary; it exists so that a derivation from an enum member has a branch-free form.

## What a hit means

Do not patch the line. The hit means a thing was never modeled. Go back to what the thing is and construct it. A construct not on the whitelist is a reported construction gap, never permission for free code. No exclusion is added to the script to silence a hit.
