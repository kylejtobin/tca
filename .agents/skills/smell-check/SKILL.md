---
name: smell-check
description: "Five line patterns that mark procedure on a TCA page: a method, a validator, a weakened type, reflection, a branch or a bare primitive. Run before claiming any page is done; it runs in `just check` and in pre-commit."
---

# Smell Check

```
.agents/skills/smell-check/smell-check <program src>...
```

Per hit, `LABEL file:line: text` and beneath it the type to write instead, specific to what matched: the field name and primitive, the keyword, the function. Exit 1 on any hit. It is a line scan; a docstring is scanned too, so a page's docstrings say what a thing is and hold no code.

| label | pattern | what to write instead |
|---|---|---|
| `METHOD` | `def` not directly under `@property` or `@computed_field` | a class, a `@property` on an action, a `@computed_field` |
| `VALIDATOR` | `model_validator`, `field_validator`, `AfterValidator`, `BeforeValidator`, `WrapValidator`, `PlainValidator` | a `Scalar` constraint or a union member |
| `WEAKENED` | `Any`, `cast(`, `# type: ignore`, `object` as a type | the type the checker refused to accept |
| `REFLECTION` | `lambda`, `getattr`, `setattr`, `hasattr`, `vars(`, `isinstance`, `issubclass`, `create_model`, `TypeAdapter`, `**` unpacking | a field, a union, a generic parameter |
| `PROCEDURE` | a line starting with `if`, `for`, `while`, `try`, `except`, `raise`; `None` anywhere | a union, a tuple, `ValidationError` propagating, a class for the absent case |
| `PRIMITIVE` | a field annotated `str`, `int`, `float`, `bool`, `bytes`, `Decimal`, `datetime`, `date`, `UUID`, `timedelta`; `root:` is exempt | a `Scalar` subclass |

