# 0001. The declarative contract for durable business programs

**Status:** decided by experiment, 2026-10-23. Resolves the four design questions in `TCA_ARCHITECTURAL_FOUNDATIONS.md` §18 at the depth of outcome 1 in `TODO.md`. Nothing here is a durable-host demonstration.

**Evidence:** `packages/python/type-construction-program`. Every claim below names the test that executes it. Tests are under `tests/type_construction_program/`; the business declarations are `fulfillment.py`, `auction.py` and `review.py`. The experiments ran under the locked dependencies with `just check`.

## What a program declares

Pydantic states composition, constraints, aliases, unions, collections and validation. A program adds one declaration per external relationship, `Interaction`: the `Source`, what it `receives`, optionally what the program `sends`, optionally what the source `acknowledges` a send with, how a delivery is `correlated` to the invocation, and for an evolving source what it is `closed_by`. `Program` holds the goal, the accepted input and the interactions, and refuses at construction any premise not obtained exactly one way. Nothing else is declared; in particular, immediate versus delayed delivery is observed, not declared.

## Q1. One interaction kind

**Decision.** One declaration kind expresses an immediate result, a delayed result, an unsolicited receive and a timer. The differences survive as observations and results, not as declaration kinds: a send exists or not; an attempt returns the result or a receipt; a receive is tied by field correlation or by the intent it answers. The premise is satisfied only by the declared result, however it arrives.

- Executable: `test_the_outcome_is_the_same_whether_the_result_is_immediate_or_delayed`. The same `Fulfilled` goal, with equal content, from a charge answered at once and from a charge acknowledged then delivered by webhook. `test_a_deadline_is_a_send_to_the_clock_and_a_receive_from_it`: the clock reading is an immediate interaction, the deadline a delayed one acknowledged by `TimerSet` and answered by `Elapsed`.
- Counterexample ruled out: "the answer a send returns is the result". `test_a_receipt_satisfies_no_premise_and_leaves_the_receive_outstanding`: the receipt is recorded against the attempt, admits no evidence, and is refused when presented as a delivery.
- Counterexample ruled out: "an absent premise waits". `test_a_premise_with_no_declared_source_is_refused_at_declaration`: a `Record` premise with no interaction refuses the program, naming the premise path.
- Failure found and repaired. The first design inferred receipt versus result from the payload's shape. `TimerSet` and `Elapsed` share the shape `{at}`, so the receipt validated as the result and closed the bidding with nothing bid. Repair: the capability reports the role; `perform` records a result, `acknowledge` records a receipt. The failing case is kept executable in `test_a_receipt_shaped_like_the_result_is_told_from_it_by_report_not_by_shape`.
- Failure found and repaired. The same shape made a clock delivery ambiguous between `Now` and `Elapsed` at admission. Repair: a delivery naming the intent it answers selects that intent's interaction before validation; shape then confirms the type. Without a named intent, a solicited receive with no field correlation cannot be tied and is refused as `Uncorrelated`.
- Decided, flagged for review: a correlated result arriving before any send is admitted and satisfies the premise, and the send is then not demanded (`test_a_result_that_arrives_before_the_send_satisfies_the_premise`). A program that accepts only answers to its own request declares no field correlation and is tied by intent alone.

## Q2. Three pure evaluation results

**Decision.** `Completed`, `Frontier`, `Blocked`. Actionable and waiting are not exclusive states: a frontier carries requests to dispatch and receives outstanding, either possibly empty, not both. Failed and cancelled are not pure results.

- Executable: `test_actionable_work_and_an_outstanding_receive_share_one_frontier` (a charge to dispatch and an approval awaited at once); `test_the_four_conditions_follow_from_the_history_in_turn`.
- Counterexample ruled out: four exclusive variants. The first experiment has no single variant to be in.
- Attempt failure is not a conclusion: `test_an_attempt_failure_keeps_the_send_dispatchable_and_concludes_nothing`. Uncertainty is outstanding and not redispatched: `test_an_uncertain_attempt_is_outstanding_and_not_dispatched_again`; which is right is the capability's recovery contract, not decided here.
- A negative business decision completes when declared: `test_a_decline_is_a_completed_negative_outcome`. A refuted rule blocks with structured reasons and the history stays: `test_a_refuted_rule_blocks_with_structured_reasons_and_keeps_the_history`.
- Defect found and repaired: a refuted premise reached by two paths was reported twice; reasons are now distinct.
- Combination rule, for the record: in a conjunction, a malformed construction outranks a refutation, which outranks open work. Among alternatives, one constructed member wins; two constructed members are `Indeterminate`.

