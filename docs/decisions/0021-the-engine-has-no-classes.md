# 0021. The engine has no classes and no order: readiness is what construction answers

Status: accepted

## Context

The engine must construct the developer's classes, perform actions, and answer routes, and it must know which class can exist next.

## Rejected

Four designs. First: `Context` holding a walk, `Next`, `Call`, `Answered` and procedures `deliver`, `send`, `open`, `close`, `serve`. Second: a proof with producer classes `Given`, `Said`, `Built`, a forward run with a memo keyed by intending fact, concurrency rules, and `Opened[C]`. Third: a built resolver with a memo keyed by type, `issubclass` branches, a hearer lookup and a first-member loop. Fourth: a top-down proof that walked the reply's fact into an order, grouped the order into levels, derived a scope map with `None` for once-per-run, read generic arguments out of Pydantic's metadata with asserts, and a fold that recomputed `needs`, `collects` and `produces` dicts for every class on every run. Each of the four precomputed what Pydantic already answers when asked.

## Decision

The engine defines no class, computes no order, and keeps nothing about a program: every question is a read of the program's classes at the moment it is asked. `answer(route, request, config, program)` is a run and a pass. The run is the instances so far, keyed by class, seeded with the request, the scalars and values it carries (0050), and the deployment's connections. A pass asks Pydantic for every class of the route not yet in the run it belongs to, `cls.model_validate(supplied)`, where `supplied` is what the run has for the class's fields, and which run a class belongs to is read from its fields (0044). Pydantic answers one of three ways: the instance constructs and enters the run, with what it carries, with each computed field's value under its own class, and with an action performed with the pass's other actions in one task group (0054); the refusal is `missing` only, or a relation or a selection refuses with `relation` (0048, 0049), and the class does not exist yet, so the next pass asks again; the refusal is anything else and it propagates. The passes end when the route itself constructs, which needs the reply, which needs its fact (0005). A pass that constructs nothing raises the relations that did not hold and the fields no class fills, in the run each was asked from (0053). `prove(route, program)` is the same passes over classes, once per route, returning the one set of classes that join, and `proven(program)` checks at startup that every class joins some route and is held by some field (0052), refusing as `missing` the field no class fills and as `cycle` a class no root fault explains, whose unfilled fields only another such class would bring, that each record has one hearer, each produced or carried class one source and each party one config field, that every class has one scope (0044), and that no relation is undecidable, certain or impossible and no union holds two members that can both hold, decided from the relations' declared constraints and the scalars' bounds (0051). The engine reads `model_fields`, union members, `model_computed_fields` return types, an action's record classes, a relation's `constraints`, and the `gt`, `ge`, `lt` and `le` metadata on a scalar's root; nothing else.

## Evidence

The engine module declares no class; its names are functions and type aliases. In the engine's test program, two elements valued at 2.50 each were quoted once per element in pass 1, valued and summed in passes 2 and 3, and answered in three passes with `Concluded.valued` holding two `Cheap` and `Total` 5.00; the program with the faults was refused at startup with `unused`, `missing`, `carrier`, `undecidable`, `relation`, `overlap`, `hearer`, `party`, `cycle` at `Egg` and `Chicken`, and `scope` named at once, and `Answered`, which waits on the missing field, was not reported as a cycle. The module type-checks under basedpyright strict, passes ruff and bandit, and keeps the import contract that the engine sits on the world.

## Consequences

A class in `type_construction.engine` is a defect. A dict of the program's shape computed before construction is a defect; what a class needs is read from its fields at the moment it is asked for. Procedure in the engine is the pass, the proof's passes, and `opened`, and ruff's complexity limits bound them. Refuted by a behavior the passes cannot produce from annotations; none identified.
