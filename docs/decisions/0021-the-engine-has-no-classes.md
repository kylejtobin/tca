# 0021. The engine has no classes and no order: readiness is what construction answers

Status: accepted

## Context

The engine must construct the developer's classes, perform actions, and answer routes, and it must know which class can exist next.

## Rejected

Four designs. First: `Context` holding a walk, `Next`, `Call`, `Answered` and procedures `deliver`, `send`, `open`, `close`, `serve`. Second: a proof with producer classes `Given`, `Said`, `Built`, a forward run with a memo keyed by intending fact, concurrency rules, and `Opened[C]`. Third: a built resolver with a memo keyed by type, `issubclass` branches, a hearer lookup and a first-member loop. Fourth: a top-down proof that walked the reply's fact into an order, grouped the order into levels, derived a scope map with `None` for once-per-run, read generic arguments out of Pydantic's metadata with asserts, and a fold that recomputed `needs`, `collects` and `produces` dicts for every class on every run. Each of the four precomputed what Pydantic already answers when asked.

## Decision

The engine defines no class and computes no order. `answer(route, request, config, program)` is a run and a pass. The run is the instances so far, keyed by class, seeded with the request, the scalars and values it carries (0050), and the deployment's connections. A pass asks Pydantic for every class of the route not yet in the run, `cls.model_validate(held)`, where `held` is what the run has for the class's fields. Pydantic answers one of three ways: the instance constructs and enters the run, with what it carries, with each computed field's value under its own class, and with an action gathered with the pass's other actions; the refusal is `missing` only, or a relation kind refuses with `relation` (0048), and the class does not exist yet, so the next pass visits it again; the refusal is anything else and it propagates. The passes end when the route itself constructs, which needs the reply, which needs its fact (0005). A pass that constructs nothing raises `missing` at each field no class fills. `prove(route, program)` is the same passes over classes, once per route, in the two scopes of 0044, and `proven(program)` checks at startup that every class joins some route, that each record has one hearer, each produced or carried class one source and each party one config field, that no route lands per element and no tuple collects a once-per-run class, and that no union holds two members the proof can see both constructing and no relation is one it can see never holding or never refusing (0051). The engine reads `model_fields`, union members, `model_computed_fields` return types, an action's record classes, and the `gt`, `ge`, `lt` and `le` metadata on a scalar's root; nothing else.

## Evidence

The engine's shop, with three parties answering fixed records, a derived line total, a threshold relation per line and a screen that may refuse: a one-line order of three teas at 2.50 answered `{"total":"7.50","charges":["ch_1"],"cheapest":"7.50"}` holding `FullPrice`; three lines including fifty gold answered `{"total":"125.000","charges":["ch_1","ch_1","ch_1"],"cheapest":"5.00"}` holding `FullPrice`, `Discounted`, `FullPrice`; a two-line order ended in four passes. A second action hearing a record is refused as `hearer`; a second computed field producing a class as `producer`; a config holding a party twice as `party`; two facts holding each other as `cycle` on each; `Large` rewritten as a second `AtMost` as `overlap`; a relation over operands whose bounds cannot meet as `relation`. The module type-checks under basedpyright strict, passes ruff and bandit, and defines no class.

## Consequences

A class in `type_construction.engine` is a defect. A dict of the program's shape computed before construction is a defect; what a class needs is read from its fields at the moment it is asked for. Procedure in the engine is the pass, the proof's passes, and `opened`, and ruff's complexity limits bound them. Refuted by a behavior the passes cannot produce from annotations; none identified.
