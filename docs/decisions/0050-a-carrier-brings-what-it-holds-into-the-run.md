# 0050. Every class has one source, and a request, a record or a value carries the scalars and values it holds

Status: accepted

## Context

A derivation's operands are the amount a record says and the share a part holds; a relation's operands are a derived total and a constant. A scope is keyed by class, and a class is asked for from the instances the scope holds under the classes its fields name, so an operand must be in the scope under its own class. Where each class's instances come from must be one thing, or the proof cannot say where it lives and the run cannot say which instance a field means.

## Rejected

A derivation holding the record and the value and reading the operand by field name: a path, which is reflection on the page. The engine putting every field of every constructed instance into the run: a fact's fields are its conclusions' grounds, not things that exist on their own, and two facts holding the same scalar class would collide. Separate faults per pair of sources, `hearer`, `carrier`, `producer`, `party`: one read, repeated four times. Projection aliases on the page, `AliasPath`, to say which of two carried instances a field means: a line written for the engine, when holding the carrier says it.

## Decision

A class's sources are read from the declarations, `sources(cls)`: a route's request; a carrier that holds it directly, read from `brought`; a request or a record that declares it as an element; an action that hears it; a config field that holds it; a default root. A class with two or more is refused as `twice`, naming them: `Name has 2 sources: carried by Element, carried by Heard; exactly one`. A class with none is built from its premises, or is a word a computed field says, or is a fault its holder reports as `missing`. A request, a record and a value carry: when one enters a scope, the scalars and values its single fields hold enter under their classes, and what those values hold enters in turn; the request carries when the run is seeded, a record when its action's answer enters, a value when it arrives inside its carrier or as an element. A scalar is therefore named by its role, never one name on two carriers, and a fact that needs the value two carriers both hold holds the carrier.

## Evidence

In the engine's test program, `Amount` is carried by `Heard`, which `Asked` hears once per element: `Low(AtMost[Amount, Limit])` constructed once per element from the carried `Amount` and the seeded `Limit`, and `Total(Sum[Amount])` summed two carried amounts to `5.00`; `Share`, carried by `Part`, an element the record declares, entered each part's scope with its part. In the program with the faults, `Name` carried by both `Element` and `Heard` was refused as `twice` at `("Name",)`, `Heard` heard by `Asked` and `Reasked` as `twice` at `("Heard",)`, and `Party` held by `Parties.party`, `Parties.backup` and `Backups.party` as `twice` at `("Party",)`.

## Consequences

A scalar class appears on one carrier. A value held by the request exists in the run without a fact asking for it. Refuted by a scalar two parties both say under one business name; that is two scalars, one per party, and a relation or a fact that holds both.
