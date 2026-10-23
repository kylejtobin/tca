# Refactor acceptance requirements

**Status: requirements for the replacement. Not implemented. Not verified.**

Nothing in this document is an executed test. No requirement below has been demonstrated against any code in the post-cleanup tree. The reduced primitive suite in `packages/python/type-construction-world/tests` covers only value-level construction and computation. It does not satisfy any requirement here that concerns invocations, evidence admission, external effects, recovery or interfaces.

The target architecture is [`TCA_ARCHITECTURAL_FOUNDATIONS.md`](TCA_ARCHITECTURAL_FOUNDATIONS.md). This document states the behavior that architecture must show.

## Traceability

The requirements in part 1 come from tests removed in the teardown. The baseline is commit `e06b207e4896ee039e0aca33332903664c65d50e` on branch `review`. The removed tests are recoverable from that commit under `packages/python/type-construction-engine/tests/type_construction_engine/` and `packages/python/type-construction-cli/tests/type_construction_cli/`.

Only behavior is carried forward. The old fixture structures, internal APIs, pass counts and source-layout assertions are not requirements. A replacement test may use any fixture and any internal structure that expresses the behavior.

## Part 1. Behavior of the removed tests

### Demand, eligibility and effects (`test_authority.py`)

- **A1.** Demand and eligibility are distinct. An action may have all its prerequisites without being relevant to the requested outcome, and a relevant action may lack the evidence it requires.
- **A2.** Adding a consumer of an action's result cannot weaken the action's evidence requirements.
- **A3.** Evidence that decides a branch is obtained before any effect that depends on that branch, with or without a fallback outcome.
- **A4.** When two unresolved effects are indistinguishable, the evaluation does not choose one arbitrarily.
- **A5.** An irrelevant branch, or a branch not taken, does not execute its effects.
- **A6.** An effect that was justified when it ran remains part of history if later work blocks.
- **A7.** A dependency shared by several consumers is evaluated once as a graph, not once per path to it.

### Occurrences and sources (`test_occurrences.py`)

- **B1.** Equal values do not merge distinct occurrences. Reusing one Python object in several places does not merge them either.
- **B2.** Repeated and nested elements remain separate occurrences.
- **B3.** Several uses of one source reference share that source.
- **B4.** Evidence cannot cross unrelated subjects, scopes or invocations.
- **B5.** Collection membership and cardinality remain meaningful: empty, fixed and variable collections keep their semantics.

### Static analysis (`test_proof.py`)

- **C1.** Unknown semantics establish no safety guarantee.
- **C2.** An optional input does not become a guaranteed one.
- **C3.** Alternatives keep their own assumptions.
- **C4.** A default is interpreted at the site that constructs with it. It is not a universal restriction of its type.
- **C5.** A sound exclusion never contradicts what construction actually does.
- **C6.** A legitimate conditional program stays expressible and is not rejected.

### Construction semantics (`test_engine.py`)

- **D1.** Native constraints, aliases, numeric bounds and validator behavior are respected as Pydantic defines them.
- **D2.** Declaration order does not arbitrarily change meaning.
- **D3.** An incorrect program receives a useful diagnostic that names the business distinction at fault.
- **D4.** Finite collection arithmetic and selections keep their value semantics.

### Failure kinds and resources (`test_execution.py`)

- **E1.** A condition that does not hold is different from a malformed construction and from an infrastructure failure.
- **E2.** A mix of validation failures is not reported as a business rejection.
- **E3.** A resource keeps its owner through exceptions and cancellation, and is released by that owner.
- **E4.** Independent invocations remain isolated from each other.
- **E5.** A diagnostic identifies the occurrence it concerns.

### Admission and derivation (`test_boundary.py`)

- **F1.** Externally supplied data passes through admission before it is used.
- **F2.** A derived value follows from its validated operands. A caller cannot supply it.
- **F3.** The evidence supporting an effect cannot be silently substituted for other evidence.

Exact source-string counts and prescribed file regions are not requirements.

### Telemetry (`test_logfire.py`)

- **G1.** Telemetry is observational. It does not affect execution.
- **G2.** Telemetry does not depend on one provider.
- **G3.** Payloads and credentials are excluded from telemetry by default.

A request equaling one trace is not a requirement.

### Interface projection (`test_cli.py`)

- **H1.** An interface's schema and help derive from the declarations.
- **H2.** An input that was omitted stays omitted. It does not become a default the declarations did not state.
- **H3.** Native validation produces useful diagnostics at the interface.
- **H4.** An interface does not create a second business model.

## Part 2. New required cases

These were not covered by the removed tests.

- **N1. Waiting without an open request.** An invocation waits for external evidence without retaining an open request or a coroutine.
- **N2. Recovery.** Recovery preserves program version, invocation identity, occurrence relationships and logical effect identity.
- **N3. Early callback.** A callback that arrives before the receive is registered is not lost.
- **N4. Duplicate delivery.** Delivering the same evidence twice creates neither duplicate evidence nor duplicate logical work.
- **N5. Conflicting duplicates.** Two different payloads under one delivery identity are detected. The second is not silently accepted.
- **N6. Correlation.** Correlation checks the declared source, tenant, subject, version and receiving relationship. Equal field values alone do not establish authority.
- **N7. Uncertain external success.** External success followed by a local recording failure is an uncertain outcome. The capability's recovery policy resolves it.
- **N8. Sibling failure.** A sibling's failure does not erase a completed external operation.
- **N9. Stale worker.** A stale worker cannot commit progress against an obsolete revision.
- **N10. Cancellation and disconnection.** Cancelling a request or losing the caller does not imply that prior effects never happened.
- **N11. Recorded observations.** Clock, identity and other nondeterministic observations are recorded and reused on recovery.
- **N12. Closed tuples.** A closed tuple keeps finite collection semantics. An evolving source has an explicit closure contract before absence, uniqueness or aggregate finality is inferred from it.
- **N13. Database concurrency.** Serializing an invocation does not replace the authoritative database's concurrency control.
- **N14. Local and durable hosts.** The same business declarations run under a local host and a durable host without a second authored workflow.
- **N15. Commands, queries and events.** They keep distinct meanings.
- **N16. First vertical slice.** The first slice pursues one declared outcome across delayed evidence, process termination, recovery and uncertain external success.

## What counts as meeting a requirement

A requirement is met when a test, written against the public behavior and independent of implementation helpers, fails if the behavior is wrong and passes when it is right. The report names which tests were executed and which requirements remain unverified.

A test of Pydantic behavior does not establish distributed recovery, correlation or concurrency correctness. Requirements N1 to N11 and N13 need tests against an execution host.
