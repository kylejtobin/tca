# 0001. The declarative contract for durable business programs

**Status:** decided by experiment, 2026-10-23. Resolves the four design questions in `TCA_ARCHITECTURAL_FOUNDATIONS.md` §18 at the depth of outcome 1 in `TODO.md`. Nothing here is a durable-host demonstration.

**Evidence:** `packages/python/type-construction-program`. Every claim below names the test that executes it. Tests are under `tests/type_construction_program/`; the business declarations are `fulfillment.py`, `auction.py`, `review.py` and `lines.py`. The experiments ran under the locked dependencies with `just check`.

## What a program declares

Pydantic states composition, constraints, aliases, unions, collections and validation. A program adds one declaration per external relationship, `Interaction`: the `Source`, what it `receives`, optionally what the program `sends`, optionally what the source `acknowledges` a send with, how a delivery is `correlated` to the invocation, and for a source that says many records what it is `closed_by`. `Program` holds the goal, the accepted input and the interactions, and refuses at construction any premise not obtained exactly one way. Nothing else is declared; in particular, immediate versus delayed delivery is observed, not declared.

## An occurrence is where a value comes from

This is the decision the four questions rest on. A class is not an occurrence (foundations §4.1, §10.2). An occurrence is a `Site`, the evidence a value is found in and the path to it with element indices, or a `Built`, the class of a constructed value and the occurrence of each premise, or `Elements`, a collection of occurrences. Evaluation is scoped: a tuple of a constructed class is one construction per element of the one collection its premises vary over, each element bound in scope, and a premise is constructed once per scope it varies over. Two sites that reach one occurrence share it; two elements with equal content do not.

- Executable: `test_two_equal_lines_are_two_occurrences_and_two_intended_operations` (two lines equal in every field, in one piece of evidence, are two sites and two operations); `test_pure_construction_per_line_shares_each_lines_occurrence` (each line priced once, and the line total under `priced` is the same object as under the sum); `test_two_equal_lines_are_priced_twice`; `test_each_result_binds_to_the_line_that_requested_it`; `test_an_unsolicited_receive_correlates_to_one_element`; `test_work_per_element_of_a_source_proceeds_before_closure`.
- Counterexamples ruled out: identity by class, and identity by the evidence a value is in. Both make the two lines one. The first experiment shows the evidence-only identity collapsing to one while the occurrence identity stays two.
- Refusals, not guesses: `test_a_class_held_at_two_sites_is_refused_not_bound_by_guess` (two orders in one command, one `Order` premise: the declaration does not say which; distinct roles of one class are distinct classes); `test_equal_elements_make_an_element_correlation_ambiguous_not_guessed`; `test_a_goal_that_varies_per_element_is_refused`; `test_a_tuple_of_a_class_that_varies_over_nothing_is_refused`; `test_a_tuple_of_a_class_that_varies_over_two_collections_is_refused` (zip or product is a business rule the declaration did not state).
- Defects found and repaired on the way: a collection reached only through a mapped element never had its closer walked statically, so evaluation would have constructed what the declaration did not validate; a premise the walk never reached now raises instead of silently merging into one occurrence; closure of a per-invocation receive ignored a result returned inside the attempt.

## Q1. One interaction kind

**Decision.** One declaration kind expresses an immediate result, a delayed result, an unsolicited receive and a timer. The differences survive as observations and results, not as declaration kinds: a send exists or not; an attempt returns the result or a receipt; a receive is tied by field correlation, by the element its correlation selects, or by the intent it answers. The premise is satisfied only by the declared result, however it arrives.

- Executable: `test_the_outcome_is_the_same_whether_the_result_is_immediate_or_delayed`; `test_a_deadline_is_a_send_to_the_clock_and_a_receive_from_it`; `test_the_clock_is_read_once_and_the_reading_is_reused`.
- Counterexample ruled out: "the answer a send returns is the result". `test_a_receipt_satisfies_no_premise_and_leaves_the_receive_outstanding`.
- Counterexample ruled out: "an absent premise waits". `test_a_premise_with_no_declared_source_is_refused_at_declaration`.
- Failure found and repaired: inferring receipt versus result from payload shape. `TimerSet` and `Elapsed` share the shape `{at}`; the receipt validated as the result and closed the bidding with nothing bid. The capability reports the role: `perform` records a result, `acknowledge` a receipt. Kept executable in `test_a_receipt_shaped_like_the_result_is_told_from_it_by_report_not_by_shape`.
- Failure found and repaired: the same shape made a clock delivery ambiguous between `Now` and `Elapsed` at admission. A delivery naming the intent it answers selects that intent's interaction before validation; shape then confirms the type. A delivery to a receive that is one per element must name its intent or correlate to its element (`test_a_result_for_a_per_line_receive_must_name_the_line_it_answers`).
- Decided, flagged for review: a correlated result arriving before any send is admitted and satisfies an unscoped premise, and the send is then not demanded (`test_a_result_that_arrives_before_the_send_satisfies_the_premise`). A program that accepts only answers to its own request declares no field correlation.

