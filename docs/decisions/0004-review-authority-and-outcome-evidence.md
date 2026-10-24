# 0004. Reviewer authority and evidence for refactor outcomes

**Status:** binding review policy, issued by the designated independent Codex reviewer at Kyle's direction, 2026-10-23. Applies to every implementing agent and every refactor outcome. This is acceptance policy, not a claim that an outcome is achieved.

## Decision-record ownership

Only Kyle's designated independent Codex reviewer may create, edit, delete, rename, move or supersede decision records, including their status, evidence and rejection sections. Claude and every other implementing agent have read-only access by instruction to `docs/decisions/**`. Using Codex as an implementation agent does not confer reviewer authority. Implementers must not delegate these edits, generate replacements elsewhere as authoritative policy, or alter instructions to bypass this restriction. Kyle may explicitly change this ownership.

The reviewer records decisions; implementers produce code, counterexamples and reproducible observations. An implementer may propose an amendment in its handoff, naming the conflicting requirement, concrete counterexample, alternatives and consequences. A proposal is not permission to change the contract. Routine implementation choices and experiments within the contract proceed without waiting for a decision-record edit.

This is a repository conduct and acceptance rule, not an assertion of filesystem or GitHub identity-based access control. Unauthorized decision-record changes are grounds to reject the submission.

## Preserve the target

Read the complete foundations document for its causal and evidentiary requirements, then the current TODO and binding reviewer records. Distinguish requirements from open proposals and implementation history. No sentence in an experimental record can override a requirement merely because the implementation follows it. [0003](0003-construction-evidence-and-justified-execution.md) explicitly rejects 0002's demand rule.

Implementers may not weaken the foundations, acceptance requirements or TODO outcomes to make their implementation conform; nor may they mark outcomes complete or declare acceptance. A demonstrated conflict must be surfaced for reviewer decision. A documentation disclaimer, "experimental" label or list of untested cases does not discharge an assigned obligation. Reporting executed checks is evidence, not self-acceptance.

## Evidence follows the existing outcome sequence

| TODO outcome | Evidence required before independent acceptance |
| --- | --- |
| 1. Declarative contract | Executable business declarations and counterexamples resolve the four §18 questions; native construction, demand and occurrence semantics hold in composition. Chosen contracts and remaining limits are explicit. |
| 2. Pure evaluator | Exact occurrence relationships, shared dependency evaluation, distinct demand and eligibility, structured progress/blocking and preservation of admitted evidence. Justified independent work progresses concurrently. |
| 3. Durable invocation slice | One declared outcome crosses delayed evidence, process termination, recovery and uncertain external success, with version pinning and committed intents. In-memory replay alone is insufficient. |
| 4. Host equivalence | The same declarations and evaluator produce equivalent business behavior under local and durable hosts; only stated durability guarantees differ. |
| 5. Extended conformance | Concurrency, duplicates/conflicts, stale commits, repetition, scoped closure, cancellation and version recovery are exercised in combinations. |
| 6. Interfaces | CLI, API and events expose the same invocation and admission semantics without another business schema or workflow; commands, queries and events retain their meanings. |
| 7. Operational verification | Reproducible integrated recovery, security, telemetry, deployment and performance evidence supports each claimed guarantee. |

This table preserves TODO order and scope. It does not require completing later host or operational outcomes before outcome 1, and it does not permit deferring the semantic decisions that outcome 1 exists to resolve.

## Tests must be capable of rejecting the implementation

Preserve supplied reviewer counterexamples as executable regressions, including their business declarations and expected behavior. Mechanical API adaptations must preserve semantics and be identified. Do not replace a difficult case with an easier fixture, weaken assertions, skip failures, or move them outside the executed suite. If a counterexample contradicts the agreed contract, retain it and present that contradiction for review.

Test the governing invariant and neighboring combinations, not only the reported instance. For the construction boundary, compare actual output and failure behavior with independent native Pydantic calls under the same declared mode. For demand, pair invalid-evidence withholding with valid-evidence release and independent-work concurrency. Include plain wrappers, opaque identity validators and field-site constraints. For evidence, combine identical values, repeated operations, multiple collections, correlation and closure.

Preserve Pydantic's genuine semantics: arbitrary field reordering is not an invariant when validators or defaults depend on prior fields. Provenance assertions must not assume transforming validators preserve input values. Expected results must not be calculated with the same engine helpers being tested.

For each repaired invariant, demonstrate that a targeted incorrect implementation would fail the test. Use the rejected commit, a disposable fault injection, or an equivalent focused falsification. Passing test counts, import assertions and fixtures designed around implementation restrictions are not substitutes. Do not add an elaborate mutation framework merely to satisfy this rule.

## Required working behavior

Start with the actual semantic defect or unresolved contract and work in the implementation and executable declarations. Do not displace this work with inventories, formatting, unrelated documentation, license edits or tooling cleanup. Retained code is neither protected nor presumptively obsolete.

Handoffs name the commit, executed checks and their results, remaining failures and unverified claims. They do not announce outcome completion or acceptance. The reviewer evaluates the whole architectural intent and test adequacy, not merely whether the last defect list disappeared.

Reviewer amendments preserve history through explicit supersession or correction. They state what was required, what was observed, what was rejected and what remains open. Neither implementer nor reviewer may turn a failing implementation assumption into an accepted architecture by changing its description.
