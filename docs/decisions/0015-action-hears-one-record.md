# 0015. An action hears one record; perform is abstract on Action and the library kind implements it

Status: accepted

## Context

An action sends something to a party and hears something back. The engine must know what it hears; the transport must know what it sends and where.

## Rejected

Finding the payload and the path by scanning an action's computed fields for a return type of `Record` or `Resource`. The checker cannot verify that such a field exists.

## Decision

`Action[P: Connection, T: Record]` declares `perform(self, party: P) -> T` as an `@abstractmethod` and no fields of its own. A library kind adds its parameters, declares its verb's inputs as abstract properties, `Post[P, S, T]` with `sends -> S` and `resource -> Resource`, `Get[P, T]` with `resource`, and implements `perform`, which sends and returns `T.model_validate_json(...)` or raises. A page implements the properties as plain properties. Pydantic's metaclass is an `ABCMeta`, so an action with no library kind cannot be constructed.

## Evidence

`class Post[P: Connection, S: Record, T: Record](Action[P, T])` with `@property @abstractmethod def sends(self) -> S`; `class Charge(Post[Payments, Payment, Charged])` returning a `Payment` from `sends` type-checked. A subclass `Half` omitting `sends` raised `TypeError: Can't instantiate abstract class Half` at construction. A direct `Action[Catalog, Price]` subclass with no `perform` raised `TypeError: Can't instantiate abstract class Bare`. `resolved(Charge, Action)` returned `(Payments, Charged)` through `Post`'s type variables.

## Consequences

Unwritable: a payload found by return type. `sends` and `resource` are plain properties, not computed fields, because an action is performed, not serialized. Refuted by a library kind that sends two things in one call; that is two actions.
