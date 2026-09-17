---
type: Reference
description: How environment and deployment input constructs frozen typed configuration. Read when adding settings, environment variables, defaults, or secrets.
---

# Config

## Use

Use for deployment values. Environment input is text; applying strict Python numeric construction to that text rejects the representation before it can become a configuration fact. Use lax settings construction, not manual conversion.

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

- Construct each independently deployed configuration once at its boundary; reuse that immutable fact in dependent constructions.
- Type every non-secret field as a semantic scalar or value object.
- Set `strict=False` only for settings input. Retain declared output types, field constraints, freezing, `extra="forbid"`, and validated defaults; lax input is not lax meaning.
- Use `SecretStr` for credentials and reveal it only while constructing the concrete client that consumes it.
- Put source names in settings aliases or `env_prefix`.
- Validate every default and make its omission meaning explicit.
- Inject the constructed config or the capability constructed from it; never re-read the environment.

## Do Not

- call `os.environ` outside `BaseSettings`
- use a settings dictionary, global singleton accessor, or module-level primitive in place of the settings model; the [composition root](composition-root.md) binds the constructed model and client once at module scope
- type a secret as `str`
- log, serialize, derive, or return a revealed secret
- mix deployment input with mutable runtime state
- copy domain `strict=True` into settings or spread settings' laxness into domain models
- compensate for textual input with a parser, validator, or field-copying conversion
