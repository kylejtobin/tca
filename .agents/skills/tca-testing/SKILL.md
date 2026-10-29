---
name: tca-testing
description: Design, write, change, or review TCA unit, integration, and acceptance tests. Establish independent expectations, challenge failure boundaries and composition, and verify defect detection without preserving implementation accidents.
---

---
name: tca-testing
description: Design, implement, revise, or review TCA unit, integration, and end-to-end acceptance tests. Apply correctness by construction, independent behavioral expectations, adversarial testing, and demonstrated defect detection without preserving implementation accidents.
---

# TCA Testing

Follow [AGENTS.md](AGENTS.md) for mandatory repository testing instructions. Keep that file synchronized with every package's `tests/AGENTS.md`.

## Establish correctness

- **Prevent defects by construction.** Identify guarantees enforced through declarative types, validated construction, and architectural invariants. Verify enforcement at the authoritative boundary; avoid duplicating those checks throughout the application. Report missing architectural guarantees rather than normalizing invalid constructions.
- Derive expected behavior from approved contracts, explicit examples, or independent references. Never derive expected results from the implementation under test or preserve observed behavior merely because it exists.
- For each changed guarantee, establish legitimate progress, meaningful failure boundaries, and a plausible defect the tests will detect. Exercise interactions between guarantees, not only isolated happy paths.

## Test at three layers

| Layer | Required evidence | Applicable techniques |
|---|---|---|
| **Unit** | Individual rules, types, and components satisfy their contracts. | TDD, negative testing, boundary-value analysis, equivalence partitioning, property-based testing, fuzz testing, mutation testing. |
| **Integration** | Real collaborating components preserve contracts, values, identity, state, and failure behavior across boundaries. | Contract testing, interface testing, state-transition testing, failure injection, transaction and recovery testing. |
| **Acceptance (E2E)** | Complete developer workflows satisfy business requirements through public interfaces and the assembled application. | End-to-end testing, acceptance testing, regression testing, adversarial scenarios, business invariants, consequential event sequences. |

Select techniques according to the guarantee and its risks; techniques may apply across layers. Choose the smallest scope that provides meaningful evidence, but verify critical application outcomes end-to-end. Do not duplicate lower-level assertions merely to populate another layer.

## Construct reliable tests

- Name tests for their conditions and expected behavior. Keep setup, actions, and assertions explicit; cite governing requirements in module docstrings.
- Use real construction and real collaborating components. Isolate external dependencies where necessary, but never substitute the behavior being verified or supply the decision the test must establish.
- Make tests independent, unattended, deterministic, and order-independent. Control time, randomness, filesystem, and external state. Preserve reproducible seeds or minimized counterexamples for generated failures.
- Exercise valid behavior and relevant failures, including malformed inputs, conflicting evidence, boundary conditions, interrupted operations, and recovery where applicable. Verify resulting state and permitted side effects.
- Assert required semantics, not incidental implementation structure, internal call sequences, or historical execution traces. Preserve confidence through refactoring and product evolution.

## Prove the tests work

- Reproduce regressions with a failing test before correcting the defect.
- Challenge critical safeguards through targeted mutation testing or fault injection; establish that relevant defects cause meaningful failures.
- Never conceal missing implementation or broken guarantees with skips, expected failures, swallowed exceptions, weakened assertions, or replacement mocks.
- Treat coverage, test counts, and mutation scores as diagnostic evidence, not proof of correctness. A system that rejects everything must fail acceptance just as a system that permits everything must fail.
- Optimize for the smallest maintainable suite that establishes convincing behavioral confidence.
