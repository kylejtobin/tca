# 0044. Several of one thing in a run is a child run per element

Status: accepted

## Context

An order has lines; each line is quoted and charged; the order is paid when every line is. A run holds one instance per class, and `tuple[Line, ...]` on the request names several.

## Rejected

A loop on the page. An engine class for a batch, a mapping or a context. One run holding several instances of one class under one key.

## Decision

An element class is one a request or a record holds as `tuple[E, ...]`; `elements(program)` reads each with the class and field that hold it. A class whose field names an element, or a per-element class, exists once per element; a record exists per its action's element; a produced class per its producer's; a class that only collects in `tuple[X, ...]` fields exists once per run. The run constructs a per-element class in one child run per element, a `ChainMap` of the element's instance over the parent's instances, so a child sees everything the parent built. A level's actions are performed together across every child. A `tuple[X, ...]` field receives each child's `X` in element order, and Pydantic validates the tuple. The proof refuses a reply's fact that exists per element, and a tuple field that collects a once-per-run class. An element source is a field of the request or of a record; a tuple inside a `Value` is not one.

This is `traverse`: a construction applied to each element and collected into one; `asyncio.gather` is the effect and `tuple[X, ...]` validation is the collection.

## Evidence

A three-line order: `elements` gave `Line` from `PlaceOrder.lines`; `scopes` gave `Quote`, `Price`, `LinePriced`, `Charge`, `Charged`, `LinePaid` per `Line` and `Paid` once per run; three `Quote`s performed at 0.0 s and three `Charge`s at 0.2 s; the reply dumped `{"total":"15.00","charges":["ch_tea","ch_milk","ch_jam"]}`. With a per-line discount, one line constructed `FullPrice` and the other `Discounted`. A reply fact holding one `LinePaid` directly was refused: "Wrong exists once per Line; a reply's fact exists once per run". A fact collecting `tuple[Paid, ...]` was refused: "collects Paid, which exists once per run; hold it directly".

## Consequences

A page writes `tuple[...]` on the request and on the collecting fact and nothing else. Refuted by an element that must come from inside a `Value`; then the `Value`'s field joins `elements`.
