# 0010. A reply holds one fact as its parameter and serializes only its computed fields

Status: accepted

## Context

A `Reply` is made from a fact and tells the caller words computed from it. The fact carries the history and the parties' records and must not leave the program. FastAPI builds the response schema from the model's JSON schema in serialization mode, so the schema and the dump must agree. A route's bound on its reply, `Reply[Fact]`, must admit a reply of any fact.

## Rejected

A `@model_serializer(mode="wrap")` returning only `model_computed_fields`: a mechanism beside Pydantic's exclusion, with the serialization schema unchecked. `Reply.__init_subclass__` setting `Field(exclude=True)` on each annotated field: a loop and `setattr` in the vocabulary, invisible on the page. A type alias `Held[T] = Annotated[T, Field(exclude=True)]` written per field: a reply field without it would serialize the fact, so the wrong outcome stayed constructible. `class Reply[F: Fact]` in the new generic syntax: basedpyright infers `F` invariant from the field, so `OrderPaid` is not a `Reply[Fact]` and a route's bound refuses it; `of: Final[F]` does not change the inference.

## Decision

`F_co = TypeVar("F_co", bound=Fact, covariant=True)` and `class Reply(BaseModel, Generic[F_co])` with `of: F_co = Field(exclude=True)` declared once in the base. A page writes `class OrderPaid(Reply[Paid])` and computed fields reading `self.of`. A reply declares no fields of its own. `Route[Q, A]` bounds `A` as `Reply[Fact]`, which a covariant `F` admits. The fact a reply is made from is `Reply.model_fields["of"].annotation`.

## Evidence

`OrderPaid(of=Paid(sku=Sku("tea"))).model_dump_json()` is `{"product":"tea"}`. `model_json_schema(mode="serialization")["properties"]` lists only `product`. `model_json_schema(mode="validation")["required"]` is `["of"]`. `OrderPaid()` raises `missing` at `("of",)`. `OrderPaid(of=Other(sku=...))` raises `model_type` at `("of",)`. `r.of.sku.root` is `"tea"`. `OrderPaid.model_fields["of"].annotation is Paid`. With the covariant `TypeVar`, `class Checkout(Route[PlaceOrder, OrderPaid])` type-checks under basedpyright strict; with `class Reply[F: Fact]` it is refused as invariant, with and without `Final`. A subclass that declares a plain field serializes it; such a field has no producer and the startup check refuses the program.

## Consequences

Unwritable: a field on a reply, a serializer, a hook, `Reply` in the new generic syntax. The engine reads the reply's fact from the field annotation. Refuted by a reply that must be made from two facts with no fact holding both; that is a missing fact.
