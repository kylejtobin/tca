# 0015. An action holds its party, hears one record, and performs through its library kind

Status: accepted

## Context

An action sends something to a party and hears something back. The engine must find the connection the deployment configured for the party and must know what the action hears; the transport must know what it sends and where. Only Pydantic's generic metadata names `P` and `T`, and Pydantic gives a generic instance no `type[T]` at run time.

## Rejected

Finding the payload and the path by scanning an action's computed fields for a return type of `Record` or `Resource`: the checker cannot verify that such a field exists. `perform(self, party: P)` with the engine reading `P` out of the parametrization and passing the connection. A record `Parametrization` validated from the metadata in place of asserts. A phantom field typed `T` so that Pydantic would resolve it. A library kind's `perform` validating the response itself, which needs `type[T]` and ends in a cast.

## Decision

`Action[P: Connection, T: Record]` declares `party: P` and `perform(self) -> T` as an `@abstractmethod`. The engine seeds the run with the deployment's connections under their classes, so the action constructs when the fact that intends it and its party both exist, like any other class, and `perform` sends through `self.party`. A library kind adds its parameters, declares its verb's inputs as abstract properties, `Post[P, S, T]` with `sends -> S` and `resource -> Resource`, `Get[P, T]` with `resource`, and implements `perform` as `return hear(self, text)`, where `hear` is the engine's function that validates the party's JSON text as the action's record and narrows it to `T` with a `TypeIs` guard. `T` is read once, in the proof, by `heard`, which binds each parametrized base's arguments through the parameters of the base before it, down the MRO to `Action`. Pydantic's metaclass is an `ABCMeta`, so an action with no library kind cannot be constructed. Exactly one action hears each `Record` class, and the proof refuses a second as `hearer`.

## Evidence

`class Quote(Says[Catalog, Price])` gave `Quote.model_fields["party"].annotation is Catalog` through the library kind, and `class Charge(Post[Payments, Price, Charged])` gave `Payments`. `heard(Quote)` returned `Price` and `heard(Charge)` returned `Charged` through `Post`'s three parameters. `Says.perform` written as `return hear(self, self.party.says.root)` type-checked under basedpyright strict against `-> T`, and the shop's answers performed through it. A direct `Action[Catalog, Price]` subclass with no `perform` raises `TypeError: Can't instantiate abstract class`. A second class hearing `Price` was refused at startup: "2 actions hear Price: Quote, Requote; exactly one must".

## Consequences

Unwritable: a payload found by return type; a `perform` that takes the party; a library kind that reads metadata. `sends` and `resource` are plain properties, not computed fields, because an action is performed, not serialized. A page never writes `party`. Refuted by a library kind that sends two things in one call, which is two actions, or by a transport whose response is not text, which is a sibling of `hear` that validates a tree.
