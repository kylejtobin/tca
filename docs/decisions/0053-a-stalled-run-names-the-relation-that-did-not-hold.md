# 0053. A stalled run names the relation that did not hold and the field no class fills, in the run each was asked from

Status: accepted

## Context

A pass that constructed nothing reported the required fields of every pending class against the parent run, so a per-element class was reported missing a field that existed in its child, and a relation that refused with no other outcome was never named.

## Rejected

Reporting `cycle` when every pending class waits on another: true in the proof, where fields are the only reason to wait, and false in a run, where a relation that refused is the reason. A class of the engine's own for the reason a class is absent: the engine declares no class, and Pydantic's refusal already says why.

## Decision

A pass keeps each refusal that said a class does not exist yet, as the `ValidationError` Pydantic raised. When a pass constructs nothing, `stalled` raises one `ValidationError` with one `relation` error at `(class,)` per class whose refusal held an error of type `relation`, "X did not hold: " and the kind's message, and one `missing` error per required single field no class fills, read with `unfilled` in the run the class is asked from, the parent for a class that descends from nothing and the child for one that descends from its element; a collecting field is never a root fault, since it waits on its children and a fault is theirs. Each error is reported once. `cycle` is reported only when neither explains the stall.

## Evidence

The engine's test program `faults`, whose only outcome for an element is `Cheap(low: Low)` with `Low(AtMost[Amount, Limit])`, one element and the party saying an amount of 25 over the limit of 10: `answer` raised a `ValidationError` holding `relation` at `("Low",)`, "Low did not hold: Amount exceeds Limit".

## Consequences

A stall names the rule or the field, in the class that refused, never a class downstream of it. Refuted by a stall whose cause is neither a relation nor a single field; then the cause is a cycle and is reported as one.
