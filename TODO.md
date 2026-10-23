# TODO

What is not done, in order. An outcome is marked done only when its completion has been observed through independent behavioral tests. Passing the reduced primitive suite does not complete any architectural outcome.

## Now

- [ ] 1. **A clean foundation with no competing runtime or instructions.** Complete and verify the teardown while retaining independent world primitives and useful behavioral requirements. This comes first so the request-bound implementation and its instructions cannot quietly determine the replacement.

- [ ] 2. **A validated declarative contract for durable business programs.** Business types express outcomes, evidence relationships and justified interactions; Pydantic owns native composition, constraints, validation and serialization. Resolve the interaction, evaluation-result, effect-identity and evidence-closure questions with executable declarations and counterexamples, adding only semantics Pydantic does not supply. This establishes what the engine must interpret before implementation choices harden into architecture.

- [ ] 3. **A pure evaluator that derives justified progress from typed evidence.** Interpret the declarations as a goal-directed construction graph, preserving occurrence binding, shared dependencies and the distinction between demand and eligibility. Delegate construction to Pydantic, keep static claims bounded by what can be established, and distinguish completion, actionable work, waiting and blocking without performing effects. This makes the validated contract executable, initially to the depth needed for the first complete invocation.

- [ ] 4. **One complete invocation that survives delayed evidence, process termination and uncertain external success.** A host admits evidence against declared source relationships, commits effect intents before dispatch, records observations and outcomes, and resumes the same version-pinned invocation with stable causal identities. Its execution mechanics serve the evaluator's decisions without duplicating business logic. This tests the architecture across real failure boundaries before expanding its surface.

- [ ] 5. **Equivalent business behavior under local and durable execution.** Run the same declarations through the same evaluator under both hosts, preserving construction and demand semantics while stating their different durability guarantees. This follows the durable slice to prove that persistence and scheduling remain execution choices rather than separate business programs.

- [ ] 6. **Correct execution across concurrency, repetition, evolving evidence, cancellation and program versions.** Extend independent conformance tests to duplicate and conflicting deliveries, stale commits, distinct logical repetitions, source closure, retained effect history and version-pinned recovery. Application scenarios exercise generic semantics rather than becoming engine branches. This challenges the working architecture beyond its first successful path; migration remains deferred until required.

- [ ] 7. **CLI, API and event interfaces that expose the same invocation model.** Derive schemas and projections from the declarations, preserve Pydantic's documented validation modes, and carry commands, queries and events through their appropriate admission boundaries. This comes after execution semantics are established so transports introduce neither a second validation language nor an authored workflow.

- [ ] 8. **An operationally verified replacement with documentation and acceptance evidence matching its behavior.** Demonstrate security boundaries, observational telemetry, deployment, recovery and performance; reconcile every acceptance requirement with executed evidence and state remaining limits explicitly. This comes last so completion describes the integrated framework's demonstrated behavior, with required unresolved guarantees preventing a completion claim.

The target is in `docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`. The requirements to meet are in `docs/REFACTOR_ACCEPTANCE.md`.
