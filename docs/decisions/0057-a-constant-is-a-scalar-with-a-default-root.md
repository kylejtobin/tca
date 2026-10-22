# 0057. A constant is a scalar with a default root, seeded in every run, with no other source

Status: accepted

## Context

A threshold, a rate, a limit: a business constant is a value no request carries and no party says, and the relations and derivations that hold it need it in the run. The proof needs its value, since a relation against a constant is decided by it.

## Rejected

The relation's field defaulted on the page, `bound: Threshold = Threshold()`: a line written for the engine, repeated on every subclass that holds the constant. A constant read from the environment as a `Setting`: a business value is not a deployment value (0025). Treating the default as the type's domain for every scalar: a scalar the request carries can be any value its bounds admit, whatever its default.

## Decision

A constant is a scalar whose root has a default and that no other class places: `class Limit(Scalar[Decimal])` with `root: Decimal = Decimal(10)`. The proof places every constant at `()`, and the run seeds every scope's root with `cls()` for each, so a field typed by a constant is a premise that is always present. Its interval is its default exactly, `Interval(low=value, high=value)`, since nothing else constructs it, and that is what the proof decides relations against it from. A scalar whose root has a default and that a carrier also holds has two sources, and the proof refuses it as `twice`; a scalar whose root has a default factory is fresh, not constant (0011).

## Evidence

In the engine's test program, `Limit` has a default root of 10 and is held by `Low(AtMost[Amount, Limit])` and `High(Beyond[Amount, Limit])` with no default on either: `proof.constants` was `(Limit,)`, `proof.path(Limit)` was `()`, `interval(Limit)` was `Interval(low=Decimal(10), high=Decimal(10))`, and `Low` constructed once per element from the carried `Amount` and the seeded `Limit`. `Reduced(Times[LineTotal, Rate])` with `Rate` a constant of 0.9 had required fields `left` and `right`. `outcomes(interval(Amount), interval(Limit))`, with `Amount` above 0, was `{-1, 0, 1}`, so neither `Low` nor `High` is certain or impossible.

## Consequences

A page declares the constant once and holds it where it is compared. A constant's value is a fact the proof reasons from, so a bound against a constant is decided exactly. Refuted by a constant the deployment must set; that is a `Setting` on a connection, and a relation against it is decided from its bounds.
