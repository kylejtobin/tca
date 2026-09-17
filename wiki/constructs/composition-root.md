---
type: Construct
description: The site where a framework callback evaluates the per-input terminal expression.
---

# Composition Root

## Definition

`main.py` is the registration site, not a declaration form. The pointer to the last successor has nothing to prove, so it has no type, and the in-memory copy of it would duplicate the fact the ledger holds. So there is no runner, no receive loop, and no current-state local. The framework owns the stream; the program owns one expression per input, and that expression nests the read of prior state so that state acquisition and evaluation are both modeled.

## Required Form

In `main.py`, configuration constructs and the concrete client binds at module scope, once:

```python
config = VenueConfig()
client = PositionClient(config.url.root, config.token.get_secret_value())
```

`receive_fill` closes over this `client`. A capability bound here is not a break, because a capability is not a meaning; this is the composition-site binding, not a module-level domain value or current-state holder.

Registration uses the application's existing framework API:

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

The read executes because the successor's construction depends on its outcome; the dependency graph determines order, and no statement sequences it. The acknowledgement carries the position that was recorded, so the reply route holds one fact once and its registered `emit` projects the two-field contract.

- Configuration, the concrete client, and callback registration bind once at this site, following the client's documented resource lifetime.
- The input constructor, callback, and output serializer register explicitly; "the framework handles it" substitutes for no binding.
- The terminal meaning is named and constructed; its annotated dependencies construct inside the outer call. Already constructed inputs pass directly.
- Externally owned prior state arrives through the read interpreter inside the expression, never through a retained snapshot.
- The declared interpreter binds without class tests or a dispatch registry. A fact with several effect families exposes each as its own derivation, and each binds to its own interpreter.
- This free boundary callback is the only admitted free function: typed input, one returned terminal expression, no local staging or domain branching.

## Forbidden

- a program-owned runner, receive loop, state-advancement loop, or multi-statement domain callback
- orchestration moved into a model method, property, constructor hook, callback chain, or custom validator
- a mutable consistency holder or a local or global current-state reference to re-point
- a runner, pipeline, manager, service, graph registry, or step list
- domain policy supplied through construction order, action selection, or action filtering
- an effect executed in a constructor, or constructing an interpreter mistaken for performing its effect
- a domain-relevant observed outcome discarded; it is a fact for the next declared construction, not a flag for a runner
- the source of prior state or the site that evaluates the terminal expression left implicit