## Q2. Three pure evaluation results

**Decision.** `Completed`, `Frontier`, `Blocked`. Actionable and waiting are not exclusive states: a frontier carries requests to dispatch and receives outstanding, either possibly empty, not both. Failed and cancelled are not pure results.

- Executable: `test_actionable_work_and_an_outstanding_receive_share_one_frontier`; `test_the_four_conditions_follow_from_the_history_in_turn`; `test_work_per_element_of_a_source_proceeds_before_closure` (a dispatch per element while the tuple stays open).
- Counterexample ruled out: four exclusive variants, by the first experiment.
- Attempt failure is not a conclusion: `test_an_attempt_failure_keeps_the_send_dispatchable_and_concludes_nothing`. Uncertainty is outstanding and not redispatched: `test_an_uncertain_attempt_is_outstanding_and_not_dispatched_again`.
- A declared negative outcome completes: `test_a_decline_is_a_completed_negative_outcome`. A refuted rule blocks with structured reasons and the history stays: `test_a_refuted_rule_blocks_with_structured_reasons_and_keeps_the_history`.
- Combination rule: in a conjunction, a malformed construction outranks a refutation, which outranks open work. Among alternatives, one constructed member wins; two are `Indeterminate`.

## Q3. Stable effect identity

**Decision.** `EffectIdentity` is the invocation, the durable name of the request class, and the occurrence of the request. Logical repetition needs no ordinal: a request built from a different element or from different evidence is a different operation, and a request built from the same occurrences is the same operation however many premises hold it. A business that intends a second operation declares what makes it second, a premise the first did not have, such as the decline it answers; identical declared premises are one intention.

- Executable: `test_a_retry_keeps_the_identity_and_numbers_a_new_attempt`; `test_another_invocation_with_the_same_input_has_different_identities`; `test_an_identity_is_reconstructed_from_the_history_not_allocated`; `test_a_request_built_from_later_evidence_names_that_evidence`; `test_two_equal_lines_are_two_occurrences_and_two_intended_operations`.
- Counterexample ruled out: a hash of the request as sent. `test_two_operations_with_equal_request_bodies_have_different_identities` (a hold and a charge with byte-equal bodies), and the two equal lines whose requests are byte-equal and distinct.
- Counterexample ruled out: the history positions of the evidence the request was built from, which was the first design here. Two lines of one order are in one piece of evidence; that identity collapsed two intended shipments into one.
- Recorded versus reconstructed: the intent and every attempt are recorded; the identity and the request are reconstructed deterministically from the history.

## Q4. Closed tuple admission and evolving sources

**Decision.** A tuple in the input is closed at acceptance. An interaction with `closed_by` is a collection source; the program holds every record it says; the tuple is sealed only at the declared closing evidence, admission refuses items after it, and per-element work proceeds before it. The host holds no rule about sufficiency.

- Executable: `test_one_received_approval_does_not_establish_only`; `test_a_current_maximum_is_not_final_while_more_may_arrive`; `test_a_tuple_supplied_in_the_input_is_closed_at_acceptance`; `test_an_item_after_closure_is_refused_and_a_redelivery_is_one_claim`; `test_closing_with_nothing_said_is_refuted_not_awaited`.
- Counterexample ruled out: "the items held so far are the collection", shown by constructing the selection from the held items and overturning it.
- Declared, not invented: `test_closure_is_declared_or_the_program_is_refused` (without `closed_by` the source says one record, so a tuple of what it says has nothing to vary over).

## Declaration diagnostics

A program that cannot be obtained one way is refused when constructed, as a `ValidationError` naming the premise path and the missing business distinction: no declared source, no closure, one class found two ways, a goal that varies, a tuple over nothing or over two collections, a correlation path that does not exist (`test_a_correlation_path_that_does_not_exist_is_refused_at_declaration`). Defect repaired: the path check raised `KeyError`, which Pydantic does not report as a refusal.

## Admission contract

`test_admission.py`: a repeated delivery identity is one claim; a different payload under it is a `Conflict`; equal field values do not correlate without the declared pair; a record is admitted only from its declared source; a receive held as one record takes no second answer. Contract experiments over an in-memory history, not host tests for N3 to N6.

## Unresolved

- **Correlation to received evidence.** A delivery correlates to the accepted input, to one of its elements, or names an intent. Correlation to a value in earlier evidence, such as a provider reference from a receipt, is not expressible.
- **Nested collections.** The walk and the scope admit a collection inside a collection; no declaration here exercises one.
- **Role trust.** A receipt with the shape of a result is told apart only by the capability's report; a mislabeling adapter is not caught (foundations §11.5).
- **Completion and cancellation.** Nothing closes an invocation after `Completed`, and attempt cancellation is not an outcome. Host matters.
- **Program version.** The identity does not name the program version; the invocation is assumed pinned to one.
