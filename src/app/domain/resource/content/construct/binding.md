---
name: tca_authorized_construct_binding
description: Build a binding, the only legal connection between transport clients and the consistency model. MUST be invoked before writing any connect, setup, or wiring class, and before catching any transport-setup signal. Replaces the forbidden forms; if a repository, a manager, a computing service, or a class holding domain logic is about to appear, stop and build the binding instead.
---
# Binding

## Definition

The class whose `connect` method binds transport clients to the consistency model. Its entire meaning is the binding it performs: it owns no domain type, holds no domain logic, and makes no domain decision.

## Required Form

```python
class PositionBinding:
    def connect(self, bus: BusClient, ledger: LedgerClient, opening: PositionState) -> PositionConsistencyModel:
        return PositionConsistencyModel(bus=bus, ledger=ledger, latest=opening)
```

## Sorting Rules

Domain state and domain transitions belong to the consistency model; the binding only constructs it. Client instantiation and configuration belong to the composition root; the binding receives constructed clients. Transport ingress belongs to the route; the binding handles no request.

## Replaced Forms

A repository is a fetch surface given a class name; consumers read facts the consistency model's transitions establish. A computing service is domain logic that escaped the consistency model. A manager is sequencing the construction graph already owns.

## Construct-Specific Doctrine

`connect` may perform transport setup whose signal has no domain meaning: connection, authentication, subscription, and the idempotent create-or-bind that binds the same client either way. If the domain reacts to a transport signal, the signal is modeled through the ordered union, never caught here.

## Allowed Patterns

- one class whose `connect` accepts constructed transport clients and any opening state, and returns the constructed consistency model
- connection, authentication, and subscription setup inside `connect`

## Forbidden

- a method that computes a domain fact
- a catch that converts a transport signal into a domain answer
- a domain type defined in the binding's file
- a repository, manager, or computing service

## Halt Rule

Halt when `connect` would need a domain decision, a domain computation, or a catch the domain reacts to. Report the row and the signal as a modeling gap: the meaning belongs in the consistency model or the ordered union, and the table is not finished.
