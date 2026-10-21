# 0011. Instant and Identity construct themselves

Status: accepted

## Context

A fact that concludes at a moment, or that identifies a thing, declares a field for it, and the value does not exist before the fact does.

## Rejected

An engine step that supplies the moment and the identity when constructing a fact. A `__init_subclass__` on `Fact` that installs a default factory per field. A memo keyed by type, which gave every `Identity` in a run the same value.

## Decision

`Instant.root` has `default_factory=lambda: datetime.now(UTC)`. `Identity.root` has `default_factory=uuid4`. A fact declaring `at: Instant` constructs with no value given, and two holders never share one.

## Evidence

`Placed(order=PlaceOrder(quantity=1))` with `at: Instant` and `id: Identity` declared constructs; `at.root` is a `datetime`, `id.root` is a `UUID`; the required fields of `Placed` are `["order"]`. `Placed(order=..., at="now")` raises `ValidationError`.

## Consequences

The engine does not supply time or identity. Refuted by a moment that must come from outside the process; that is a field of the arrival.
