# 0014. An unused generic parameter distinguishes nothing

Status: accepted

## Context

A record class, since removed (0012), was parameterized by the party, `Unreachable[P: Connection](Record)`, so that a field typed `Unreachable[Payments]` would refuse an instance made for the catalog.

## Decision

A generic parameter that no field uses does not constrain validation. A parameter that must distinguish instances is held by a field.

## Evidence

With no field typed `P`: `Unpaid(unreachable=Unreachable[Catalog](failure=...))` constructed for a field typed `Unreachable[Payments]`. `Unreachable[Payments] is not Unreachable[Catalog]` was `True` and their metadata args differed, and validation still accepted the instance. With `party: P` added: the same call raised `model_type` at `("unreachable", "party")`, and `Unreachable[Payments](party=catalog, ...)` raised `model_type`.

## Consequences

Every generic parameter on a kind is read from a field or from a library kind's `perform`. `Action[P, T]` is read by the library kind, not by validation. Refuted by nothing.
