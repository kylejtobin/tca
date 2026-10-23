# type-construction-program

Business programs as declared external relationships, the recorded history of one invocation, and an experimental pure evaluation of the next justified work. This package is the executable form of the contract validated under outcome 1 of [`TODO.md`](../../../TODO.md). It is experimental machinery for that validation, not the replacement runtime.

## What is here

- **Declarations** (`declaration`). `Source` names an external party. `Interaction` is one declared relationship with a source: what it says (`receives`), what this program sends to make it say so (`sends`), the receipt it may answer the send with first (`acknowledges`), how a delivery is tied to the invocation (`correlated`), and the evidence after which it says nothing more (`closed_by`). `Program` is a goal, the input it accepts, and its interactions; constructing one validates that every premise the goal transitively needs is obtained exactly one way, and refuses a program that waits on an undeclared source or holds a collection from a source with no declared closure.
- **History and protocol** (`invocation`). `Invocation` is an append-only history: the accepted input, admitted `Evidence`, committed `Intended` effects and numbered `Attempted` outcomes. An occurrence is where a value comes from: a `Site` (the evidence and the path to the value, element indices included), a `Built` (a constructed class and the occurrence of each premise) or `Elements`. `EffectIdentity` is the invocation, the request class and the occurrence of the request. `accept`, `admit`, `intend`, `perform`, `acknowledge`, `failed` and `uncertain` grow the history or raise `Refusal` with a structured reason.
- **Evaluation** (`evaluation`). `evaluate(program, invocation)` returns `Completed`, `Frontier` (requests to dispatch and receives outstanding, either possibly empty but not both) or `Blocked` (structured reasons). Construction is by occurrence and scoped per collection element: a tuple of a constructed class is one construction per element of the collection its premises vary over, and two sites that reach one occurrence share it. It constructs pure values through Pydantic, reads no clock, performs no effect and allocates nothing not derived from the history.

Pydantic owns composition, constraints, aliases, unions, collections and validation. The declarations add only what Pydantic cannot state: the source of a record, its tie to an invocation, and the closure of an evolving source.

## What is not here

A durable host. The history is in memory; nothing demonstrates recovery, worker ownership, stale commits, concurrency or early delivery against a store. Acceptance requirements N1 to N11 and N13 in [`docs/REFACTOR_ACCEPTANCE.md`](../../../docs/REFACTOR_ACCEPTANCE.md) need that host and remain unverified.

A class found at two places the declaration does not tell apart is refused with both places named: distinct roles of one class are distinct classes, and a collection's elements are told apart by position. The decisions this package demonstrates, their counterexamples and what remains unresolved are in [`docs/decisions/0001-durable-program-contract.md`](../../../docs/decisions/0001-durable-program-contract.md).

The package needs no runtime configuration.
