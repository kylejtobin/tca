# 0016. A connection with a credential is a subclass, not a union

Status: accepted

## Context

Some HTTP parties take a credential and some do not.

## Rejected

`Http(Connection)` with `key: Key | NoKey`, where `NoKey(Value)` has no fields. It puts a deployment-time choice on every page's connection, and the only way to choose `NoKey` from the environment is the variable value `{}`.

## Decision

`Http(Connection)` with `url: Url`. `Keyed(Http)` adds `key: Key`. A party is one or the other, and each party is its own `Connection` subclass, held once in the config: the proof refuses an action whose party class the config holds zero or two times.

## Evidence

With `key: Key | NoKey` on the connection and `PAYMENTS__URL` set: `PAYMENTS__KEY` absent raises `missing` at `("payments", "key")`; `PAYMENTS__KEY=` raises `too_short` at `("payments", "key", "Key")`; `PAYMENTS__KEY={}` constructs `NoKey`. With `Keyed(Http)` holding `key: Key`, `PAYMENTS__KEY=k` constructs a `SecretStr` (0019). A config with `catalog: Catalog` and `other: Catalog` was refused at proof time with "2 config fields hold Catalog, the party of Quote; exactly one must".

## Consequences

Unwritable: `NoKey`, a union on a connection field. Refuted by a party whose credential is optional at one address; that is two connections.
