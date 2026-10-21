# 0021. The engine has no classes and no order: readiness is what construction answers

Status: accepted

## Context

The engine must construct the developer's classes, perform actions, and answer routes, and it must know which class can exist next.

## Rejected

Four designs. First: `Context` holding a walk, `Next`, `Call`, `Answered` and procedures `deliver`, `send`, `open`, `close`, `serve`. Second: a proof with producer classes `Given`, `Said`, `Built`, a forward run with a memo keyed by intending fact, concurrency rules, and `Opened[C]`. Third: a built resolver with a memo keyed by type, `issubclass` branches, a hearer lookup and a first-member loop. Fourth: a top-down proof that walked the reply's fact into an order, grouped the order into levels, derived a scope map with `None` for once-per-run, read generic arguments out of Pydantic's metadata with asserts, and a fold that recomputed `needs`, `collects` and `produces` dicts for every class on every run. The fourth passed its own check because the smell check was pointed away from it and record 0021 named the engine the place procedure lives. Each of the four precomputed what Pydantic already answers when asked.

## Decision

The engine defines no class and computes no order. `answer(route, request, config, program)` is a run and a pass. The run is the instances so far, keyed by class, seeded with the request and the deployment's connections. A pass asks Pydantic for every class of the route not yet in the run, `cls.model_validate(held)`, where `held` is what the run has for the class's fields. Pydantic answers one of three ways: the instance constructs and enters the run, with each computed field's value under its own class and an action gathered with the pass's other actions; the refusal is `missing` only and the class waits for the next pass; the refusal is anything else and it propagates. The passes end when the route itself constructs, which needs the reply, which needs its fact (0048). A pass that constructs nothing raises `missing` at each field no class fills. `prove(route, program)` is the same passes over classes, once per route, and `proven(program)` checks at startup that every class joins some route and that each record has one hearer, each produced class one producer and each party one config field. The engine reads `model_fields`, union members, `model_computed_fields` return types, and an action's record type; nothing else.

## Evidence

The shop with three lines, two parties returning fixed records and a per-line discount: a one-line order of three teas at 2.50 answered `{"total":"7.50","charges":["ch_1"]}` holding `FullPrice`; three lines including fifty gold answered `{"total":"125.000","charges":["ch_1","ch_1","ch_1"]}` holding `FullPrice`, `Discounted`, `FullPrice`. The same program with `Quote` deleted was refused by `proven` with one error, `missing` at `("LinePriced", "price")`, "no class fills LinePriced.price, which holds Price". A second action hearing `Price` was refused as `hearer`; a second computed field producing `LargeAmount` as `producer`; a config holding `Catalog` twice as `party`; two facts holding each other as `cycle` on each. The module type-checks under basedpyright strict, passes ruff and bandit, and defines no class.

## Consequences

A class in `type_construction.engine` is a defect. A dict of the program's shape computed before construction is a defect; what a class needs is read from its fields at the moment it is asked for. Procedure in the engine is the pass, the proof's passes, and `opened`, and ruff's complexity limits bound them. Refuted by a behavior the passes cannot produce from annotations; none identified.
