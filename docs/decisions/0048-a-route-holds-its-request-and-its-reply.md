# 0048. A route holds its request and its reply; constructing it ends the run

Status: accepted

## Context

The engine must know a route's request class to deserialize, and must know when an answer is complete. `Route[Q, A]` with no fields left both to Pydantic's generic metadata.

## Rejected

Reading `Q` and `A` from `__pydantic_generic_metadata__` of the parametrized base, with asserts that they are a request and a reply. An engine-side end condition, the reply's fact appearing in the run.

## Decision

`Route[Q, A]` declares `request: Q` and `reply: A`. An instance is one answered request. The route is a class of the program like any other, so the passes construct it when the reply exists, and that construction is the end of the run: `answer` returns the route instance, and a server reads `.reply`. The request class is `Route.model_fields["request"].annotation`, read by `asked` with a `TypeIs` guard; no metadata is read. `Reply`'s fact is a covariant type variable, declared the old way because the new syntax infers invariance for a field, so the bound `A: Reply[Fact]` admits `Reply[Paid]`.

## Evidence

`class Checkout(Route[PlaceOrder, OrderPaid])` gave `Checkout.model_fields["request"].annotation is PlaceOrder` and `["reply"].annotation is OrderPaid`. With `Reply` declared `class Reply[F: Fact]`, basedpyright refused `OrderPaid` for the bound `Reply[Fact]` as invariant; `Final[F]` did not change that; `F_co = TypeVar("F_co", bound=Fact, covariant=True)` with `class Reply(BaseModel, Generic[F_co])` was accepted, and Pydantic still required `of`, excluded it from the dump and refused another fact's instance as `model_type`. `answer` returned a `Checkout` whose `reply.model_dump_json()` was `{"total":"7.50","charges":["ch_1"]}`.

## Consequences

A page writes a route with no fields, as before; the two fields are the kind's. A server kind serializes `answered.reply`. The proof names a route whose reply cannot exist at `(Checkout, reply)`. Refuted by a route that answers without a reply; there is none.
