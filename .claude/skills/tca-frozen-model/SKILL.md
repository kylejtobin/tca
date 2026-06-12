---
name: tca-frozen-model
description: Build a frozen model, the only legal shape for a composite domain value. MUST be invoked before writing any composite. Replaces the forbidden forms; if a dataclass, NamedTuple, TypedDict, untyped dict shaped like a value, a post-construction check, or a T | None field is about to appear, stop and build the frozen model instead.
---

# frozen model

A frozen model composes already-declared types into one proven product; its existence
is the certificate that every field's constraint held together.

    class SourceLocation(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        file_path: PythonFilePath
        line_number: PositiveLineNumber

    class Smell(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        invariant_name: InvariantName
        message_text: MessageText
        source_location: SourceLocation

A relation between fields is part of the composite proof, and its home is structural:
reparameterize so the relation collapses into a single-field constraint and a
derivation. Hold `line_start` and a `LineCount` (`ge=1`), derive `line_end`, and an
inverted span has no representation:

    class SourceSpan(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        line_start: PositiveLineNumber
        line_count: LineCount

        @cached_property
        def line_end(self) -> PositiveLineNumber:
            return PositiveLineNumber(self.line_start.root + self.line_count.root - 1)

A reparameterization that seems to distort the model is not a license for a validator;
it is the signal that the related fields are their own concept, not yet factored. There
is no asserting validator: a validator that raises is a check riding inside
construction, and the gate denies it.

A composite lifts whole from foreign-shaped data in one construction: the constituents
are proven by coercion inside it, never pre-constructed one scalar at a time beside it,
which restates the work the constructor is already doing.

    stored = StoredObject.model_validate(
        {"object_name": info.name, "object_size": info.size, "object_digest": info.digest}
    )
    view = AccountView.model_validate(orm_row, from_attributes=True)

"May be missing" is never a field. Absence that means something is a choice
(`tca-union`): factor the states, and the axis names what absence means there. A
`T | None` field fuses the absence question into the field and answers nothing. At a
lifting, a foreign key that may be omitted resolves to a default that names what
omission means, so no bare `None` crosses:

    class CaptureWindow(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        depth: BookDepth = BookDepth(50)   # omission means the venue default, named

The contrast that fails the test, subclassing for field reuse: `class Order(PricedThing)`
to share a `price` field. The shared field is already shared as the leaf both models
compose; a base class is a second structure for one meaning.

## Construction discipline

Construction is direct keyword construction: `Quote(price=price, size=size)`. The
constructor is the pipeline: a raw primitive passed where a scalar field stands
constructs that scalar inside the composite's proof, its constraint proven in the same
call, so constructing constituents one by one beside the composite restates work the
constructor owns. `model_validate` and `model_validate_json` belong to the crossings,
where a raw foreign payload arrives whole; a dict assembled by hand and fed to
`model_validate` where keywords express it is a mapper in miniature and is denied. A
coalesce on the way in (`x or default`, a ternary fallback) forges a value nothing
proved: absence is resolved by the absence doctrine, a declared default that names what
omission means or a variant, never an inline default. A check after construction
un-proves the value it guards; the value's existence already answered.

## The row

The spec row this card expands. Every field value is a declared row name; the
gate denies a field the row does not declare and a type the field does not
match. A union variant adds its pin.

    {"construct": "frozen_model", "name": "SourceLocation", "file": "value.py", "fields": {"file_path": "PythonFilePath", "line_number": "PositiveLineNumber"}}
    {"construct": "frozen_model", "name": "Filled", "file": "outcome.py", "fields": {"fill_price": "Price"}, "kind": {"axis": "OrderOutcomeKind", "member": "filled"}}

## Allowed patterns

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`
- every field a declared type: a scalar, a collection of declared elements, a frozen
  model, or a union
- a shared field composed by holding the shared leaf as a field
- a cross-field relation reparameterized into one constrained field plus a derivation
- absence factored into states: a union over a named axis or separate models, never a
  `T | None` field
- derivations implying the model's facts (`tca-derivation`)

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
