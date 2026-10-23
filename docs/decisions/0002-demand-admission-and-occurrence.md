# 0002. Demand, admission and occurrence: the contract after the review of 0001

**Status:** experiments, 2026-10-23. Supersedes in part [`0001-durable-program-contract.md`](0001-durable-program-contract.md). This record bounds every claim by the test that executes it; where a claim is wider than its tests, it says so. It does not resolve the design questions in `TCA_ARCHITECTURAL_FOUNDATIONS.md` §18, and it does not mark any outcome in `TODO.md` or any requirement in `REFACTOR_ACCEPTANCE.md` as met. Nothing here is a durable-host demonstration.

**Evidence:** `packages/python/type-construction-program`, tests under `tests/type_construction_program/`. Business declarations: `fulfillment.py`, `auction.py`, `review.py`, `lines.py`, `decisions.py`, `transfer.py`. Executed with `just check` under the locked dependencies: ruff, ruff format, basedpyright strict, bandit, and pytest, 90 tests passing, of which 71 are in this package and 19 in `type-construction-world`.

## What was wrong in 0001, as assumptions rather than defects

The review of 0001 found that the first slice made its examples executable by weakening the architecture they were meant to test. Grouped by the assumption each disproved case rests on:

1. **Available and demanded was taken for justified.** The evaluator merged the open work of every premise of a conjunction and of every member of an alternative and dispatched the union. Foundations §7.2 says decisions precede their dependent effects, with or without a fallback, and §7.3 says a choice between effects is never guessed. The fulfillment fixture happened to sequence its charge before its shipment by data dependency, so the defect never showed.
2. **A returned payload was taken for evidence.** `perform` validated a returned result against the interaction's records and recorded it, without the correlation, duplicate, closure or intent checks a delivery went through. Foundations §4.2, §6.2 and §10.4: a result is validated and admitted before it is evidence, and type validity is not source authority.
3. **A class was taken to have one construction relationship.** Evidence was located, memoized and bound by class. Two roles of one class in one input were refused with the instruction to declare two classes. Foundations §4.1 and §5: a class is not an occurrence, and a construction relationship is how a particular occurrence obtains its premises.
4. **A correlated result arriving before any request was taken to satisfy the premise.** A `Captured` for the right order, from the right source, admitted when this invocation had asked for nothing. That is available evidence mistaken for the declared authority, which is the provider's answer to this program's request.

Each is replaced below with the rule that repairs it, the test that would fail without the repair, and the neighbouring cases tried against the replacement.

## The construction graph

`Program` now compiles the goal into a graph of construction relationships, `Node`: `Found` (a value at a location in the input or a received record), `Heard` (one record a source says, with the node of the request it answers), `Made` (a class from its premises), `Choice` (a union), `Each` (one construction per element of a collection) and `All` (every record a collection source says, sealed by its closer). Nodes are structural: two places that obtain a value the same way compile to one node and share one occurrence; two that obtain it differently are two nodes. Evaluation memoizes by node and the scope it varies over, not by class.

- Executable: `test_pure_construction_per_line_shares_each_lines_occurrence` (one line total shared by the priced line and the sum); `test_each_role_is_its_own_occurrence_and_its_own_operation` (one `Account` class, two nodes, two operations); `test_each_total_is_over_its_own_lines_and_equal_lines_are_two`.
- Not demonstrated: that memoization bounds evaluation cost (acceptance A7 speaks of cost as well as sharing). No test measures it.

## Binding: the declaration that tells two places apart

`Binding(premise, subject)` declares that the premise at a path is obtained at a place in the accepted input. On an `Interaction` the path is from the request it sends; on a `Program` it is from the goal. A premise that is a tuple of a constructed class is bound to the collection it is one construction per element of. Inside one construction per element, a class found in that element is the element's; that is what "per element" means, and it is the one place the compiler prefers a location, stated here so it is not a silent rule. A class found at two places the declarations do not tell apart is still refused, and the refusal now names both places and the `Binding` that would decide, instead of a class to invent.

- Executable: `test_without_a_binding_two_roles_of_one_class_are_refused_naming_the_binding`; `test_each_role_is_its_own_occurrence_and_its_own_operation` (the debit request holds the source account, the credit request the target, each with its own identity and its own correlated confirmation); `test_a_confirmation_for_the_other_role_does_not_answer_this_one`; `test_a_binding_to_a_place_holding_another_class_is_refused`; `test_without_a_binding_one_element_class_in_two_collections_is_refused`; `test_each_total_is_over_its_own_lines_and_equal_lines_are_two`; `test_a_class_held_at_two_sites_is_refused_naming_the_binding_that_would_decide`.
- Bounded: a binding's subject is a place in the accepted input. Binding a premise to a value in received evidence is not expressible. A goal-relative binding into a union member or a request is accepted by the path grammar and exercised by no test.

## Demand: two rules over the graph

**Necessity across alternatives.** Where more than one member of a union is live (not refuted), a request is dispatched only if every live member needs it. A request one member needs and another does not is withheld as `Unchosen`. When nothing else can advance the invocation, that is `Blocked` with `Undecidable`, naming the premise, the members and the operations: the declarations have not said which effect to perform.

**Decisions precede dependent effects.** A premise is undecided while evidence still to come may refute it: a receive whose source may answer with another member, a refutable class over an open premise, a tuple over an unclosed source whose element can be refuted. While any premise of a conjunction is undecided, the requests under its decided premises are withheld as `Deferred`, naming the premises they wait on, and only the requests under the undecided premises are dispatched. This holds with and without a fallback outcome.

Both are properties of how outcomes combine at `Made`, `Each` and `Choice`, not of any one request; a `Frontier` reports what is withheld and why beside what is dispatched and awaited.

