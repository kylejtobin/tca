---
type: construct
---

# Config

## Definition

A frozen `BaseSettings` model, the only structure that reads environment values. Every field is a declared scalar or secret type, and it is constructed once by the composition root and injected.

## Required form

```python
class VenueUrl(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class PositionConfig(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="forbid", env_prefix="VENUE_")
    url: VenueUrl
    token: SecretStr
```

## Secrets

A secret is never a bare `str`: `SecretStr` keeps it out of every dump, repr, and log. `get_secret_value()` is called exactly once, at client instantiation in the composition root.

`BaseSettings` lives in the `pydantic-settings` package; if it is not installed, that is a gap to report, not a reason to read the environment directly.

## Sorting

- Environment values → this construct.
- A configured value used in the domain → carried as its declared [semantic scalar](semantic-scalar.md), never re-read from the environment.
- Client instantiation from config values → the [composition root](composition-root.md).
- A value that is domain state rather than environment fact → the [consistency model](consistency-model.md).
- Program placement → lives in `config.py`; see [topology](topology.md).

## Allowed

- one frozen `BaseSettings` model per program with `SettingsConfigDict(frozen=True, extra="forbid")`
- an `env_prefix` naming the program's environment namespace
- every field a declared scalar or `SecretStr`
- constructed once in the composition root and injected

## Forbidden

- an `os.environ` read anywhere
- a settings dict or config singleton
- a secret typed as bare `str`
- `get_secret_value()` outside the composition root
