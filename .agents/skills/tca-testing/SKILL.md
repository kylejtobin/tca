---
name: tca-testing
description: Design, write, change, or review TCA unit, integration, and acceptance tests. Establish independent expectations, challenge failure boundaries and composition, and verify defect detection without preserving implementation accidents.
---

# TCA Testing

Use [AGENTS.md](AGENTS.md) as the canonical package test instruction file. Copy it unchanged to each package's `tests/AGENTS.md`; repository placement, commands, and authority belong there.

## Establish the contract

- Tests MUST identify the required behavior, its independent expected result, and a plausible defect they detect. Express these through names, inputs, and assertions; cite the governing requirement in the module docstring.
- Expectations MUST come from the approved contract, explicit examples, or an independent reference. Tests MUST NOT calculate expected results through the implementation under test or preserve observed behavior merely because it exists.
- Every changed guarantee MUST have valid-progress and failure-boundary coverage. Exercise applicable malformed inputs, missing evidence, conflicting claims, and interactions with other guarantees. Missing combinations MUST NOT be concealed behind isolated happy paths.

## Choose the scope

| Type | Required scope and evidence |
|---|---|
| Unit | One rule or component; valid, boundary, and failure behavior with precise fault isolation. |
| Integration | Real collaborating components; preservation of values, identity, state, and failures across their boundary. Substitute external systems only. |
| Acceptance | Complete developer scenarios through public interfaces; required outcomes, justified progress, prohibited operations prevented, and consequential event sequences. No assertions about internal implementation structure. |

Choose the smallest scope that establishes the guarantee. An acceptance scenario can integrate components; MUST NOT duplicate it solely to populate another category. Unit tests MAY target internal algorithms; their expectations MUST express required semantics rather than incidental layouts or call sequences.

## Engineer the suite

- Tests MUST use explicit Arrange, Act, Assert structure and names stating condition and expected behavior. Keep consequential inputs and assertions visible. Share small setup helpers; MUST NOT build a second interpreter or testing framework.
- Tests MUST run unattended, independently, and in any order. Own setup and cleanup; control time, randomness, filesystem, and external services. Generated failures MUST retain a reproducible seed or minimized example.
- Use real values and real construction. Doubles MUST stop at the external boundary and MUST NOT supply the decision the test claims to verify. Assert actual external calls when testing execution permission.
- Failures MUST identify the violated expectation and relevant inputs. Parameterize meaningful boundaries and event permutations. Keep fast focused checks available and run broader checks for interacting behavior.

## Challenge the evidence

- Regression tests MUST fail on the reproduced defect and pass on the correction. Critical safeguards MUST undergo targeted fault injection or mutation, with the relevant test demonstrably failing for the intended reason.
- Assess each mutation against the requirement before turning it into an assertion. A surviving mutant is a question about the contract or coverage, not permission to freeze current behavior.
- Tests MUST NOT hide missing implementation or broken guarantees with skips, expected failures, swallowed exceptions, weaker assertions, or replacement mocks. Missing execution evidence remains unfinished work.
- Passing counts, coverage, and mutation scores MUST NOT substitute for demonstrated behavior. Preserve both prevention and legitimate progress; a system that refuses everything MUST fail acceptance.
