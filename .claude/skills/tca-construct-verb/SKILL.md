---
name: tca-construct-verb
description: Build a verb, the only legal state transition on the consistency model. MUST be invoked before writing any method on the consistency model. Replaces the forbidden forms; if a fetch-and-return method, a multi-step body, a staged construction chain, serialization inside a method, or a method the catalog does not declare is about to appear, stop and build the verb instead.
---
# Verb

## Definition

A state-transition method on the consistency model. Its parameter is the innermost constructed value it consumes; its body contains at most one construction statement, with constituents constructing inside that call; it may capture a foreign reply before the construction, re-point a state field to the constructed fact, and emit the constructed fact through a client field.

## Required Form

```python
    def book(self, report: VenueFill) -> None:
        self.latest = Position(prior=self.latest, fill=report)
        self.bus.publish(self.latest)
        self.ledger.append(self.latest)
```

`Position.fill` is typed `Fill`, so the `Fill` constructs from the `VenueFill` inside the `Position` construction call. The state field is the constructed value's only name, and every emit passes the proven value itself; serialization happens at the client binding or the route reply, never here.

A yielding verb yields constructed facts:

```python
    async def watch(self, account: AccountId) -> AsyncIterator[Fill]:
        async for report in self.feed.subscribe(account):
            yield Fill.model_validate(report)
```

A capturing verb feeds the ordered union's constructor:

```python
    async def reconcile(self, account: AccountId) -> None:
        try:
            raw: object = await self.ledger.position(account)
        except PositionNotFoundError as signal:
            raw = signal
        self.recorded = LedgerReplyConstructor.validate_python(raw)
```

## Sorting Rules

A fact implied by already-proven fields is a derivation, not a verb. A method that only retrieves and returns is not a verb; consumers read facts that transitions establish. Construction of the request shape belongs to the route; the verb receives the innermost value, never a transport wrapper.

## Replaced Forms

A multi-step body staging constructions in sequence is the work stolen from a constructor: a constituent constructed in a separate statement before the composite that holds it restates what the composite's call proves. A fetch-and-return method is a repository surface given a verb's name. Serialization in the body is the transport's concern restated in the domain.

## Verb Body

The body contains at most one construction statement; constituent values construct inside that one call. It may also: capture a foreign reply before the construction (one call assigned, each declared exception assigned to the same variable), assign the constructed fact to a state field, and emit the constructed fact through a client field. An effect is never emitted before the fact is constructed. A verb that constructs nothing, emits nothing, and yields nothing declares no transition.

## The Row

```json
{"construct": "verb", "name": "book", "file": "position.py", "on": "PositionConsistencyModel", "accepts": "VenueFill", "constructs": "Position", "emits": ["Position"]}
{"construct": "verb", "name": "watch", "file": "position.py", "on": "PositionConsistencyModel", "accepts": "AccountId", "yields": "Fill"}
{"construct": "verb", "name": "reconcile", "file": "position.py", "on": "PositionConsistencyModel", "accepts": "AccountId", "captures": {"signals": ["PositionNotFoundError"], "into": "LedgerReply"}, "state": "recorded"}
```

A capturing verb adds `captures`: `signals` lists the declared exception types the client call may raise, and `into` names the ordered-union row the captured value constructs; `state` names the consistency-model field the result is assigned. `on` names the consistency model row, and the verb lives in that model's file. `accepts` is the innermost row the verb consumes. `constructs` names at most one row, the single construction the body performs. `emits` lists rows whose proven values pass through client fields. `yields` and `returns` are mutually exclusive; a verb with `returns` must also declare `constructs`, because the return is read from the constructed fact. A verb declaring none of `constructs`, `emits`, or `yields` is refused. An unmodeled method on the consistency model is denied at the write, and a modeled verb missing from the class is a violation.

## Allowed Patterns

- `-> None` transition: at most one construction, a state-field assignment, emits of the proven fact
- the capture before the construction, exactly the three-line form, feeding the ordered union's constructor
- a yielding verb constructing and yielding one fact per arrival
- a returning verb whose return is read from the fact its body constructs

## Forbidden

- more than one construction statement in a body
- a constituent constructed in a separate statement before its composite
- `model_dump`, `model_dump_json`, or `.root` in the body
- a parameter holding a transport wrapper
- a method that only retrieves and returns
- `match`, `if`/`elif`, or `isinstance` in the body
- a hand-assembled dict where a constructed type belongs
- a stub body: `raise NotImplementedError`, bare `...`, or `pass`

## Halt Rule

Halt when the transition needs a second construction statement, a computation no derivation carries, a branch, or a parameter only available as a transport wrapper. Report the row and the statement that will not fit: the composite, the derivation, or the route's unwrap is missing from the table, and the table is not finished.