- Executable, decisions first: `test_a_constructible_demanded_request_waits_for_the_decision_it_depends_on` (no fallback: the ping waits for the registrar); `test_a_denial_blocks_and_the_dependent_request_was_never_dispatched`; `test_with_a_fallback_the_branch_not_taken_performs_no_effect`; `test_a_decision_nothing_is_sent_for_still_defers_the_request_that_depends_on_it` (the decision is an unsolicited receive); `test_two_operations_with_equal_request_bodies_have_different_identities` (the hold waits for the charge, which may decline).
- Executable, never guessed: `test_a_choice_between_two_effects_nothing_decides_is_not_guessed` (`Blocked` with `Undecidable`, no intent committed); `test_the_same_choice_decided_by_a_rating_performs_the_one_the_rating_picks`.
- Executable, not serialized: `test_two_necessary_requests_nothing_can_refute_are_dispatched_together`; `test_two_decisions_are_made_together`; `test_work_per_element_of_a_source_proceeds_before_closure`; `test_a_deciding_request_that_needs_another_result_has_that_result_obtained_first` (deferral does not deadlock: the request that decides needs the pinged result, so the ping is dispatched).
- Executable, eligibility: `test_a_consumer_added_cannot_weaken_what_the_request_requires` (A2); `test_a_justified_effect_stays_in_the_history_when_later_work_blocks` (A6).
- Counterexample that bounds the rule, kept as a limit: `test_a_passive_alternative_beside_the_charge_leaves_the_charge_unchosen`. Shipped or refused or cancelled by the customer: the charge is needed by two members and not by the third, which needs only a delivery that may never come. The evaluator withholds the charge and waits. The declarations do not say the charge is attempted while a cancellation may arrive, and shipping cannot be the outcome while one may: that needs a boundary on the cancellation (foundations §9.4), and no declaration here expresses absence over a closed receive. Whether that is the right reading of the program, or a missing declaration kind, is not decided here.

## Admission: one judgement for a delivery and a returned result

`admissible(program, invocation, claim)` is the one place a claim becomes evidence. A delivery and a result an attempt returns are both a `Claim`: the source, how it came (`Delivered` or `Returned`), the payload, and the request it answers when known. The judgement is the same: the receive is selected by the request named or by the source's declared receives; the payload is validated as what that receive says; a claim already admitted under its origin is one claim and a different payload under it is a `Conflict`; every declared correlation holds, at exactly one element where the subject is in a collection; a claim for a solicited receive answers one committed request, named or the one its correlation selects, and with none it is `Unrequested`; a receive that says nothing more refuses. `perform` records the attempt's outcome only after the result passes; refused, nothing is recorded, and what that makes of the attempt is the host's to record.

- Executable: `test_a_result_for_another_order_is_refused_whichever_way_it_comes` (the same `Uncorrelated` reason by delivery and by return); `test_a_result_this_invocation_never_asked_for_is_not_evidence` (`Unrequested`, and the request is still dispatched); `test_a_result_delivered_before_the_attempt_is_the_answer_the_attempt_then_repeats` (early callback after the intent is committed: admitted as the answer; the attempt's equal result is that answer; a different one is `Closed` both ways); `test_a_result_for_the_other_line_does_not_answer_this_lines_request` (an element-correlated result that names one line's request and correlates to the other is `Ambiguous` both ways; unnamed, it answers the line it correlates to).
- Carried from 0001: the admission experiments in `test_admission.py`, and `test_a_receipt_shaped_like_the_result_is_told_from_it_by_report_not_by_shape`.
- Bounded: these are contract experiments over an in-memory history. They do not demonstrate N3 to N6 against a host.

## What the §18 questions look like after this

Not resolved. What the experiments show about each:

- **Q1, one interaction kind.** One declaration kind still expresses the cases in `test_interactions.py`: immediate and delayed results with one business outcome, an unsolicited receive, a timer. The admission revision narrows the kind: a solicited receive is satisfied only by an answer to a request this invocation committed. No experiment shows the kind is sufficient for an interaction not represented here.
- **Q2, three results.** `Completed`, `Frontier`, `Blocked` still express the four conditions in `test_evaluation.py`, and `Frontier` now carries withheld work with its reasons. `Blocked` gains `Undecidable`. Whether a withheld frontier with nothing awaited should ever be reported as waiting rather than blocked is settled here as blocked for unchosen effects; a deferred-only frontier with nothing awaited cannot arise, and the evaluator raises if it does.
- **Q3, effect identity.** Invocation, request class, and the occurrence of the request, where an occurrence is now a node of the graph bound in a scope. `test_identity.py`, `test_occurrences.py` and `test_roles.py` show distinct operations for byte-equal bodies, for equal elements, and for two roles of one class. Logical repetition without a distinguishing premise remains inexpressible: two intended operations with the same request node and the same scope are one.
- **Q4, closure.** Unchanged from 0001: `test_closure.py`. The passive-alternative limit above is where closure meets demand and is not resolved.

## Unresolved

- Absence over a closed receive, and with it the passive alternative beside an effect (above).
- Correlation or binding to a value in received evidence, such as a provider reference from a receipt.
- Nested collections: the compiler and the scope admit a collection inside a collection; no declaration exercises one. Goal-relative bindings into union members and requests likewise.
- Role trust: a receipt with the shape of a result is told apart only by the capability's report (foundations §11.5).
- A returned result that fails admission: the attempt happened and returned something that is not evidence; this protocol records nothing and leaves the host to record `uncertain`. Untested.
- Completion and cancellation of an invocation; program version in the identity; evaluation cost.
