---
name: smell-check
description: Scans Python for the five procedural patterns that LLMs write instead of modeling (free function, isinstance, loop, conditional, dict) and the parse methods hung on models. Run before claiming any TCA code is done, after every file write under a domain package, and when the user says "smell check", "scan", or "check for procedure".
---

# Smell Check

Run it:

```
.agents/skills/smell-check/smell-check src/
```

It prints one line per hit, labeled, with file and line. Exit 1 means violations exist. Exit 0 means the scan is clean. A clean scan is required before you report any TCA build complete. Do not report completion with a nonzero exit.

## What a hit means

Every hit is a violation. There is no severity, no "edge work", no "serialization", no "just a helper". Those words are how procedural code rationalizes itself. The patterns below are the procedural style, and in TCA they are forbidden by the python-development skill.

| Label | What you wrote | What it actually is |
|---|---|---|
| FREE-FUNCTION | a `def` at module level | a meaning that should be a type. The only admitted free function is the framework callback in `main.py`; a second `def` in `main.py` is a free function and fails. |
| ISINSTANCE | `isinstance(x, T)` | a question the value already answered by existing as its variant. Behavior that differs by variant is a same-named property on each variant. |
| LOOP | `for` or `while` | a fold whose result has no name. A fold is a comprehension inside the one returned expression of a derivation, with no `if`. |
| CONDITIONAL | `if`, `elif`, `else`, `match`, `case`, ternary | a branch. The only branch in TCA is Pydantic construction choosing a union variant. Zero conditionals in a domain package, not "fewer". |
| DICT | `dict[...]`, `dict(...)`, `{...}`, `JsonValue`, `Json[...]` | a shape nobody proved. A violation. See DICT hits. |
| PARSE-METHOD | a method with parameters beyond `self`, a `staticmethod`, a validator, a `str()` call | procedure hung on a model. A derivation takes only `self` and its body is exactly one returned expression. A parameterized question is a frozen model holding its inputs. A validator is a procedure where a representation belongs. |

## What to do with a hit

Do not patch the line. The line is the symptom. The hit means a thing was never modeled, so go back to what the thing is and construct it. The fix for a loop is the collection and its fold. The fix for a conditional is the union. The fix for a dict is the model. The fix for a parse method is construction through annotations and aliases. The fix for a free function is the type that owns the meaning.

If the construct you need is not on the whitelist, that is a reported construction gap. Say so. It is never permission for free code.

## DICT hits

Every DICT hit is a violation. Fix the model.

The one exception is a case table: a dict literal whose keys are every member of one `StrEnum` or `Literal`, indexed directly. The script recognizes that shape, a literal whose every key is `Enum.MEMBER` followed by `[`, and prints it as `CASE-TABLE` without failing. Whether every member is present is not visible on the line; that is the judge's question. Any other dict is `DICT` and a violation.
