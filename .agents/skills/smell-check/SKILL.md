---
name: smell-check
description: "Scans Python's syntax tree, zone by zone, for the procedure LLMs write instead of modeling. Run before claiming any TCA code is done, after every file write under a domain package, and when the user says smell check, scan, or check for procedure."
---

# Smell Check

Run it:

```
.agents/skills/smell-check/smell-check src/
```

It prints one line per hit, labeled, with file and line. Exit 1 means violations exist. Exit 0 means the scan is clean. A clean scan is required before you report any TCA build complete, and it is never enough: whether the types mean the domain is the noun audit's to establish, and whether their constraints hold is the model tests'.

A file's zone is its path: under `domain/`, the domain; under `integration/`, an integration; anything else, the application, whose package `__init__.py` and `main.py` are the composition root. Files under `parser/` are not scanned. The checker admits exactly the constructions `python-dev-tca` names, in exactly their shapes: an `interpret` that stands within the one `async with` acquiring its capability and takes the library's execution controls as keyword-only arguments defaulting to `None`; a rejection predicate; `None` in a signature, or returned by an integration's property annotated `-> None`. There is no other exemption, no severity and no suppression.

## What a hit means

| Label | What you wrote | What it actually is |
|---|---|---|
| `FREE-FUNCTION` | a function outside the composition root, or a second callback in `main.py` | a meaning that should be a type |
| `MODULE-STATE` | a module-level statement other than an import, a class, a callback or `__all__`; a process's `main.py` may also bind what its startup configures, as its telemetry | state held outside a value |
| `IMPORT` | the domain importing anything but the standard library's value types, Pydantic, and the domain | the domain depending on what is outside it |
| `PARSER-IMPORT` | `from parser…` outside `integration/<system>/model.py` | a format read where no format belongs |
| `MUTABLE` | a model without `frozen=True` | a fact that can change after it was constructed |
| `LAX` | a model without `strict=True` | a type that accepts what is not its value; text is read in string mode instead |
| `PRIMITIVE` | a field typed as a primitive | a meaning with no name; a primitive is only a root |
| `HELD` | a field typed as a class that is not yours | a library's or another system's object held as a fact |
| `NONE` | `None` or `Optional` in a field or an expression | an absence with no name; the empty case is a class |
| `BODY` | a derivation, `interpret` or callback that is not one returned expression, a context it does not acquire, a step inside one | procedure inside what should be construction |
| `PARSE-METHOD` | a method, a parameter on a derivation, a positional parameter on `interpret`, a validator, `staticmethod`, `str()` | procedure hung on a type |
| `PREDICATE` | a rejection predicate not of the one shape, or reading more than `self` through `len`, `all`, `any`, `sum` and `set` | a validator disguised as an invariant |
| `ISINSTANCE` | `isinstance`, `issubclass` | a question the value answered by existing as its variant |
| `REFLECTION` | `getattr`, `setattr`, `hasattr`, `type`, `eval`, `exec`, `vars` | dispatch past the type |
| `LOOP` | `for`, `while` | a fold whose result has no name |
| `CONDITIONAL` | `if`, `match`, a ternary, `and`/`or`, a filtered comprehension | a branch; the only branch is construction choosing a variant |
| `CATCH` | `try`, `except`, `raise` | a failure handled by procedure; a refusal is a variant of the reply |
| `DICT` | a dict, `Mapping`, `TypedDict`, `JsonValue`, `model_dump`, `**` unpacking | a shape nobody proved |
| `LIST` | a list or list comprehension | a many that is not a `RootModel` over a tuple |
| `SET` | a set outside a rejection predicate | a many that is not a `RootModel` over a tuple |
| `ANY` | `Any` | a type that admits everything |
| `TYPEADAPTER` | `TypeAdapter` | validation outside a model |
| `LAMBDA` | `lambda`, `*args`, `**kwargs` | a function with no name, or an untyped parameter list |
| `JSON` | `json.loads`, `json.dumps` | parsing or building by hand |
| `BYPASS` | `model_construct`, `model_copy`, `PrivateAttr`, `cached_property`, `lru_cache`, `model_post_init`, `__init__`, `__setattr__`, `SkipValidation`, `global`, `nonlocal` | construction skipped, or state kept outside a value |

## What to do with a hit

Do not patch the line. The line is the symptom. The hit means a thing was never modeled, so go back to what the thing is and construct it. The fix for a loop is the collection and its fold. The fix for a conditional is the union. The fix for a dict is the model. The fix for a parse method is construction through annotations and aliases. The fix for a free function is the type that owns the meaning.

If the construct you need is not a page of python-dev-tca, that is a reported construction gap. Say so. It is never permission for free code.
