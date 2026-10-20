---
name: smell-check
description: "Scans Python's syntax tree for the procedure LLMs write instead of modeling. Run before claiming any TCA code is done, after every file write under a program, and when the user says smell check, scan, or check for procedure."
---

# Smell Check

Run it:

```
.agents/skills/smell-check/smell-check <program src>...
```

It prints one line per hit, labeled, with file and line. Exit 1 means violations exist. Exit 0 means the scan is clean. A clean scan is required before you report any TCA build complete, and it is never enough: whether the types mean the domain is the noun list's to establish, and whether their constraints hold is the model tests'.

The checker admits exactly what `tca-python-dev` names: classes that subclass a kind of the world; fields typed as the program's own classes; derivations, an `effect`, an `open`, a `stream` and a rejection predicate, each one returned expression; a module of imports, classes, `__all__` and a `Route`. There is no zone, no exemption, no severity and no suppression. The engine is not scanned: it is the one place procedure exists.

## What a hit means

| Label | What you wrote | What it actually is |
|---|---|---|
| `BASE` | a class that does not subclass a kind of the world, or one of your own classes | a class that is not one of the kinds |
| `ENGINE` | an import from `type_construction.engine` other than `.parties` | a program reaching into the engine; it imports the world and the engine's parties |
| `FREE-FUNCTION` | a function at module level | a meaning that should be a type |
| `MODULE-STATE` | a module-level statement other than an import, a class, `__all__` or a `Route`; in `main.py`, other than the one call that serves the config | state held outside a value |
| `PRIMITIVE` | a field typed as a primitive | a meaning with no name; a primitive is only a root |
| `HELD` | a field typed as a class that is not yours | a library's or another party's object held as a fact |
| `NONE` | `None` or `Optional` in a field or an expression | an absence with no name; the empty case is a class |
| `BODY` | a derivation, `effect`, `open` or `stream` that is not one returned expression, a `with`, a step inside one | procedure inside what should be construction |
| `PARSE-METHOD` | any other method, a parameter beside `self` on a property or `open`, a default, a validator, `staticmethod`, `str()` | procedure hung on a type |
| `PREDICATE` | a rejection predicate not of the one shape, or reading more than `self` through `len`, `all`, `any`, `sum` and `set` | a validator disguised as an invariant |
| `ISINSTANCE` | `isinstance`, `issubclass` | a question the value answered by existing as its variant |
| `REFLECTION` | `getattr`, `setattr`, `hasattr`, `type`, `eval`, `exec`, `vars` | dispatch past the type |
| `LOOP` | `for`, `while` | a fold whose result has no name |
| `CONDITIONAL` | `if`, `match`, a ternary, `and`/`or`, a filtered comprehension | a branch; the only branch is construction choosing a variant |
| `CATCH` | `try`, `except`, `raise` | a failure handled by procedure; a refusal is a variant of the reply |
| `DICT` | a dict, `Mapping`, `TypedDict`, `JsonValue`, `model_dump`, `**` unpacking | a shape nobody proved |
| `LIST` | a list or list comprehension | a many that is not a `Many` over a tuple |
| `SET` | a set outside a rejection predicate | a many that is not a `Many` over a tuple |
| `ANY` | `Any` | a type that admits everything |
| `TYPEADAPTER` | `TypeAdapter` | validation outside a model |
| `LAMBDA` | `lambda`, `*args`, `**kwargs` | a function with no name, or an untyped parameter list |
| `JSON` | `json.loads`, `json.dumps` | parsing or building by hand |
| `BYPASS` | `model_construct`, `model_copy`, `PrivateAttr`, `cached_property`, `lru_cache`, `model_post_init`, `__init__`, `__setattr__`, `SkipValidation`, `global`, `nonlocal` | construction skipped, or state kept outside a value |

## What to do with a hit

Do not patch the line. The line is the symptom. The hit means a thing was never modeled, so go back to what the thing is and construct it. The fix for a loop is the collection and its fold. The fix for a conditional is the union. The fix for a dict is the model. The fix for a parse method is construction through annotations and aliases. The fix for a free function is the type that owns the meaning. A hit is never permission for free code.
