# TODO

Remaining refactor outcomes, in order. Implementing agents provide changes and reproducible evidence; acceptance and outcome status belong to the reviewer. Tests must challenge declared behavior independently of implementation helpers.

The old runtime, interfaces, decision catalog and conflicting skills have been removed, including the remaining skills in `7aaf39d`. Repeated teardown inventories and blanket audits of retained primitives are not prerequisites to the work below. Fix concrete defects encountered while establishing the new contract; retained code is neither mandatory nor presumptively obsolete.

## Now

- [ ] 1. **A validated declarative contract for durable business programs.** Establish how business types declare outcomes, evidence relationships and external interactions while Pydantic owns native composition, constraints, validation and serialization. Resolve the four questions in foundations §18 through executable declarations and counterexamples: immediate and delayed interactions, pure evaluation results, logical effect identity and closed evidence collections. This comes first so the replacement implements demonstrated semantics rather than turning infrastructure choices or procedural examples into the business language.

- [ ] 2. **A pure evaluator that derives justified progress from typed evidence.** Interpret declarations as a goal-directed construction graph with exact occurrence relationships, shared dependencies and distinct demand and eligibility. Delegate value construction to Pydantic and keep unsupported static conclusions unproven. Derive completion, actionable work, waiting and blocking without performing effects, initially to the depth needed for the durable slice; this makes the contract executable before adding its host.

- [ ] 3. **One complete invocation that survives delayed evidence, process termination and uncertain external success.** Admit evidence against declared source relationships, commit effect intents before dispatch, retain observations and outcomes, and resume the same version-pinned invocation with stable logical identities. The host executes and records the evaluator's justified work without interpreting business branches. This exercises the architecture's defining failure boundaries before broadening its surface.

- [ ] 4. **Equivalent business behavior under local and durable execution.** Run the same declarations through the same evaluator under both hosts, preserving construction and demand semantics while stating their different durability guarantees. This follows the durable slice to establish that persistence and scheduling do not create a second business program.

- [ ] 5. **Correct execution across concurrency, repetition, evolving evidence, cancellation and program versions.** Extend conformance to duplicate and conflicting deliveries, stale commits, distinct logical repetitions, closure, retained effect history and version-pinned recovery. Application scenarios challenge generic semantics rather than introducing scenario-specific engine branches. This broadens the demonstrated contract beyond the first slice; program migration remains deferred.

- [ ] 6. **CLI, API and event interfaces that expose the same invocation model.** Derive schemas and projections from declarations, preserve Pydantic's documented validation modes, and admit commands, queries and events according to their distinct meanings. This follows the execution contract so transports add access to the program without adding another schema or workflow.

- [ ] 7. **An operationally verified engine with reproducible acceptance evidence.** Exercise security boundaries, observational telemetry, deployment, recovery and performance against the integrated implementation, and tie acceptance requirements to executed tests. This establishes the replacement's demonstrated guarantees and remaining limits; documentation records the evidence rather than substituting for it.

The target is in `docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`. The requirements to meet are in `docs/REFACTOR_ACCEPTANCE.md`. Contract experiments do not establish host recovery or concurrency guarantees.
