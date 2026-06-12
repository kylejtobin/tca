---
name: tca-failure
description: The failure doctrine compiled: refusal versus the domain's no, and the one legal crossing for a wire that says no in refusal's vocabulary. MUST be read before writing any try/except, error handler, retry, fallback, or None-check, and before any thought of catching ValidationError. Replaces the forbidden forms; if a catch-into-default, an error-handler layer, a reply parser, a broad except, or a coalesce manufacturing a value is about to appear, stop and read this card.
---

# failure

One question sorts every failure: **did the domain say no, or did the proof fail?**

The proof's refusal is construction throwing. No value exists, nothing was proven,
and the refusal is not a domain meaning: it is never modeled, never caught into a
value, never defaulted. `ValidationError` is the refusal's name on this substrate;
catching it manufactures the unproven value the architecture exists to forbid. The
refusal propagates, and the program does not continue past it.

The domain's no is the opposite in every respect: a fact the domain asserts, so it
is a union variant with its own payload and pinned identity, constructed and proven
like any other fact. The consumer reads it; nothing re-derives it from a flag.

## The railroad

When a crossing is expected to fail sometimes, the failure is a domain case with a
constructible home: the ordered union (`tca-boundary`). The stronger construction is
attempted first; the failure variant catches what refuses it; the conversion from
refusal to fact is declared, never caught.

## The wire that says no in refusal's vocabulary

A declared client answers in declared types and raises declared signals, so both of
the wire's shapes are known, and known foreign shapes are modeled, never parsed:

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

Fed the answer, `Carried` lifts the payload declaratively and proves it inside its
own construction. Fed the signal, `Carried` refuses (nothing to lift), the refusal
falls through the railroad, and `NotFound` composes from its pinned identity.
Construction is the router; the shapes are the parser; an empty payload constructs
as the legal empty value it is, never forged by a default.

## The capture

Python will not hand a raise to a constructor, so the verb owns the capture
(`tca-consistency-model`), and the gate holds it to exactly this shape:

    try:
        raw: object = await self.store.get(name.root)
    except ObjectNotFoundError as signal:
        raw = signal
    return GetReplyCrossing.model_validate(raw).root

One call assigned; each declared signal reassigned as the arrived value; the
crossing constructed from whatever arrived. The capture converts nothing, decides
nothing, defaults nothing. An undeclared raise propagates as the refusal it is.

## Forbidden

- A `try`/`except` converting a refusal into a default, a flag, or a partial object.
- A caught `ValidationError`, anywhere, ever.
- A reply parser: a function, a `match`, or an `isinstance` deciding a reply's case.
- A catch arm constructing the domain's answer inline: conversion is the railroad's.
- A broad `except`, a second statement in an arm, a retry or fallback wearing a catch.
- A coalesce (`x or default`) manufacturing a value nothing proved.

Build exactly these patterns. Never invent an exception. If a failure fits no form
here, the model is not finished: report the gap.
