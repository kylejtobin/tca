# 0058. Two records one action hears are told apart by a Literal or a required key, or the proof refuses them

Status: accepted

## Context

An action hears one of several records, `Tell[Party, Clear | Flagged]`, and `hear` validates the party's text as the union in Pydantic's smart mode. Two records the same payload constructs would be chosen by smart mode's tie-breaking, which Pydantic documents may change between minor releases.

## Rejected

A `Field(discriminator=...)` the engine adds to every record union: a union whose members differ by a required key needs none, and the engine would be writing into the page's declaration. Leaving it to a test.

## Decision

`told_apart(a, b)` reads two record classes: they are told apart when a field both declare as a `Literal` has no value in common, or when one requires a key, by alias or name, that the other does not declare, since `extra="forbid"` refuses it there. An action whose heard records include a pair not told apart is refused as `undiscriminated`: "Both hears Echo | Alike, and no field tells them apart; declare a Literal on each". `hear` keeps validating the union in smart mode, which is decisive for a union the proof accepted.

## Evidence

In the engine's test program, `Clear` with `status: Literal["clear"]` and `Flagged` with `status: Literal["flagged"]` and a `Word`, heard by one action: `hear` of `{"status": "clear"}` was a `Clear` and of `{"status": "flagged", "word": "no"}` a `Flagged`. In the program with the faults, `Echo` with `said: Word` and `Alike` with `told: Other = Field(alias="said")`, both validating the one key `said` with no `Literal`, heard by `Both`: `proven` raised `undiscriminated` at `("Both",)`.

## Consequences

A party's two answers that the same text constructs are one record. Refuted by nothing.
