---
type: construct
---

# Binding

## Definition

The class whose `connect` method binds transport clients to the consistency model. Its entire meaning is the binding it performs: it owns no domain type, holds no domain logic, and makes no domain decision.

## Required form

```python
class PositionBinding:
    def connect(self, bus: BusClient, ledger: LedgerClient, opening: PositionState) -> PositionConsistencyModel:
        return PositionConsistencyModel(bus=bus, ledger=ledger, latest=opening)
```

## Transport setup

- `connect` may perform transport setup whose signal has no domain meaning: connection, authentication, subscription, and the idempotent create-or-bind that binds the same client either way.
- A transport signal the domain reacts to is modeled through the [ordered union](ordered-union.md), never caught here.

## Replaced forms

- A repository is a fetch surface given a class name; consumers read facts the consistency model's transitions establish.
- A computing service is domain logic that escaped the consistency model.
- A manager is sequencing the construction graph already owns.

## Sorting

- Domain state and domain transitions → [consistency model](consistency-model.md); the binding only constructs it.
- Client instantiation and configuration → [composition root](composition-root.md); the binding receives constructed clients.
- Transport ingress → [route](route.md); the binding handles no request.
- Program placement → lives in `service/<context>.py`; see [topology](topology.md).

## Allowed

- one class whose `connect` accepts constructed transport clients and any opening state, and returns the constructed consistency model
- connection, authentication, and subscription setup inside `connect`

## Forbidden

- a method that computes a domain fact
- a catch that converts a transport signal into a domain answer
- a domain type defined in the binding's file
- a repository, manager, or computing service
