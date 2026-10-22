# 0050. A request, a record or a value carries the scalars and values it holds into the run

Status: accepted

## Context

A derivation's operands are the unit price a record says and the quantity a line holds; a relation's operands are a derived total and a threshold. The run is keyed by class, and a class is asked for from the instances the run holds under the classes its fields name, so an operand must be in the run under its own class. A scalar inside a record, and a value inside a request, were reachable only through the class that held them.

## Rejected

A derivation holding the record and the value and reading the operand by field name: a path, which is reflection on the page. The engine putting every field of every constructed instance into the run: a fact's fields are its conclusions' grounds, not things that exist on their own, and two facts holding the same scalar class would collide.

## Decision

A request, a record and a value carry: when one enters the run, the scalars and values its single fields hold enter under their classes, and what those values hold enters in turn. The request carries when the run is seeded; a record carries when its action's answer enters; a value carries when it is constructed in a pass or when it is an element of a child run (0044). The proof reads the same: `carried(cls)` is what a carrier brings with it, and the elements a request or a record holds join with what each carries; which run a carried class belongs to is read by descent through its carrier (0044). A fact, an action, a reply and a route do not carry. Exactly one carrying class holds each scalar or value class, and the proof refuses a second as `carrier`, so a scalar is named by its role, never one name on two carriers.

## Evidence

In the engine's test program, `Amount` is carried by `Heard`, which `Asked` hears once per element: `descends(Amount)` was `{Element}`, `Low(AtMost[Amount, Limit])` constructed once per element from the carried `Amount` and the defaulted `Limit`, and `Total(Sum[Amount])` summed two carried amounts to `5.00`. `Name`, carried by `Element`, entered each child run with its element. In the program with the faults, `Name` carried by both `Element` and `Heard` was refused at startup as `carrier` at `("Name",)`.

## Consequences

A scalar class appears on one carrier. A value held by the request exists in the run without a fact asking for it. Refuted by a scalar two parties both say under one business name; that is two scalars, one per party, and a relation or a fact that holds both.
