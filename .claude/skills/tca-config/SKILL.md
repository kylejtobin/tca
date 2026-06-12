---
name: tca-config
description: Build config, the only legal read of the environment. MUST be invoked before reading any environment variable or settings value. Replaces the forbidden forms; if an os.environ read, a settings dict, a dotenv parse, or a config singleton is about to appear, stop and build the config model instead.
---

# config

Config is a frozen `BaseSettings` model that constructs typed fields from the
environment, so configuration is proven the moment the program starts. The environment
is read here and nowhere else. The config root is constructed once by the composition
root (`tca-main`), frozen, and injected.

    class BusUrl(RootModel[str], frozen=True):
        root: str = Field(min_length=1)

    class NatsConfig(BaseSettings):
        model_config = SettingsConfigDict(frozen=True, extra="forbid", env_prefix="NATS_")
        url: BusUrl
        token: SecretStr   # secrets stay wrapped end to end; .get_secret_value() is
                           # read exactly once, at the client seam in the composition root

A secret is never a bare `str`: `SecretStr` keeps it out of every dump, repr, and log,
and the unwrap site is the foreign seam, the same place `.root` unwraps a scalar.

`BaseSettings` lives in the `pydantic-settings` package. When it is not installed, that
is a gap: stop, report it, and the owner adds the dependency.

## The row

The spec row this card expands. Every field a declared scalar row; the file is
`config.py`.

    {"construct": "config", "name": "AnalysisConfig", "file": "config.py", "fields": {"bus_url": "BusUrl"}}

## Allowed patterns

- one frozen `BaseSettings` model per program, `extra="forbid"`
- every field a declared scalar (`tca-scalar`)
- constructed once in the composition root and injected

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
