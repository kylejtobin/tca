# 0035. A page holds classes only; procedure lives in a library kind's perform

Status: accepted

## Context

Every failure in this project's history is procedure written on a page: a function that ordered construction, a branch that chose a fact, a loop over lines, a validator that checked a value, a method that bound an id.

## Rejected

A page that may contain a function, a method, a branch, a loop, a `try`, or a validator when the developer judges it simpler.

## Decision

A page contains subclasses of the kinds, `StrEnum` subclasses, `@computed_field` properties and the `@property` members a library kind declares. Nothing else. The only Python in a program that calls anything is `perform` in a library kind. The smell check in `.agents/skills/smell-check/smell-check` reports every other `def`, every validator, every `if`, `for`, `while`, `try`, `raise`, every `None`, every bare primitive field and every reflective call, with the construct to write instead, and `just check` runs it on every program.

## Evidence

The smell check on a page with one of each construct reported 10 hits across all six labels; on the demo page it reported none. See `tests/features/smell_check.feature`.

## Consequences

A hit is never answered by editing the line; it is answered by the class the instruction names. Refuted by nothing.
