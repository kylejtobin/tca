# 0021. The engine has no classes

Status: accepted

## Context

The engine must construct the developer's classes in dependency order, perform actions, and answer routes.

## Rejected

Three designs in one session. First: `Context` holding a walk, `Next`, `Call`, `Answered` and procedures `deliver`, `send`, `open`, `close`, `serve`. Second: a proof with producer classes `Given`, `Said`, `Built`, a forward run with a memo keyed by intending fact, concurrency rules, and `Opened[C]`. Third: a built resolver, `answer()`, with a memo keyed by type, `issubclass` branches, a hearer lookup and a first-member loop; it passed `just check` on nine tests and was reverted. The memo keyed by type gave every `Instant` and `Identity` in a run one value. Each design described the page in the engine's terms.

## Decision

The engine is reading and a fold, and it defines no class. `prove(route, program)` reads top-down from `A` through `F` and every field's class and returns the classes in the order they can exist, with every fault raised at once; it is cached per route. `levels` groups the classes the run builds by depth, one more than the deepest class each needs or collects; records and produced classes are not built and are not in a level. `answer(route, request, config, program)` is one span and one fold: for each level, for each class, for each run it exists in, `model_validate` from the instances its fields name, keep what its computed fields produced, perform if it is an action; a level's actions are awaited together with `asyncio.gather`; the reply is `A(of=F)`. The engine holds no state beyond the instances of one run, keyed by class, with a child run per element as a `ChainMap` over the parent (0044). Connections are opened and closed by `opened` (0045). Spans are the only output beside the reply (0046).

## Evidence

`levels` on a route with a per-line discount: `Quote`, `LinePriced`, `Discounted` and `FullPrice`, `Charge`, `LinePaid`, `Paid`, with no record and no produced scalar in any level. The construction loop has no branch on a class's kind: its only conditions are a refused union member, which is skipped, and a performed action, which is gathered. Against a program with two parties: `Quote` and `Estimate` started at 0.0 s and ended at 0.2 s together, and `Charge` started at 0.2 s. The module type-checks under basedpyright strict and defines no class.

## Consequences

A class in `type_construction.engine` is a defect. A branch in the fold that tests what a class is, rather than whether it constructed, is a defect in an earlier reading, and the reading is fixed. Refuted by a behavior the fold cannot produce from annotations; none identified.

