# TCA Core Frame

The main failure mode is not misunderstanding TCA in chat. The main failure mode is generation drift while writing code.

Do not substitute your current confidence for this frame. Long-horizon reasoning drifts toward default training. Repeated self-reflection is part of the architecture because the model is not a trustworthy judge of its own alignment over time.

The universal TCA defaults are:

- the type system is the semantic layer
- the model is the program
- construction is proof
- derivation extends proof
- uncertainty must become typed possibility space, not procedural control state
- procedure belongs only at irreducible seams
- every error is a design error; the fix is more modeling, never less
- the preferred Pydantic surfaces are `RootModel`, focused `BaseModel`, `Field(...)`, `Annotated`, aliases, `Literal`, `Field(discriminator=...)`, `from_attributes`, `model_validate`, `model_validate_json`, `@computed_field`, and `@cached_property`

## Fight Procedural Fallback

Watch for these signs:

- module-level helper functions coordinating domain work
- service methods, helpers, or coordinators that map, enrich, branch, classify, or sequence what models should own
- `if`/`elif` or `match` dispatch on tags, types, or categories
- intermediate dictionaries or adapter layers between named types
- derivations performed outside the model that owns the proven fields
- validators or helper code doing work that `Field(...)`, `Annotated`, aliases, `from_attributes`, `RootModel`, focused `BaseModel`, `Literal`, discriminated unions, or projections should have carried

Default fix:

- strengthen the model
- use `RootModel` and focused `BaseModel` to own named concepts
- use `Field(...)`, `Annotated`, aliases, `model_validate`, and `from_attributes` for declaration and wiring
- use enums, `Literal`, and `Field(discriminator=...)` for classification
- use `@computed_field`, `@cached_property`, and `@property` for intrinsic derivation
- keep procedure only at irreducible seams

## Fight Flat Modeling

Watch for these signs:

- bare `str`, `dict`, `list`, `Any`, `object`, or loose primitives for named domain concepts
- dictionaries crossing boundaries without named products
- string categories that should be enums or `Literal` tags
- unstructured blobs where the cases or fields are already known
- generic containers where the domain has a sharper shape
- status or control state carried as strings, flags, or dict payloads when the cases should be typed

Default fix:

- name the concept
- build `RootModel` wrappers, focused products, enums, and discriminated unions
- prefer constrained or domain-specific types over bare primitives
- prefer immutable shapes

## Validator Discipline

Use validator language precisely:

- prefer `Field(...)` and `Annotated` metadata before validators
- use `model_validator(mode="before")` for irreducible boundary normalization
- use `model_validator(mode="wrap")` only when the seam must surround inner validation
- use `model_validator(mode="after")` only for integrity that truly belongs after construction
- use `field_validator` only when the proof cannot be carried more declaratively on the field itself

Do not treat validators as forbidden. Treat them as tightly scoped Pydantic surfaces whose legitimacy depends on ownership and irreducibility.

## Build The Program The TCA Way

- start from the app world and model everything the program needs to know
- the domain context owns the program
- API and service layers are transport and plumbing, not the home of logic
- the model is the program: construction, `model_validate`, `model_validate_json`, classification, derivation, projection
- unknown outcomes are still representable states: success, failure, pending, retry, review, and multi-case results should be typed
- construct certainty, then derive further certainty
- a seam is acceptable only when it normalizes foreign input into owned truth and cannot be eliminated by stronger modeling
- seams must be irreducible, contained, terminal, and justified

## Review Standard

When reviewing or auditing edits:

- prioritize structural failures over style
- call out procedure where structure should exist
- call out flat primitives where domain types should exist
- call out unmodeled uncertainty where a possibility space should exist
- call out seam inflation where operational code becomes the semantic center
- name the exact construct introduced
- say what stronger Pydantic construct or model move should replace it
- do not recommend casts, suppressions, or workarounds

## Safety standard

- hooks are part of the architecture, not optional polish
- if a hook forces reconsideration, prefer the hook's warning over your own confidence
- do not reason yourself out of anti-drift safeguards

Every error is a design error. The fix is always more modeling. Never less.
