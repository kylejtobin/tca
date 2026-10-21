# 0010. A reply holds one fact as its parameter and serializes only its computed fields

Status: accepted

## Context

A `Reply` is made from a fact and tells the caller words computed from it. The fact carries the history and the parties' records and must not leave the program. FastAPI builds the response schema from the model's JSON schema in serialization mode, so the schema and the dump must agree.

## Rejected

A `@model_serializer(mode="wrap")` returning only `model_computed_fields`: a mechanism beside Pydantic's exclusion, with the serialization schema unchecked. `Reply.__init_subclass__` setting `Field(exclude=True)` on each annotated field: a loop and `setattr` in the vocabulary, invisible on the page. A type alias `Held[T] = Annotated[T, Field(exclude=True)]` written per field: a reply field without it would serialize the fact, so the wrong outcome stayed constructible.

## Decision

`class Reply[F: Fact](BaseModel)` with `of: F = Field(exclude=True)` declared once in the base. A page writes `class OrderPaid(Reply[Paid])` and computed fields reading `self.of`. A reply declares no fields of its own. `Route[Q, A]` bounds `A` as `Reply[Fact]`, so the fact a route's reply is made from is read from the reply's generic argument.

## Evidence

`OrderPaid(of=Paid(sku=Sku("tea"))).model_dump_json()` is `{"product":"tea"}`. `model_json_schema(mode="serialization")["properties"]` lists only `product`. `model_json_schema(mode="validation")["required"]` is `["of"]`. `OrderPaid()` raises `missing` at `("of",)`. `OrderPaid(of=Other(sku=...))` raises `model_type` at `("of",)`. `r.of.sku.root` is `"tea"`. The parametrized base's `__pydantic_generic_metadata__["args"]` is `(Paid,)`. A subclass that declares a plain field serializes it; such a field has no producer and the startup check refuses the program.

## Consequences

Unwritable: a field on a reply, a serializer, a hook. The engine reads the reply's fact from the generic argument, the same way it reads an action's `T`. Refuted by a reply that must be made from two facts with no fact holding both; that is a missing fact.
