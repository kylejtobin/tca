# 0022. The classes are the inventory

Status: accepted

## Context

A `nouns.json` per package listed every class with its kind, what it holds and what it is, and a check compared it to the code.

## Decision

The class is the name, its base is the kind, `model_fields` is what it holds, the docstring is what it is. `nouns.json`, its schema's use, and `noun-check.py` are removed. The `tca-noun-list` skill is a skeleton until a need for a second representation is shown.

## Evidence

No run applies; the decision removes a construct. The list restated `model_fields` and docstrings; the check compared one copy to another.

## Consequences

Unwritable: a second representation of the program's classes. Refuted by a reader that cannot read Python classes; none in this system.
