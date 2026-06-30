---
name: tca_authorized_construct_consistency_model
description: Build the consistency model, the single legal home for live clients and mutable state. MUST be invoked before holding any socket, database, bus, or client, and before declaring any mutable field. Replaces the forbidden forms; if a manager, an engine, a second unfrozen model, a module-level client, or a class sequencing domain work is about to appear, stop and build the consistency model instead.
---
# Consistency Model

## Definition

The single unfrozen `BaseModel` of a context, the one node where live clients and mutable state converge. Every state it holds is a proven fact, and state evolution is a field re-pointing to a newer proven value.

## Required Form

```python
PositionState = Annotated[Position | Flat, Field(discriminator="kind")]


class PositionConsistencyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bus: BusClient
    ledger: LedgerClient
    latest: PositionState

    def book(self, report: VenueFill) -> None:
        self.latest = Position(prior=self.latest, fill=report)
        self.bus.publish(self.latest)
        self.ledger.append(self.latest)
```

`PositionState` is the state union: `Position` and `Flat` are the concept models declared in their own sections, each carrying the same-named `exposure` derivation, so exposure reads off `latest` with no branch. Clients are fields, state fields are declared types, and every method is a verb. `arbitrary_types_allowed` is legal on this class and nowhere else.

## Sorting Rules

A second unfrozen model means the context is two contexts: stop and report it. Client binding belongs to the binding; the consistency model receives constructed clients as fields. A fact the state implies is a derivation on the state's model, not a method here. A frozen domain composite is a concept model.

## Replaced Forms

A manager or engine is domain logic with a technology name and no proof obligation. A module-level client is the live edge escaped from the one node that may hold it. A second unfrozen model is a second convergence point for state, which is two contexts fused into one.

## Construct-Specific Doctrine

State evolution is reassignment of proofs, never mutation of their contents: construct the newer proven fact and re-point the field to it. The consistency model never holds an unproven value, not even for one statement. Every non-client field is a declared type; no bare primitives, no `T | None`, no `bool` gates. Selection never happens here: construction selected the variant, the checker narrows it, and what differs by variant is read from the union value.

## Allowed Patterns

- one unfrozen `BaseModel` per context with `arbitrary_types_allowed=True`, clients as fields
- every non-client field a declared type holding a proven value
- state evolution by re-pointing a field to a newly constructed fact
- verbs as the only methods

## Forbidden

- a second unfrozen model in one context
- a module-level client
- `match`, `if`/`elif`, or `isinstance` anywhere in the class
- a hand-assembled dict where a constructed type belongs
- an unproven or unmodeled value held in any field
- `arbitrary_types_allowed` on any other class

## Halt Rule

Halt when a context needs a second unfrozen model, when a client no verb reaches is demanded, or when a state field has no declared row. Report the row and the field or client: the context is mis-factored or the meaning is unmodeled, and the table is not finished.
