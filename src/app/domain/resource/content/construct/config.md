---
name: tca_authorized_construct_config
description: Build config, the only legal read of the environment. MUST be invoked before reading any environment variable or settings value. Replaces the forbidden forms; if an os.environ read, a settings dict, a dotenv parse, or a config singleton is about to appear, stop and build the config model instead.
---
# Config

## Definition

A frozen `BaseSettings` model, the only structure that reads environment values. Every field is a declared scalar or secret type, and it is constructed once by the composition root and injected.

## Required Form

```python
class VenueUrl(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class PositionConfig(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="forbid", env_prefix="VENUE_")
    url: VenueUrl
    token: SecretStr
```

## Sorting Rules

A configured value used in the domain is carried as its declared scalar, never re-read from the environment. Client instantiation from config values belongs to the composition root. A value that is domain state rather than environment fact belongs on the consistency model.

## Replaced Forms

An `os.environ` read scatters the environment through the program; config proves it once at startup. A settings dict carries unproven values; a config singleton hides the read behind import order.

## Construct-Specific Doctrine

A secret is never a bare `str`: `SecretStr` keeps it out of every dump, repr, and log. `get_secret_value()` is called exactly once, at client instantiation in the composition root.

`BaseSettings` lives in the `pydantic-settings` package; if it is not installed, that is a gap to report, not a reason to read the environment directly.

## Allowed Patterns

- one frozen `BaseSettings` model per program with `SettingsConfigDict(frozen=True, extra="forbid")`
- an `env_prefix` naming the program's environment namespace
- every field a declared scalar or `SecretStr`
- constructed once in the composition root and injected

## Forbidden

- an `os.environ` read anywhere
- a settings dict or config singleton
- a secret typed as bare `str`
- `get_secret_value()` outside the composition root

## Halt Rule

Halt when an environment value has no declared scalar or secret type to land in, or when `pydantic-settings` is absent. Report the row and the value: the environment fact is not yet modeled, and the table is not finished.
