# 0047. An action holds its party as a field, and hears its record through the engine

Status: accepted

## Context

An action is performed against the connection the deployment configured for its party `P`, and its response is validated as `T`. The engine must find both, and only Pydantic's generic metadata names them.

## Rejected

`perform(self, party: P)` with the engine reading `P` out of the parametrization and passing the connection. A record `Parametrization` validated from the metadata to replace the asserts. A phantom field typed `T` so Pydantic would resolve it. A library kind's `perform` validating the response itself, which needs `type[T]` at run time, which Pydantic does not give a generic instance.

## Decision

`Action[P, T]` declares `party: P`. The engine seeds the run with the deployment's connections under their classes, so the action constructs when the fact that intends it and its party both exist, like any other class, and `perform(self)` reads `self.party`. `T` is read once, in the proof, by `heard`, which binds each parametrized base's arguments through the parameters of the base before it down the MRO until it reaches `Action`. `hear(action, text)` is the engine's function a library kind's `perform` returns: it validates the party's JSON text as the action's record and narrows it to `T` with a `TypeIs` guard, so `perform` type-checks with no cast.

## Evidence

`class Quote(Says[Catalog, Price])` gave `Quote.model_fields["party"].annotation is Catalog` through the library kind, and `class Charge(Post[Payments, Price, Charged])` gave `Payments`. `heard(Quote)` returned `Price` and `heard(Charge)` returned `Charged` through `Post`'s three parameters. `Says.perform` written as `return hear(self, self.party.says.root)` type-checked under basedpyright strict against `-> T`. The shop's two answers performed through it.

## Consequences

A library kind never reads metadata; it holds `self.party` and returns `hear(self, text)`. The world's `Action` has one field, and a page never writes it. Refuted by a transport whose response is not text; then `hear` gains a sibling that validates a tree.
