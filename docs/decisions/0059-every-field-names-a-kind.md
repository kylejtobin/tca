# 0059. Every field names a kind, what arrives is data, and a program has one deployment

Status: accepted

## Context

A field annotated with a bare primitive carries no rule and no name; a fact holding an enumeration or `None` has no class for the absent case; a request holding a fact holds what cannot arrive on a command line or in a body; a config holding a business value mixes the deployment with the business; a program with two deployments or none has no one environment to read. Each was a page the smell check might catch and the proof did not.

## Rejected

Leaving these to the smell check, which runs on a program's source and not on a class, and to the checker, which accepts a bare `int`.

## Decision

Three reads of every declared class's fields. `unmodeled`: a member of a field's annotation that names no kind the class may hold is refused at `(class, field)`: a model is a kind anywhere; an enumeration is data on a carrier, a connection or a config; a `Literal` or `None` is data on a record only; a relation's ordering field and a derivation's root, the kind's own computed fields, are exempt, and a scalar's root is the primitive by definition. `boundary`: a request or a value holds scalars, values and tuples of them, since that is what arrives; a config holds connections and settings and a connection holds settings, since that is what the deployment sets. `deployment`: a program declares exactly one `Config`, or is refused as `config` at the program's name. What the proof accepts the command line renders, so nothing fails at the prompt that could fail at startup.

## Evidence

In the program with the faults: `Bare(Fact)` with `count: int` was refused as `unmodeled` at `("Bare", "count")`, "Bare.count is a bare int; write a Scalar over it, or a class for the absent case"; `Direct(Request)` with `cheap: Cheap` as `boundary` at `("Direct", "cheap")`; `Parties(Config)` with `limit: Limit` as `boundary` at `("Parties", "limit")`; the module, declaring `Parties` and `Backups`, as `config` at `("type_construction_engine.faults",)`, "declares 2 Config classes". The command line's test program, with a request holding scalars, an enumeration, a value and two tuples, was proven and rendered every option.

## Consequences

Unwritable: a bare primitive, an enumeration or `None` on a fact; a fact on a request; a scalar on a connection; a second config. Refuted by a field a kind cannot express; that is a missing kind.
