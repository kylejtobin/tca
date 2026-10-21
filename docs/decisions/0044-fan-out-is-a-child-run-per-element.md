# 0044. Several of one thing in a run is a child run per element

Status: accepted

## Context

An order has lines; each line is quoted and charged; the order is paid when every line is. A run holds one instance per class, and `tuple[Line, ...]` on the request names several.

## Rejected

A loop on the page. An engine class for a batch, a mapping or a context. One run holding several instances of one class under one key. A scope map computed before the run that said, per class, which element it exists per, with `None` for once per run.

## Decision

When a request or a record enters the parent run, each `tuple[E, ...]` field it holds fans out: one child run per element, a `ChainMap` of the element's instance over the parent's instances, so a child sees everything the parent built. Each pass visits the parent first and then every child, and a class already present through the chain is not asked for again; so a class whose fields are fillable in the parent exists once, and a class that needs the element exists once per element, decided by construction and not by a map. The pass's actions are performed together across the parent and every child, and a record enters the run it was asked from. A `tuple[X, ...]` field of a parent-run class is supplied once every child holds an `X`, in element order, and Pydantic validates the tuple; until then the field is left out and the class is `missing`. An element source is a field of the request or of a record; a tuple inside a `Value` is not one, and a child's own records do not fan out again.

The proof sees the same two scopes. `prove` runs its passes over two sets, the classes that exist once per run and those that exist once per element, deciding each class from the same state the way a pass does: once if its single fields are filled from the run and its tuples from the run or its children, else per element if filled there. `proven` refuses as `scope` a route that lands per element, because its reply's fact holds an element or a per-element class directly, and a `tuple[X, ...]` field that collects a once-per-run class.

This is `traverse`: a construction applied to each element and collected into one; `asyncio.gather` is the effect and `tuple[X, ...]` validation is the collection.

## Evidence

A three-line order, tea 3, gold 50, jam 2 at 2.50 each: `Quote`, `LinePriced`, `Discounted` or `FullPrice`, `Charge` and `LinePaid` were constructed per line, `Paid` once, and the reply dumped `{"total":"125.000","charges":["ch_1","ch_1","ch_1"]}` with the lines holding `FullPrice`, `Discounted`, `FullPrice`. A one-line order dumped `{"total":"7.50","charges":["ch_1"]}`. `prove(Checkout, shop)` gave once: `PlaceOrder`, `Catalog`, `Payments`, `Paid`, `OrderPaid`, `Checkout`; per element: `Line`, `Quote`, `Price`, `LinePriced`, `LargeAmount`, `SmallAmount`, `Discounted`, `FullPrice`, `Charge`, `Charged`, `LinePaid`. A reply fact holding `one: LinePaid` directly was refused at startup: `scope` at `("CheckoutWrong",)`, "CheckoutWrong exists once per element; a route exists once per run, so its reply's fact collects elements as tuple[X, ...] instead of holding one". A fact collecting `tuple[Paid, ...]` was refused: `scope` at `("Collects", "orders")`, "Collects.orders collects Paid, which exists once per run; hold it directly".

## Consequences

A page writes `tuple[...]` on the request and on the collecting fact and nothing else. Refuted by an element that must come from inside a `Value`; then the `Value`'s field fans out too.
