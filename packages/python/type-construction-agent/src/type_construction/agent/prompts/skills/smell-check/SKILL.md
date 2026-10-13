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

Every hit is a violation. There is no severity, no "edge work", no "serialization", no "just a helper". Those words are how procedural code rationalizes itself. The patterns below are the procedural style, and in TCA they are forbidden by the python-dev-tca skill.

| Label | What you wrote | What it actually is |
|---|---|---|
| FREE-FUNCTION | a `def` at module level | a meaning that should be a type. The only admitted free functions are a composition root's callbacks: the one framework callback in `main.py`, where a second `def` fails, and one per public function in a package's `__init__.py`. |
| ISINSTANCE | `isinstance(x, T)` | a question the value already answered by existing as its variant. Behavior that differs by variant is a same-named property on each variant. |
| LOOP | `for` or `while` | a fold whose result has no name. A fold is a comprehension inside the one returned expression of a derivation, with no `if`. |
| CONDITIONAL | `if`, `elif`, `else`, `match`, `case`, ternary | a branch. The only branch in TCA is Pydantic construction choosing a union variant. Zero conditionals in a domain package, not "fewer". |
| DICT | `dict[...]`, `dict(...)`, `{...}`, `JsonValue`, `Json[...]`, `Mapping`, `MutableMapping`, `OrderedDict`, `defaultdict`, `TypedDict`, `ChainMap` | a shape nobody proved. A violation. See DICT hits. |
| PARSE-METHOD | a method with parameters beyond `self`, a `staticmethod`, a validator, a `str()` call | procedure hung on a model. A derivation takes only `self` and its body is exactly one returned expression. A parameterized question is a frozen model holding its inputs. A validator is a procedure where a representation belongs. |
| CATCH | `try`, `except`, `finally`, `raise`, `raise_for_status` | a failure handled by procedure. Nothing is caught and the program raises nothing; a refusal is a variant of the reply. |
| NONE | `\| None`, `Optional[...]` | an absence with no name. The empty case is a class. |
| LAMBDA | `lambda`, `*args`, `**kwargs` | a function with no name, or an untyped parameter list. |
| LIST, SET, ANY, TYPEADAPTER | `list`, `[...]`, `set`, `frozenset`, `Any`, `TypeAdapter` | a shape that is not one of your classes. A many is a `RootModel` over a tuple; a union is a `RootModel` over its variants. |
| JSON | `json.loads(`, `json.dumps(` | parsing or building by hand. Raw text goes to a constructor; a model serialises itself. |
| PARSER-IMPORT | `from parser…` outside `integration/<system>/model.py` | a format read where no format belongs. Only a foreign model annotates its records with a format type. |
| BYPASS | `model_construct`, `model_copy(`, `PrivateAttr`, `cached_property`, `lru_cache`, `object.__setattr__`, `model_post_init`, `def __init__(`, `SkipValidation`, `global`, `nonlocal` | construction skipped or mutated, or state kept outside a value. |

Files under `parser/` are not scanned. Only a format type lives there.

## What to do with a hit

Do not patch the line. The line is the symptom. The hit means a thing was never modeled, so go back to what the thing is and construct it. The fix for a loop is the collection and its fold. The fix for a conditional is the union. The fix for a dict is the model. The fix for a parse method is construction through annotations and aliases. The fix for a free function is the type that owns the meaning.

If the construct you need is not a page of python-dev-tca, that is a reported construction gap. Say so. It is never permission for free code.

## DICT hits

Every DICT hit is a violation. Fix the model.
