# 0021. The engine is one loop over the program's declarations, and the proof and the run are the same construction

Status: accepted

## Context

The engine must construct the developer's classes, perform actions, and answer routes, and it must know which class can exist next and where. Everything it knows must come from the declarations, or the run runs because the engine's procedure happens to work and not because the program is true.

## Rejected

Five designs. First: `Context` holding a walk, `Next`, `Call`, `Answered` and procedures `deliver`, `send`, `open`, `close`, `serve`. Second: a proof with producer classes `Given`, `Said`, `Built`, a forward run with a memo keyed by intending fact, concurrency rules, and `Opened[C]`. Third: a built resolver with a memo keyed by type, `issubclass` branches, a hearer lookup and a first-member loop. Fourth: a top-down proof that walked the reply's fact into an order, grouped the order into levels, derived a scope map with `None` for once-per-run, read generic arguments out of Pydantic's metadata with asserts, and a fold that recomputed `needs`, `collects` and `produces` dicts for every class on every run. Fifth: a proof that was one set of joined classes, with scope decided at run time by `descends`, a graph walk from each class through fields, hearers, carriers and producers to the element it reached, with `None` for a class that reached none, and a run keyed by class with child runs chained over the parent: the walk was an algorithm of the engine's own, it supported one level of elements only, and scope was computed by the run instead of proven. A compiled construction graph with bound occurrences, a demand worklist with subscriptions, memoization by occurrence and an effect scheduler with derived decision prerequisites: a plan the run obeys in place of the declarations.

## Decision

The engine reads each class's fields once, through `holds`, `collects`, `premises`, `declares`, `heard`, `carried` and `produces`, over `model_fields`, `model_computed_fields` and the generic parameters, and knows nothing else about a program. There is one loop. The proof's passes ask `place` for every class not yet placed and keep what is placed until a pass places nothing; `Proof` is constructed from the result and its validator refuses the program with every fault (0055). The run's passes ask Pydantic for every class of the route not yet in its scope whose premises are present, `cls.model_validate(supplied)`, keep what constructs, perform the pass's actions in one task group (0054), and stop when the route constructs; a pass that constructs nothing raises what stalled it (0053). Readiness is the same read in both: a class is asked for when every required single field names a placed class, or a present instance. A relation or a selection that refuses is refuted in that scope and asked again next pass; any other refusal propagates. The engine's classes are its values: `Placement`, `Waiting`, `Fault`, `Proof` and the run's `Scope`; none describes a program's shape beyond what the reads say, and nothing is kept between runs. `answer(route, request, deployment, proof)` takes the proof as a value the server computed once (0030).

## Evidence

In the engine's test program, two elements the party valued at 2.50 in two parts each: pass 1 built and performed `Asked` in each element's scope; pass 2 built `Low`, `Total` and each part's `Portion`, and refuted `High`; pass 3 built `Portions`, `Largest` and `Cheap` in each element's scope; pass 4 built `Concluded`, `Answered` and `Operation`; `tca.passes` was 4 and the reply was `{"total":"5.00"}`. The program with the faults was refused at startup with `missing`, `cycle`, `twice`, `unplaceable`, `collects`, `route`, `unreached`, `unmodeled`, `boundary`, `config`, `ambiguous`, `never`, `undiscriminated` and `undecided` named at once, and `Answered`, which waits on a field no class fills, was not reported as a cycle. The module type-checks under basedpyright strict, passes ruff and bandit, and keeps the import contract that the engine sits on the world.

## Consequences

A dict of the program's shape computed before construction, a walk to decide a scope, an order, a plan or a scheduler in the engine is a defect; what a class needs is read from its fields when it is asked for, and where it lives is what the proof placed. Procedure in the engine is the two loops, `opened`, and the solver inside the proof's validator. Refuted by a behavior the passes cannot produce from annotations; none identified.