## Q3. Stable effect identity

**Decision.** `EffectIdentity` is the invocation, the durable name of the request class, and the history positions of the evidence the request was constructed from. It is derived from the history and also recorded before dispatch. Retries keep it and number attempts.

- Executable: `test_a_retry_keeps_the_identity_and_numbers_a_new_attempt`; `test_another_invocation_with_the_same_input_has_different_identities`; `test_an_identity_is_reconstructed_from_the_history_not_allocated`; `test_a_request_built_from_later_evidence_names_that_evidence`.
- Counterexample ruled out: identity as a hash of the request as sent. `test_two_operations_with_equal_request_bodies_have_different_identities`: a hold and a charge with byte-equal bodies have distinct identities.
- Recorded versus reconstructed: the intent (identity and request) and every attempt are recorded; the identity itself and the request are deterministically reconstructable from the history. Attempt numbers are positions in the recorded attempts.

## Q4. Closed tuple admission and evolving sources

**Decision.** A tuple in the input is closed at acceptance. A collection from a source is sealed only at the declared closing evidence; the evaluator waits for exactly that evidence, admission refuses items after it, and the program that lacks the declaration is refused. The host holds no rule about sufficiency.

- Executable: `test_one_received_approval_does_not_establish_only` (one approval, then a second, then closure refutes `Only`); `test_a_current_maximum_is_not_final_while_more_may_arrive` (a third bid overturns the current greatest); `test_a_tuple_supplied_in_the_input_is_closed_at_acceptance`; `test_an_item_after_closure_is_refused_and_a_redelivery_is_one_claim`; `test_closing_with_nothing_said_is_refuted_not_awaited`.
- Counterexample ruled out: "the items held so far are the collection". Both experiments construct the selection from the held items to show the conclusion it would reach and then overturn it.
- Declared, not invented: `test_closure_is_declared_or_the_program_is_refused`.

## Declaration diagnostics

A program that cannot be obtained one way is refused when constructed, as a Pydantic `ValidationError` whose message names the premise path and the missing business distinction: no declared source (`test_a_premise_with_no_declared_source_is_refused_at_declaration`), no closure (`test_closure_is_declared_or_the_program_is_refused`), one class found two ways (`test_a_class_held_at_two_sites_is_refused_not_bound_by_guess`), a correlation path that does not exist (`test_a_correlation_path_that_does_not_exist_is_refused_at_declaration`). Defect found and repaired: the path check raised `KeyError`, which Pydantic does not report as a validation refusal, so a bad path escaped `Program` and `Interaction` as a raw exception.

## Admission contract

`test_admission.py`: a repeated delivery identity is one claim; a different payload under it is a `Conflict`; equal field values do not correlate without the declared pair; a record is admitted only from its declared source; a receive held as one record takes no second answer. These are contract experiments over an in-memory history, not host tests for N3 to N6.

## Unresolved

- **Occurrence binding.** This evaluator binds a premise by its declared class, validated to be found one way. One class at two sites of an invocation is refused, not guessed (`test_a_class_held_at_two_sites_is_refused_not_bound_by_guess`), and so is not expressible. Outcome 2 must bind by occurrence without reintroducing guessing.
- **Logical repetition.** The identity has no ordinal. The same request from the same evidence in one invocation is one effect; a deliberate repetition under identical evidence (periodic polling, "charge again") is not expressible except as a distinct request class. Whether an ordinal belongs in the identity is undemonstrated.
- **Correlation to received evidence.** A delivery correlates to the accepted input or names an intent. Correlation to a value in earlier evidence, such as a provider reference from a receipt, is not expressible.
- **Role trust.** A receipt with the shape of a result is told apart only by the capability's report. An adapter that mislabels one is not caught; this is the trusted-code boundary of foundations §11.5.
- **Completion and cancellation.** Nothing closes an invocation after `Completed`, and attempt cancellation is not an outcome. Both are host matters.
- **Program version.** The identity does not name the program version; the invocation is assumed pinned to one.
