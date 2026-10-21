# 0009. A tagged record union is discriminated

Status: accepted

## Context

A party answers with one of several records and sends a field that says which: `{"status": "succeeded", ...}` or `{"status": "declined", ...}`.

## Rejected

An untagged union `Charged | Declined` validated by smart mode. Errors list every member; selection depends on smart-mode tie-breaking, which Pydantic's documentation says may change between minor releases.

## Decision

Each record declares the tag as a `Literal` field. The union is written once as a type alias on the page: `type ChargeResult = Annotated[Ok | Declined, Field(discriminator="status")]`, and used where the action declares what it hears.

## Evidence

`Heard(RootModel[ChargeResult])`: `{"status":"succeeded","id":"c1"}` constructs `Ok`; `{"status":"declined","reason":"nsf"}` constructs `Declined`; `{"status":"other"}` raises `union_tag_invalid`.

## Consequences

On a page, a `Literal` field appears only on a `Record` whose party sends the tag, and a page never writes a callable `Discriminator`. A library kind reading another party's document with no single tag field uses Pydantic's callable `Discriminator` with a `Tag` per member, as the documentation prescribes for that case; the CLI's schema nodes do (0027). Refuted by nothing found.

