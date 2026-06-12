---
name: tca-boundary
description: Build a boundary model, the only legal crossing for foreign data, or an ordered union for identity-free data that sometimes fails, including a client that raises where it means no. MUST be invoked before touching any API payload, file format, message, response, or raising client call. Replaces the forbidden forms; if a mapper, adapter, DTO, translator, json.loads dict, a field-copying function, a try/except around construction, or a reply parser over a raising client is about to appear, stop and build the crossing instead.
---

# boundary model

A boundary model takes foreign-shaped data and produces domain truth in one
construction; the same model facing outward is the API contract.

    class HookToolInputBoundary(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        file_path: PythonFilePath = Field(alias="filePath")
        source_text: FileSourceText = Field(alias="sourceText")

    class HookEventBoundary(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        tool_name: ToolName
        tool_input: HookToolInputBoundary

The first form that expresses the crossing is the form: a rename is `Field(alias=...)`;
nested foreign structure is a nested boundary model; a serialized payload enters by
`model_validate_json`, an object by `from_attributes=True`. A transport envelope burying
the payload under a key is crossed by exactly this, with only the key changed:

    @model_validator(mode="before")
    @classmethod
    def _payload(cls, data: dict) -> dict:
        return data["payload"]

That validator is one returned index and nothing else; it never renames, never
restructures, never computes, never branches. It lifts data only: a live handle's home
is the consistency model (`tca-consistency-model`).

A foreign key that may be omitted is resolved here, at lifting: a default that names
what omission means, or a variant when omission means a different fact. A bare `None`
never crosses into the domain.

When the crossing is expected to fail sometimes, the failure is a domain case, never a
`try`/`except`: the result is an ordered union, stronger construction first, the
failure variant last, composed from the payload itself, the one fact that cannot fail
to exist. The conversion from refusal to fact is declared, never caught, and the
failure variant pins its kind like any variant (`tca-union`):

    class Unparseable(BaseModel):
        model_config = ConfigDict(frozen=True)
        kind: Literal[FrameKind.UNPARSEABLE] = FrameKind.UNPARSEABLE
        raw: RawPayloadText

        @model_validator(mode="before")
        @classmethod
        def _wrap(cls, data: object) -> object:
            return {"raw": data}

    Frame = Annotated[Json[Parsed] | Unparseable, Field(union_mode="left_to_right")]

    class FrameCrossing(RootModel[Frame], frozen=True):
        pass

Ordered selection is legal exactly here and nowhere else, where foreign data carries
no identity to discriminate on; everywhere identity is in the data, the discriminated
union rules (`tca-discriminated-union`).

A near-miss seen in the wild, labeled: a foreign object graph (an `ast` walk, a DOM
traversal, a reflection sweep) declared "the sanctioned procedural crossing" of a
boundary model. That sanction does not exist. It is a mapper dressed in this skill's
vocabulary, and a premise or docstring arguing for it is the verdict against it. The
boundary model's only procedure is the one-returned-index validator above; a crossing
that needs a walk is a meaning no construct here carries, and its one legal output is
the gap row. The same near-miss returns without the slogan as "findings are
constructed at the membrane", or as the walk simply unmentioned while its outputs
appear typed: the walk relocated or omitted is the walk still, and the gap row is
still its one legal output.

## The row

The spec row this card expands. Fields are the domain-side names; every value a
declared row. Boundary rows live in the context's `api.py`.

    {"construct": "boundary", "name": "HookEventBoundary", "file": "api.py", "fields": {"tool_name": "ToolName", "tool_input": "HookToolInputBoundary"}}

An expected-failure crossing is its own row, over a union whose variants are
modeled in attempt order, failure last; the gate requires the `Annotated`
alias, the exact order, and `union_mode="left_to_right"`, and only in `api.py`:

    {"construct": "union", "name": "Frame", "file": "api.py", "axis": "FrameKind", "members": ["parsed", "unparseable"], "variants": ["Parsed", "Unparseable"]}
    {"construct": "ordered_union", "name": "FrameCrossing", "file": "api.py", "over": "Frame"}

Rendered, the row is the envelope already shown above: the stronger construction is
attempted first, the failure variant composes from the payload itself (the one fact
that cannot fail to exist), and identity is minted by the defaulted pins, so the wire
that carried no identity produces a fact that carries it everywhere after. As a field,
the crossing rides a boundary model, and garbage lands declared:

    class CaptureBoundary(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        frame: FrameCrossing                  # garbage lands as Unparseable, declared

The contrast, the two failures never confused: an *unexpected* `ValidationError` is the
proof refusing, and catching it manufactures the unproven value; it propagates. The
*expected* failure is the last variant above, declared, arriving as a value.

## The wire's signal

A client that raises where it means no is the same crossing in a different costume,
and it rides the same railroad (the full doctrine is the failure card, `tca-failure`).
Both of the wire's shapes are known, so both are modeled: the answering shape lifts
its payload declaratively, and the no is an identity-only variant composing from its
pin. Fed the signal, the answering shape refuses, and the refusal falls through;
construction is the router, and no function inspects the reply to decide its case.

    class Carried(BaseModel):
        model_config = ConfigDict(frozen=True, from_attributes=True)
        kind: Literal[GetReplyKind.CARRIED] = GetReplyKind.CARRIED
        data: ObjectBytes

    class NotFound(BaseModel):
        model_config = ConfigDict(frozen=True, from_attributes=True)
        kind: Literal[GetReplyKind.NOT_FOUND] = GetReplyKind.NOT_FOUND

    GetReply = Annotated[Carried | NotFound, Field(union_mode="left_to_right")]

    class GetReplyCrossing(RootModel[GetReply], frozen=True):
        pass

    {"construct": "union", "name": "GetReply", "file": "api.py", "axis": "GetReplyKind", "members": ["carried", "not_found"], "variants": ["Carried", "NotFound"]}
    {"construct": "ordered_union", "name": "GetReplyCrossing", "file": "api.py", "over": "GetReply"}

The raise becomes a value in the verb's capture (`tca-consistency-model`), three lines
that decide nothing; the crossing constructs from whatever arrived, and the bare union
travels the graph.

The crossing takes the foreign payload whole: `model_validate` on the arrived object,
`model_validate_json` on the arrived bytes. A dict assembled field by field from a
foreign result and fed to `model_validate` is the mapper this card replaces: lift
whole, or construct directly with keywords and let coercion prove the constituents. No
coalesce mints data the wire did not carry; an omissible key is resolved at the field,
by the absence doctrine, declared.

## Allowed patterns

- frozen model, `extra="forbid"`, every field a declared domain type
- `Field(alias="foreign_name")` for every rename
- a nested boundary model for every nested foreign structure
- `model_validate_json` for serialized payloads; `from_attributes=True` for objects
- the one-returned-index `mode="before"` validator, only the key changed
- an omitted foreign key resolved at lifting: a default naming what omission means, or
  a variant when omission means a different fact
- an ordered union (`union_mode="left_to_right"`) for an expected-failure crossing, its
  last variant composing the failure from the payload itself

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
