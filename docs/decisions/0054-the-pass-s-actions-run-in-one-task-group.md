# 0054. The pass's actions run in one task group, a client's exception propagates in a group, and a connection that fails to open closes what opened

Status: accepted

## Context

The pass's actions ran under `asyncio.gather`: the first exception propagated and the other actions ran on unawaited, so a failed pass left tasks the run no longer owned. `opened` opened every connection before its `try`, so a later open that raised left the earlier ones open. Retry, timeout, idempotency and compensation had no stated owner.

## Rejected

`gather(return_exceptions=True)`, which hides the failure in the result. Retry or timeout in the engine. Compensation of effects already performed; the engine has no model of what undoing an effect means.

## Decision

The actions of a pass, across the parent run and its children, are created as tasks in one `asyncio.TaskGroup`. One action's exception cancels the group's other actions and propagates out of `answer` as the `ExceptionGroup` the task group raised; an action cancelled mid-flight may have had its effect, and its span ends without a record. Effects already performed in earlier passes stand. The engine never retries, times out or compensates: delivery guarantees are the library kind's and the connection's, and an idempotency key a party needs is a field on the action, supplied by the program and sent by the kind. `opened` opens each connection in field order and, when one raises, closes those already opened in reverse before the exception propagates. The command line prints each `ValidationError` in a group and exits 1 when the group holds nothing else; any other group propagates.

## Evidence

The engine's test program with its party raising `ConnectionError` on every `perform`, two elements: `answer` raised an `ExceptionGroup` whose exceptions were two `ConnectionError`. A config of a party that opens and one whose `open` raises `ConnectionError` logged `open:Fine`, `open:Down`, `close:Fine`, and `opened` raised the `ConnectionError`.

## Consequences

A transport's failure reaches the caller as its own exception, grouped with the pass's others. Refuted by nothing.
