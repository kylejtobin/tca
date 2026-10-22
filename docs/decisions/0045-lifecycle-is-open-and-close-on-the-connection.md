# 0045. A connection opens once at startup and closes once at shutdown, holding its client outside validation

Status: accepted

## Context

A party is reached through a client, an `httpx.AsyncClient`, that must be opened once per process and closed once, and the engine holds no state.

## Rejected

An engine class holding opened clients. A module-level client. A client parameter on `perform`. A client per call. The engine passing the connection to `perform` (0015).

## Decision

`Connection` declares `open` and `close` as abstract methods, so a connection with no library kind cannot be constructed. The library kind's `open` creates the client and holds it in a `PrivateAttr`, outside validation and outside the frozen fields; `close` closes it; `perform` reads it from `self.party`, the connection the action holds. The engine's `opened(config)` opens every connection once before its body and closes every one once after, last opened first, and when an open raises it closes what was opened before the exception propagates (0054). A server kind runs inside it, and `answer` seeds each run with the same connection instances, so every action in every answer holds an opened client.

## Evidence

On a frozen `Connection` with `_client: httpx.AsyncClient = PrivateAttr()`, `open` set the client, a field assignment was refused as `frozen_instance`, `model_dump_json` gave `{"url":"https://p.test"}` with no client, and `hash` returned an int.

## Consequences

The engine never sees a client and never passes a connection; the action holds it. Refuted by nothing.
