# 0053. A stalled run names the relation or selection that did not hold, with the ordering observed, leaving out one whose complement held

Status: accepted

## Context

A pass that constructs nothing must say why, in the developer's names. In a run, the reason a class is absent is a relation or a selection that refused, or a premise that never arrived; and in a scope where one of two complementary relations held, the other's refusal is the choice being decided, not a cause.

## Rejected

Reporting `cycle` when every pending class waits on another: true in the proof, where fields are the only reason to wait, and false in a run, where a relation that refused is the reason. A class of the engine's own for the reason a class is absent, beyond the refusal Pydantic raised. Pydantic's message for a refused ordering, "Input should be -1 or 0", which names neither operand. Naming every refuted relation, so that a stall over an empty selection also named the complement that was refused because the other held.

## Decision

A pass keeps each refusal that said a relation or a selection does not hold, with the scope it refused in. When a pass constructs nothing, `stalled` raises one `ValidationError` with one `relation` error at `(class,)` per refuted class that no class present in its scope decides against, "X did not hold: " and what was observed: for a relation, the ordering field's operands and the ordering, rendered from the error's `input` and the field's `Comparison`, as `value Amount > bound Limit`; for a selection, Pydantic's message. A refuted relation whose complement is present in the same scope is left out, since that choice was decided; when every refuted class is left out, all are named. When nothing was refuted, one `missing` error per required field no class fills in the scope the class is asked from, for a class no pending class would bring; and `cycle` only when neither explains the stall.

## Evidence

The program `stalls`, whose only outcome for an element is `Cheap(low: Low)` with `Low(AtMost[Amount, Limit])`, one element and the party saying an amount of 25 over the limit of 10: `answer` raised a `ValidationError` holding exactly `relation` at `("Low",)`, "Low did not hold: value Amount > bound Limit". The engine's test program with the party saying an amount of 2.50 and no parts: `Largest(Greatest[Portion])` refused with `too_short`, `High` refused since 2.50 is under the limit, and `answer` raised exactly `relation` at `("Largest",)`, "Largest did not hold: Tuple should have at least 1 item after validation, not 0", with `High` left out because `Low` held in that scope.

## Consequences

A stall names the rule in the class that refused, never a class downstream of it and never the complement of a choice that was made. Refuted by a stall whose cause is neither a refusal nor a single field; then the cause is a cycle and is reported as one.
