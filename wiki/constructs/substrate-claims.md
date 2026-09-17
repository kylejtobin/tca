---
type: Reference
description: The Pydantic facts the doctrine rests on, each established by a run against the pinned version.
---

# Substrate Claims

A claim about what Pydantic or basedpyright does is a claim about what proof a constructor actually gives. It is settled once, by the doctrine author, by running the declared shape against the pinned version, and it never appears in a program as a test. The facts below were established on Pydantic 2.13.5 and basedpyright 1.39.10.

## Governing Reading

Pydantic is the runtime for TCA. Its annotations compile the construction graph; its constructors execute that graph. Read `model_validate`, `model_validate_json`, `validate_python`, and `validate_json` as constructors: their successful output is the program value. The constructor graph is eager, required constituents construct before the outer fact exists; owned derivations are demand-driven, their facts construct when read.

## Mandatory Configuration

| Construct substrate | Exact configuration |
|---|---|
| Owned `BaseModel` | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| Semantic `RootModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| Foreign `BaseModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`; `extra` exactly matches the source contract |
| `BaseSettings` | `frozen=True`, `extra="forbid"`, `strict=False`, `validate_default=True`, `revalidate_instances="never"` |
| Effect interpreter | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`, `arbitrary_types_allowed=True` |

`arbitrary_types_allowed=True` appears only on an effect interpreter field typed as an imported capability, with `Field(exclude=True, repr=False)`. The capability is neither semantic proof nor serializable state.

## Established Facts

- `frozen=True` refuses field assignment on `BaseModel` and `RootModel` alike, whether set by class keyword or `model_config`. Freezing is shallow: a `list` or `dict` field mutates in place, and the dict under a frozen `RootModel[dict[K, V]]` mutates in place, so no recursively immutable keyed association exists on this substrate. `Mapping` annotations construct a `dict`; `MappingProxyType` has no schema.
- `@cached_property` on a frozen model is assignable; `@property` and fields are not. A cached derivation is a proof that can be replaced.
- `PrivateAttr` assignment, `object.__setattr__`, `model_construct`, and `model_copy(update=...)` all bypass constraints.
- An unfrozen model without `validate_assignment` stores an unproven value on assignment.
- `revalidate_instances="always"` with `extra="forbid"` refuses a subclass instance in a parent-typed field. With `"never"`, the subclass instance is kept in Python and its identity is lost through JSON at a parent-typed field.
- An undiscriminated union of identical shapes reconstructs as the first variant through JSON. Structurally disjoint variants select correctly in Python and JSON mode and round-trip. A discriminated alias with a defaulted `Literal` pin serializes the pin, recovers the variant, and reports failure on the claimed variant only.
- `union_mode="left_to_right"` honors declared order on overlapping shapes and refuses when no variant constructs. Attempt order absorbs every refusal of the strong variant, a constraint failure as much as a decode failure.
- `strict=True` refuses `Price("101.50")` in Python mode; JSON mode accepts a numeric string for `Decimal`. A bare `StrEnum` field under strict refuses the raw string in Python mode and accepts it in JSON mode. `BaseSettings` with `strict=True` refuses a numeric field from the environment.
- `validate_default=True` refuses an invalid default; without it the invalid default passes.
- `AliasPath` lifts a nested wrapper whole. With `from_attributes=True` the alias is the attribute name read from the object. `AliasPath("root", 0)` under `from_attributes` reads index zero of a `RootModel` tuple and reports `missing` on an empty tuple. Output uses field names unless `by_alias=True`; `validation_alias` does not affect output.
- `@computed_field` output is not validated. Under `extra="forbid"` a model's own dump with computed fields does not reload; `round_trip=True` omits them. A contract therefore carries computed fields only for facts derived from its own fields.
- Pydantic's JSON parser keeps the last of duplicate object keys silently, so dictionary uniqueness proves nothing about the source.
- A self-referential model with a recursive `@property` resolves to depth 301 without a loop.
- basedpyright reads a same-named `@property` across a bare union without narrowing, reports an error when one variant lacks it, checks `match` with `assert_never` exhaustive on a bare union, accepts a child where the parent is typed, and narrows a discriminated alias on its `kind`.
