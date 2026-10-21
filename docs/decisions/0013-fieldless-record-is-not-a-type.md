# 0013. A record with no fields is not a type

Status: accepted

## Context

Records such as `Sent`, `Elapsed`, `Tick`, `Started` were declared with no fields to mark that a party said nothing, that time passed, or that a context began.

## Decision

A `Record` with no fields is not written. A record holds what distinguishes it.

## Evidence

`class Arrival(BaseModel): said: Tick | Elapsed | Sent` with all three fieldless: `Arrival(said={})` constructs `Tick`, the first member. Construction cannot tell the three apart.

## Consequences

Unwritable: a fieldless record. Refuted by nothing; two things construction cannot distinguish are one thing.
