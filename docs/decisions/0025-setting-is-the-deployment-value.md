# 0025. A deployment value is a Setting, lenient; a business value is a Scalar, strict

Status: accepted

## Context

`Connection` and `Config` fields are read from the environment. Every environment value is text. pydantic-settings JSON-decodes a value for a complex field and validates the result in Python mode, so a strict root refuses a `float` for `Decimal` and an `int` for `timedelta`.

## Rejected

A lenient config on `Connection`: the refusal is on each `Scalar`'s own root config, so the outer config changed nothing. Restricting settings to types pydantic-settings' decoding happens to satisfy: a deployment could not set a duration or a money amount.

## Decision

`Setting[T](RootModel[T])` with `SETTING = ConfigDict(frozen=True, validate_default=True, revalidate_instances="never")`, no `strict`. A value the deployment sets is a `Setting` subclass; a value the business holds is a `Scalar` subclass. `Connection` and `Config` fields are `Setting`s. Owner decides strictness.

## Evidence

Strict `Connection` with `wait: Duration` and `fee: Amount(Scalar[Decimal])` from `PAYMENTS__WAIT=2` and `PAYMENTS__FEE=2.50`: `time_delta_type` at `("payments", "wait")`, `is_instance_of` at `("payments", "fee")`. With `Setting` roots: `Url(HttpUrl)`, `Key(SecretStr)`, `Retries(int)`, `Wait(timedelta)`, `Fee(Decimal)`, `On(bool)` all constructed from `.env`; `Retries(-1)` raised `greater_than_equal`; the same connection constructed in code from typed values. pydantic-settings 2.15.0 hands a `Setting` root the raw string: `PAYMENTS__KEY=12345` constructed `SecretStr("12345")` and `PAYMENTS__NOTE=null` constructed the string `"null"`, with and without `enable_decoding`.

## Consequences

A `Scalar` on a `Connection` or `Config` is a defect. Refuted by a deployment value that must refuse text; none exists, the environment is text.
