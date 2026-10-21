# 0037. A type is never weakened to pass a check

Status: accepted

## Context

A red check from basedpyright or Pydantic can be made green by `Any`, `cast`, `# type: ignore`, `object` in place of the type, a default where none belongs, or `None` on a page.

## Rejected

Each of those, as the fix for a red check.

## Decision

The checker's refusal is the specification. The type it names is written, or the class the data is becomes a class (0032), or the narrowing is a `TypeIs` guard (0031). The smell check reports `Any`, `cast(`, `# type: ignore` and `object` as a type under `WEAKENED`.

## Evidence

`**kwargs: object` on `Reply`'s hook produced 48 errors and `Unpack[ConfigDict]` produced none, before the hook itself was removed (0010). `**` unpacking to pass or omit `metavar` was replaced by `metavar=None` the same hour it was written.

## Consequences

A weakened type in a program or a kind is a defect regardless of whether the check is green. Refuted by nothing.
