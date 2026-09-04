---
type: Reference
description: Why names are instructions when a language model reads a type.
---

# Semantic Index Types

> Naming is programming.

When a language model consumes a type schema, names stop being inert labels and
become instructions. Field names, descriptions, and variant names participate in
computation.

A **semantic index type** is a type declaration where natural-language tokens
function as computational indices because the consumer interprets them as
meaning-bearing instructions, not structurally inert identifiers.

## What Changes

In traditional runtimes, names are read as identity keys. Consistent renaming
preserves behavior because readers match names, they do not interpret meaning.

With neural consumers, names are read as meaning. Renaming can change output
distribution even when schema structure is unchanged.

```python
# Same structure, different computation signal
churn_risk_tier: RiskTier
x7: RiskTier
```

This is a consumer-level alpha-equivalence failure: structure is preserved, but
semantic behavior shifts.

## Two Channels, One Declaration

A schema consumed by an LLM operates through two channels:

- **Structural channel**: type constraints, validators, decoding constraints.
  Determines what outputs are admissible.
- **Semantic channel**: names, descriptions, variant names. Determines which
  admissible outputs become likely.

Structure defines support. Semantics defines salience.

## The Design Dial

Per field, semantic influence is bounded by structural compression:

`I(N; Y_f) <= H(Y_f) <= log2|V_f|`

Where `|V_f|` is the number of structurally valid values for field `f`.

| Type constraint | Valid outputs | Max semantic influence |
|:---|---:|---:|
| `bool` | 2 | 1 bit |
| 4-variant union | 4 | 2 bits |
| unconstrained `str` | unbounded | unbounded |

Tighter structure narrows semantic bandwidth. Loose structure pushes more work
onto naming.

## Development Discipline: Progressive Hardening

1. Start with precise names and descriptions.
2. Observe failure modes.
3. Harden repeated failures into structure (narrower types, unions, constraints).

Each hardening step moves behavior from soft semantic guidance to hard
structural guarantee.

## Security Consequence

If names are computational instructions, schema text is an attack surface.
Untrusted names/descriptions can function as adversarial indices. Defenses are
the same controls used for instruction channels: provenance, sanitization,
least-privilege exposure, and structural containment.

## Scope

This note states the architectural consequence for TCA systems. The formal
treatment (definitions, formal model, empirical synthesis, and experiment) is
the `sit` source of truth:

- [SIT repository](https://github.com/kylejtobin/sit)
