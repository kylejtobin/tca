---
type: Construct
description: Environment input constructed once into a frozen settings model, lax on input because the environment is text.
---

# Config

## Definition

Deployment values, constructed once from the environment into a frozen `BaseSettings` model. Environment input is text; strict numeric construction on that text rejects the representation before it can become a configuration fact, so settings construct lax. Lax input is not lax meaning: output types, constraints, freezing, and validated defaults are retained.

The package declaring this construct declares `pydantic-settings>=2,<3` beside its Pydantic dependency.

## Required Form

```python
class VenueConfig(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="VENUE_",
    )
    url: VenueUrl
    token: SecretStr
```

- Each independently deployed configuration constructs once at its boundary and is reused as an immutable fact in dependent constructions.
- Every non-secret field is a semantic scalar or value object.
- `SecretStr` holds credentials and is revealed only while constructing the concrete client that consumes it, at the [composition-root site](./composition-root.md).
- Source names live in settings aliases or `env_prefix`.
- Every default is validated and its omission meaning is explicit.
- The constructed config, or the capability constructed from it, is injected; the environment is never re-read.

## Forbidden

- `os.environ` read outside `BaseSettings`
- a settings dictionary, global singleton accessor, or module-level primitive in place of the settings model
- a secret typed as `str`
- a revealed secret logged, serialized, derived, or returned
- deployment input mixed with mutable runtime state
- domain `strict=True` copied into settings, or settings' laxness spread into domain models
- textual input compensated by a parser, validator, or field-copying conversion
