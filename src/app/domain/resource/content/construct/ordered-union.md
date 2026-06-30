---
name: tca_authorized_construct_ordered_union
description: Build an ordered union, the only legal shape for identity-free foreign data that sometimes fails or says no, including a client that raises where it means no or hands back a marker where it means a fact. MUST be invoked before writing any try/except, error handler, retry, fallback, or None-check, and before any thought of catching ValidationError. Replaces the forbidden forms; if a catch-into-default, a reply parser, a broad except, or a coalesce manufacturing a value is about to appear, stop and build the ordered union instead.
---
# Ordered Union

## Definition

`Annotated[A | B, Field(union_mode="left_to_right")]` over variants in attempt order, for foreign data that carries no identity and is expected sometimes to fail or to say no. The stronger construction is attempted first, the failure variant is last and composes from the input itself, and construction selects the case.

## Required Form

```python
class TapeText(RootModel[str], frozen=True):
    """The venue tape's frame text as received. Unconstrained on purpose: an unparseable frame is any text."""

    root: str


class FrameKind(StrEnum):
    TICK = "tick"
    UNPARSEABLE = "unparseable"


class Tick(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[FrameKind.TICK] = FrameKind.TICK
    price: Price
    quantity: Quantity


class Unparseable(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[FrameKind.UNPARSEABLE] = FrameKind.UNPARSEABLE
    raw: TapeText

    @model_validator(mode="before")
    @classmethod
    def _wrap(cls, data: object) -> object:
        return {"raw": data}


Frame = Annotated[Json[Tick] | Unparseable, Field(union_mode="left_to_right")]

FrameConstructor = TypeAdapter(Frame)


class TapeEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    frame: Frame
```

Fed bytes that parse, `Json` decodes and `Tick` constructs; fed garbage, `Json` refuses and `Unparseable` composes from the input itself. As a field, `frame: Frame` admits garbage as a declared value.

A raising client, modeled the same way:

```python
class LedgerKind(StrEnum):
    BOOKED = "booked"
    UNBOOKED = "unbooked"


class Booked(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    kind: Literal[LedgerKind.BOOKED] = LedgerKind.BOOKED
    exposure: Exposure


class Unbooked(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    kind: Literal[LedgerKind.UNBOOKED] = LedgerKind.UNBOOKED


LedgerReply = Annotated[Booked | Unbooked, Field(union_mode="left_to_right")]

LedgerReplyConstructor = TypeAdapter(LedgerReply)
```

Fed the reply object, `Booked` constructs from its attributes. Fed the exception, `Booked` refuses, and `Unbooked` constructs from its pinned kind.

## Sorting Rules

One question routes every failure: did the domain say no, or did the proof fail? A construction refusal proves nothing, is never modeled, and propagates; catching `ValidationError` manufactures the unproven value. A domain no is a value: this construct. An omission that means a fact is the absence doctrine at a foreign lift, not a failure. A transport-setup signal nothing in the domain reacts to belongs to the binding. Identity-carrying data constructs through the union's discriminator, never by attempt order.

## Replaced Forms

A `try`/`except` producing a default, flag, or partial object manufactures the unproven value construction refused to make. A reply parser inspecting a foreign reply to choose a case restates the selection construction performs. A coalesce (`x or default`) manufactures a value nothing proved.

## Construct-Specific Doctrine

**The wrap.** The one `mode="before"` validator the architecture admits: a single wrapping line on the failure variant that places the bare input under its field name, legal only with a recorded substrate run showing the declarative inventory refuses the shape. One return, constant keys, the input as every value. A marker handed back where it means a fact constructs an identity-only variant the same way.

**The constructor.** The constant beside the alias is the alias's declared constructor, the substrate's `TypeAdapter`, named for the alias it constructs. It defines no structure and decides nothing. As a field on a foreign model, the alias needs no constant: `frame: Frame` admits garbage as a declared value, the `TapeEntry` form above.

**The capture.** Python raises must be captured before construction can receive them. The capture lives in a verb: one call assigned, each declared exception assigned to the same variable, then ordered-union construction from that variable. The capture does not choose a variant, does not construct in an `except` arm, and an undeclared raise propagates as the refusal it is.

## Allowed Patterns

- the `Annotated` alias with `union_mode="left_to_right"`, variants in attempt order, failure last
- the failure variant composing from the input itself through the proven one-line wrap
- `Json[...]` as the stronger construction when the input is serialized
- the `TypeAdapter` constant named for the alias
- the alias as a field on a foreign model
- the capture in a verb feeding the constructor

## Forbidden

- `except ValidationError`, anywhere
- a `try`/`except` producing a default, flag, partial object, or domain variant
- a broad `except` or a second statement in an `except` arm
- `x or default`
- a reply parser: a function, `match`, or `isinstance` deciding a reply's case
- a `RootModel` class created to construct the alias

## Halt Rule

Halt when a client produces a signal or marker not named by its interface, when the failure variant cannot compose from the input through the wrap, or when ordered selection is demanded for data that carries identity. Report the row and the signal: the wire's shapes are not fully modeled, and the table is not finished.
