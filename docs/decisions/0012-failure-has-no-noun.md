# 0012. Failure has no noun

Status: accepted

## Context

A party may not answer. A rule may not hold. A reply may not construct.

## Rejected

`Unreachable(Record)` holding a `Failure` scalar with the library's error text, held by facts such as `Unpaid` and `Unquoted`, answered by replies such as `OrderUnpaid`, whose computed field exposed the library text to the caller. Six classes on the first page existed so the engine had a type to construct when a client raised. A `Reason` vocabulary was about to be added to hide the library text.

## Decision

A failure is a refusal. A client exception from `perform` propagates. A `ValidationError` propagates. A route none of whose replies construct refuses the caller. A refusal the party states is a `Record` the action hears, in a union with the success record (0009).

## Evidence

No run applies; the decision removes a construct. The removal took `Unreachable`, `Failure`, `Unpaid`, `Unquoted`, `OrderUnpaid`, `OrderUnquoted` off the first page; the route answers `OrderPaid` only.

## Consequences

Unwritable: a class naming the engine's or the transport's failure. The server kinds map the exception to a status or an exit code. Refuted by nothing; what a party says on failure is a record.
