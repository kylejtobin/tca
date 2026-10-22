# 0015. An action holds its party, hears the records it declares, and performs through its library kind

Status: accepted

## Context

An action sends something to a party and hears something back, and a party may answer in more than one way: a charge is made or declined. The engine must find the connection the deployment configured for the party and must know what the action hears; the transport must know what it sends and where. Only Pydantic's generic metadata names `P` and `T`, and Pydantic gives a generic instance no `type[T]` at run time.

## Rejected

Finding the payload and the path by scanning an action's computed fields for a return type of `Record` or `Resource`: the checker cannot verify that such a field exists. `perform(self, party: P)` with the engine reading `P` out of the parametrization and passing the connection. A record `Parametrization` validated from the metadata in place of asserts. A phantom field typed `T` so that Pydantic would resolve it. A library kind's `perform` validating the response itself, which needs `type[T]` and ends in a cast. `heard` returning one record class, so that an action declaring a union of records had no class to return and the program could not start.

## Decision

`Action[P: Connection, T: Record]` declares `party: P` and `perform(self) -> T` as an `@abstractmethod`. The engine seeds the run with the deployment's connections under their classes, so the action constructs when the fact that intends it and its party both exist, like any other class, and `perform` sends through `self.party`. `T` is one record class or a union of them, `Tell[Party, Clear | Flagged]`, whose members a field tells apart (0058). A library kind adds its parameters, declares its verb's inputs as abstract properties, `Post[P, S, T]` with `sends -> S` and `resource -> Resource`, `Get[P, T]` with `resource`, and implements `perform` as `return hear(self, text)`, where `hear` is the engine's function that validates the party's JSON text as `T` through a `TypeAdapter`, so a union chooses its member, and narrows the result to `T` with a `TypeIs` guard. `T` is read once, in the proof, by `said`, which binds each parametrized base's arguments through the parameters of the base before it, down the MRO to `Action`; `heard` is the record classes in it. Pydantic's metaclass is an `ABCMeta`, so an action with no library kind cannot be constructed. Exactly one action hears each `Record` class; a record heard by two has two sources and is refused as `twice` (0050). A record is placed where its hearer is, and the elements it declares one level under (0044).

## Evidence

In the engine's test program, `class Asked(Tell[Party, Heard])` gave `Asked.model_fields["party"].annotation is Party` through the library kind, and `heard(Asked)` returned `(Heard,)`; for an action declared `Tell[Party, Heard | Other]`, `heard` returned `(Heard, Other)`; `hear` on an action declared `Tell[Party, Clear | Flagged]` returned a `Clear` for `{"status": "clear"}` and a `Flagged` for `{"status": "flagged", "word": "no"}`. `Tell.perform` written as `return hear(self, self.party.says.root)` type-checked under basedpyright strict against `-> T`. A direct `Action[Party, Heard]` subclass with no `perform`, and a `Connection` subclass with no `open` or `close`, each raised `TypeError` naming the class as abstract when constructed. In the program with the faults, `Heard` heard by `Asked` and `Reasked` was refused as `twice` at `("Heard",)`.

## Consequences

Unwritable: a payload found by return type; a `perform` that takes the party; a library kind that reads metadata. `sends` and `resource` are plain properties, not computed fields, because an action is performed, not serialized. A page never writes `party`. A party's refusal is a record in the action's union, and the fact that holds it is the outcome (0012). Refuted by a library kind that sends two things in one call, which is two actions, or by a transport whose response is not text, which is a sibling of `hear` that validates a tree.
