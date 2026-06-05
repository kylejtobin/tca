---
paths:
  - "tca/**/*.py"
---

# active model — the single live node where the graph meets time

This rule auto-loads on any concept file of a context, alongside domain.md: domain.md is the
shape of the frozen concept files, this is the shape of the one unfrozen model. The active
model's file is named for its domain concept (`catalog.py`, `feed.py`), so a glob cannot pick
it out from a frozen-model file; forge-active loads this rule for the node it owns. The shape
is derived from the Active model construct in `docs/type-construction-architecture.md`; that
document is the authority.

The active model is the single unfrozen `BaseModel` of a context, the one node where
mutable live state converges and the graph meets time. It holds transport clients (a
socket, a database, a message bus, a model client) as fields. It is exempt only from the
immutability-derived rules: it may hold those clients, receive live input, reassign
fields, and carry `-> None` methods that evolve state. There is one per context; a second
unfrozen node is illegal and means the context is two contexts.

    class FeedModel(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        socket: SocketClient
        store: StoreClient

        def ingest(self, raw: str) -> None:
            message = FeedEnvelope.model_validate_json(raw)   # construct a frozen fact
            self.store.put(message.captured.model_dump_json())  # emit an effect after proof

It is bound by **every other rule**. Its non-client fields are declared types, no bare
primitives, no `bool` gates. It never branches on a value to choose behavior: no
`if`/`elif`, no `match`; when behavior differs by variant it reads that variant's own
derivation. A mutation method's body is a sequence, its one privilege as the node that
meets time, in which each statement is a single legal operation: construct a frozen fact,
assign a constructed value, read a derivation, or emit an effect, with no value-branching
and no assembling of an untyped dict where a constructed type belongs. It receives live
input, constructs frozen facts as proof, and emits effects only after proof.

When which effect to emit depends on which variant a union holds, the effect is read off the
variant like any other behavior, never chosen by a branch. Each variant carries it as a
same-named derivation returning a typed effect description, a frozen model, and the method
hands that one value to a single uniform emit step:

    def settle(self, outcome: SettlementOutcome) -> None:
        effect = outcome.root.effect                # the variant's own effect description
        self.bus.publish(effect.model_dump_json())  # one uniform emit, no branch on which effect

The emit step is uniform because it does not inspect a set of effect kinds and pick a client
call; it runs the single typed effect it is handed. A `match` to choose the effect is the
discriminator's procedural twin, banned for the same reason as a `match` to choose a value.
When the effect's channel itself varies, one outcome mailing, another writing a row, another
calling an API, one emit step cannot select the call without that `match`; the variation
crosses instead as a domain event published uniformly here, and each consuming context
re-selects the variant by construction at its boundary and emits its own one uniform effect.

`arbitrary_types_allowed` is the active model's one sanctioned home, because holding a
live client is its privilege. The deterministic gate flags that flag wherever it appears,
because a parser cannot tell an active model from a frozen one; on a genuine active model
the flag is a true finding by construction, surfaced and confirmed downstream, not a thing
to reshape away.

**The breaks this file forbids:**
- A second unfrozen model in the context (duplicated live convergence). One per context.
- An `if`/`elif` or `match` on a value, re-dispatching what construction already selected
  (the variant's own derivation carries the behavior).
- A branch, or an emit step that inspects effect kinds, selecting which effect to emit by
  variant; the variant's own effect derivation carries it, run by one uniform emit.
- An effect emitted before the fact is constructed and proven.
- A bare primitive or a `bool` gate as a field (the immutability exemption does not extend
  to the typing rules).
