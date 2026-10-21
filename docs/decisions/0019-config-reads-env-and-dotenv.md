# 0019. Config reads the environment and .env

Status: accepted

## Context

A deployment sets connections through environment variables; a developer's checkout sets them in a file.

## Decision

`Config(BaseSettings)` with `SettingsConfigDict(**PRODUCT, env_nested_delimiter="__", env_file=".env")`. Nested fields are read as `PAYMENTS__URL`. The command line carries only the request; connections come from the environment for every server kind.

## Evidence

With `.env` containing `PAYMENTS__URL=https://p.test` and `PAYMENTS__KEY=k`, `ShopConfig()` constructed `payments.url.root` as `https://p.test/` and `payments.key.root` as a `SecretStr`. `SettingsConfigDict(**PRODUCT, ...)` passed basedpyright strict; `ConfigDict(**PRODUCT, validate_by_name=True, ...)` for `Record` did not, so `Record`'s config is written out in full.

## Consequences

A missing variable fails at startup naming the field. Refuted by a deployment that cannot set environment variables; that is a settings source added to `Config`, which pydantic-settings supports.
