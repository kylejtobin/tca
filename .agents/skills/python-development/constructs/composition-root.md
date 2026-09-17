---
type: Reference
description: Where a framework callback evaluates the per-input terminal expression. Read when registering the program boundary or wiring read and write interpreters.
---

# Composition Root

## Use

Use `main.py` as the registration site. An unexplained `prior` leaves state acquisition unmodeled; an unspecified caller leaves evaluation unmodeled. Close both edges: nest the read interpreter in the terminal expression and register its one-expression callback once. Do not count this site as a declaration form.

## Required Form

In `main.py`, construct configuration and bind the concrete client at module scope, once:

```python
config = VenueConfig()
client = PositionClient(config.url.root, config.token.get_secret_value())
```

`receive_fill` closes over this `client`. A capability bound here is not a TCA break because a capability is not a meaning; this composition-site binding is allowed, not a module-level domain value or current-state holder.

Use the application's existing framework API for this registration; do not introduce another framework or adapter:

```text
Registration: once, in main.py
Input constructor: FillRoute.receive
Callback: receive_fill
Output serializer: FillReplyRoute.emit
```

```python
def receive_fill(message: FillRoute) -> FillReplyRoute:
    return FillReplyRoute(
        recorded=PersistPositionInterpreter(
            action=Position(
                prior=ReadPositionInterpreter(
                    action=ReadPosition(
                        account=message.fill.account,
                        instrument=message.fill.instrument,
                    ),
                    client=client,
                ).execute(),
                fill=message.fill,
            ).persistence,
            client=client,
        ).execute(),
    )
```

The acknowledgement carries the position that was recorded. Pass that fact once to `FillReplyRoute`; its registered `emit` projects the two-field `FillBooked` contract. Do not stage `recorded` and `successor` as separate callback locals or publish the source fact as the reply.

- Bind configuration, the concrete client, and callback registration once at this site; follow the client's documented resource lifetime.
- Register the input constructor, callback, and output serializer explicitly; do not substitute "the framework handles it" for any binding.
- Name the terminal meaning and construct it; let its annotated dependencies construct inside the outer call.
- Pass already constructed inputs directly. Obtain externally owned prior state through the read interpreter inside the expression, not through a retained snapshot.
- Keep configuration in its declared settings model and capabilities at their concrete interpreter fields.
- Express domain dependencies in fields and owned derivations, not statement order.
- Bind the declared interpreter without class tests or a program-owned dispatch registry.
- Permit this free boundary callback only: typed input, one returned terminal expression, no local staging or domain branching.
- Use the existing terminal construct at the site; do not add a wrapper merely to represent execution.

## Do Not

- define a program-owned runner, receive loop, state-advancement loop, or multi-statement domain callback
- move orchestration into a model method, property, constructor hook, callback chain, or custom validator
- introduce a mutable consistency holder or a local/global current-state reference to re-point
- create a runner, pipeline, manager, service, graph registry, or step list
- supply domain policy through construction order, action selection, or action filtering
- execute an effect in a constructor or pretend that constructing an interpreter performs its effect
- discard a domain-relevant observed outcome; it is a fact for the next declared construction, not a flag for a runner
- leave the source of prior state or the site that evaluates the terminal expression implicit
