# 0015. An action hears one record; perform is abstract on Action and the library kind implements it

Status: accepted

## Context

An action sends something to a party and hears something back. The engine must know what it hears; the transport must know what it sends and where.

## Rejected

Finding the payload and the path by scanning an action's computed fields for a return type of `Record` or `Resource`. The checker cannot verify that such a field exists. `perform(self, party: P)` with the engine choosing the connection (0047).

## Decision

`Action[P: Connection, T: Record]` declares `party: P` and `perform(self) -> T` as an `@abstractmethod`. A library kind adds its parameters, declares its verb's inputs as abstract properties, `Post[P, S, T]` with `sends -> S` and `resource -> Resource`, `Get[P, T]` with `resource`, and implements `perform`, which sends through `self.party` and returns `hear(self, text)` (0047), or raises. A page implements the properties as plain properties. Pydantic's metaclass is an `ABCMeta`, so an action with no library kind cannot be constructed. Exactly one action hears each `Record` class, and the proof refuses a second as `hearer`.

## Evidence

`class Says[P: Speaker, T: Record](Action[P, T])` with `perform` returning `hear(self, self.party.says.root)` type-checked; `class Quote(Says[Catalog, Price])` holding `line: Line` was constructed by the run once its line and its catalog existed and performed. A direct `Action[Catalog, Price]` subclass with no `perform` raises `TypeError: Can't instantiate abstract class`. A second class hearing `Price` was refused at startup: "2 actions hear Price: Quote, Requote; exactly one must".

## Consequences

Unwritable: a payload found by return type; a `perform` that takes the party. `sends` and `resource` are plain properties, not computed fields, because an action is performed, not serialized. Refuted by a library kind that sends two things in one call; that is two actions.
