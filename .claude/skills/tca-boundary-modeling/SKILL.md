---
name: tca-boundary-modeling
description: Model external interfaces the TCA way. Use when the user is asking about APIs, third-party systems, adapters, webhooks, payloads, wrappers, events, request/response contracts, sockets, or how to handle foreign data.
---

Use this skill when the problem is really about how raw foreign reality should enter the program.

## Outcome

Model the boundary as a staged construction path:

1. mirror the foreign schema
2. absorb any outer wrapper on that same boundary
3. capture live input at the seam
4. lift into owned domain truth

Use the corresponding Pydantic surfaces:

1. `Field(alias=...)` and declarative boundary fields for the foreign contract
2. `model_validator(mode="before")` for irreducible wrapper absorption
3. `model_validate_json` or immediate `model_validate` at the live input seam
4. aliases, `from_attributes`, and staged `model_validate` for foreign-to-domain lift

## Method

1. Name the foreign contract exactly as it exists.
2. Build a boundary model that owns that foreign schema declaratively.
3. Use `Field(...)`, `Annotated`, aliases, constrained types, and the smallest justified seam logic.
4. Keep wrapper normalization on the boundary, not in handlers or services.
5. Keep live transport code thin: raw input in, immediate handoff.
6. Lift from foreign truth into domain truth by construction, not translators.
7. Reach for `model_validator(mode="wrap")` only when the seam must surround inner validation; do not use validator modes as generic cleanup procedure.

## Review standard

Flag these failures:

- adapter classes and translator services
- repeated payload peeling in handlers
- socket loops or routes interpreting business meaning
- dict payloads crossing boundaries instead of named products
- validators or helper code doing work that better field shape, aliases, or an intermediate model could carry
- `field_validator` or `model_validator(mode="after")` used where boundary declaration or `mode="before"` should have solved the seam
