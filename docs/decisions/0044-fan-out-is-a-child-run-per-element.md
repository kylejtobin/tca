# 0044. Several of one thing in a run is a child run per element

Status: accepted

## Context

An order has lines; each line is quoted and charged; the order is paid when every line is. A run holds one instance per class, and `tuple[Line, ...]` on the request names several.

## Rejected

A loop on the page. An engine class for a batch, a mapping or a context. One run holding several instances of one class under one key. A scope map computed before the run that said, per class, which element it exists per, with `None` for once per run.

## Decision

When a request or a record enters the parent run, each `tuple[E, ...]` field it holds fans out: one child run per element, a `ChainMap` of the element's instance, with the scalars and values it carries (0050), over the parent's instances, so a child sees everything the parent built. Which run a class belongs to is read from its fields, not kept: a class descends from the element its hypotheses mention, through the classes its single fields name, the action that hears a record, the carrier that holds a scalar or value, and the computed field that produces a class, until a class some request or record holds as `tuple[E, ...]` is reached. A class that descends from nothing is asked for in the parent; one that descends from `E` is asked for in each child made for an `E`. The pass's actions are performed together across the parent and every child, and a record enters the run it was asked from; a record heard in the parent that holds `tuple[E, ...]` fans out the same way. A `tuple[X, ...]` field is supplied once the carrier of the element `X` descends from is in the run and every child made for that element holds an `X`, in element order, and Pydantic validates the tuple; a carrier that fanned out to nothing supplies the empty tuple, the vacuous truth, so `Sum` of nothing is zero and a selection of nothing refuses (0049). Until the carrier arrives the field is left out and the class is `missing`. A tuple inside a `Value` is data, not a source.

The proof is one set, the classes that join from a route, and scope is the same read. `proven` refuses as `scope` a route that descends from an element, because its reply's fact holds an element or a per-element class directly; a `tuple[X, ...]` field whose `X` descends from nothing; a class that descends from two elements, which would exist per element of two things at once; and a record heard once per element that holds a collection, since a record fans out from the parent run only.

## Evidence

The engine's test program, two elements the party values at 2.50 each: `Asked`, `Low`, `High` and `Cheap` were constructed once per element, `Concluded.valued` held two `Cheap` in element order, and `Total(Sum[Amount])` summed to `5.00`. The same program with no element: `Concluded.valued` was the empty tuple and `Total` was `0`. `descends(Cheap)`, `descends(Asked)` and `descends(Amount)` were `{Element}`; `descends(Total)` and `descends(Operation)` were empty.

## Consequences

A page writes `tuple[...]` on the request and on the collecting fact, and nothing else. Refuted by an element that must come from inside a `Value`; then that field fans out too.
