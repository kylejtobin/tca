---
type: Reference
description: How Pydantic executes TCA construction graphs as the runtime construction substrate. Read before implementing or interpreting any whitelisted construct.
---

# Pydantic Execution Substrate

## Governing Reading

Pydantic is the runtime for TCA. Its annotations compile the construction graph; its constructors execute that graph. Read `model_validate`, `model_validate_json`, `validate_python`, and `validate_json` as constructors. They do not validate a value before the real program; their successful output is the program value.

## Construct Mapping

- `RootModel` constructs a semantic scalar or named collection.
- `BaseModel` constructs products: values, concepts (including the state-transition shape), foreign models, contracts, transformations, actions, routes, and interpreters.
- `Annotated[A | B, Field(...)]` declares a union or ordered union.
- `TypeAdapter` constructs and serializes a bare union or ordered-union alias.
- `BaseSettings` constructs configuration from deployment input.
- Nested annotations create construction edges.
- `Field`, model configuration, and nested shapes define inhabitable values. Program-owned custom validators are not admitted; [construction](construction.md) carries the rule in the representation.
- Aliases, `validation_alias`, and `AliasPath` lift foreign names and wrappers.

## Mandatory Configuration

| Construct substrate | Exact configuration |
|---|---|
| Owned `BaseModel` | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| Semantic `RootModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| Foreign `BaseModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`; `extra` exactly matches the source contract |
| `BaseSettings` | `frozen=True`, `extra="forbid"`, `strict=False`, `validate_default=True`, `revalidate_instances="never"` |
| Effect interpreter | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`, `arbitrary_types_allowed=True` |

Raw nested input constructs recursively. TCA treats existing model instances as prior proofs because every program introduction path uses normal construction; Pydantic does not verify that provenance when revalidation is disabled. `model_construct`, unchecked copying, assignment, `PrivateAttr`, undeclared instance state, and `object.__setattr__` are forbidden proof bypasses. Pydantic freezing is faux immutability under supported APIs, so every semantic constituent uses recursively immutable field types.

The constructor graph is eager: required constituents construct before the outer fact exists. Owned derivations are demand-driven: their declared facts construct when read. Neither requires a mutable current-state reference or a runner that stages domain constructions. The composition root is a named site: `main.py` registers a framework callback once, and that callback evaluates the per-input terminal expression, including read and write interpreters. It is not another declaration form.

`arbitrary_types_allowed=True` appears only on an effect interpreter field typed as an imported non-program-owned standard-library or third-party capability. That field uses `Field(exclude=True, repr=False)`. Provenance is enforced by the import boundary; Pydantic performs only the instance check. The capability is neither semantic proof nor serializable state, and no program-owned arbitrary class is admitted through it.

## Construction Surfaces

- Use the ordinary constructor for already named Python inputs.
- Use `model_validate_json` for serialized JSON.
- Use `model_validate` with `from_attributes=True` for object-shaped foreign input.
- In attribute mode, use the input alias as the source attribute name: `price: Price = Field(alias="px")` reads `source.px`, not `source.price`. `AliasPath` starts from its named attribute; output-only `serialization_alias` does not affect lookup. Do not infer a domain-named source attribute or compensate with a field-copying mapper.
- Respect the input mode, not just the annotation. Under `strict=True`, pass `Side.BUY` to a Python constructor; raw Python `"buy"` is refused. JSON construction accepts `"buy"` and constructs the member. Do not infer Python coercion from JSON acceptance or loosen the semantic model to make both inputs alike.
- Use `TypeAdapter` for a bare union or ordered-union alias.
- Use `model_dump_json` or the declared framework serializer only at a route or effect interpreter.
- Use `@property` for every semantic transformation; its one returned expression follows the closed [transformation](constructs/transformation.md) algebra and constructs its typed result. Model membership does not admit arbitrary method bodies.
- Do not use `@cached_property` on a semantic model because its cache is assignable despite `frozen=True`.
- Use `@computed_field` only to publish a derived contract field; construct its returned semantic value explicitly because Pydantic does not validate computed output.
- Serialize alias-bearing wire models with `by_alias=True`. `validation_alias` and `AliasPath` affect input only; `serialization_alias` affects output only.
- Distinguish computed wire output from reconstruction input; reconstruct with `round_trip=True` or exclude computed output.
- Use `strict=False` for settings: environment text must construct numeric and other typed configuration values. Keep output constraints and immutability; do not copy this input exception into ordinary semantic models.

## Forbidden Substrate Paths

`model_construct`, unchecked model copying, assignment mutation, `PrivateAttr`, undeclared instance state, `Any`, `SkipValidation`, mutable nested values, and unvalidated defaults cannot create or alter a semantic value. Report `ValidationError` as construction refusal, never as a domain witness.

No program-owned custom validator, constructor override, `model_post_init`, or schema hook supplies domain meaning. Pydantic's built-in construction constraints remain the substrate; handwritten validation is not another construct.
