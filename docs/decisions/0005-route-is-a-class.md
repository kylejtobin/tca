# 0005. A route is a class that holds its request and its reply

Status: accepted

## Context

A program declares what it accepts and what it answers. The engine must know a route's request class to deserialize, and must know when an answer is complete.

## Rejected

`checkout = Route[PlaceOrder, OrderPaid](name=RouteName("checkout"))`: a module-level instance with a `RouteName` scalar. The route's name appeared twice, once as the variable and once as the field, and a module-level instance is not a class the program's reader can find by subclass. `Route[Q, A]` with no fields, its `Q` and `A` read from `__pydantic_generic_metadata__` of the parametrized base with asserts that they are a request and a reply. The reply's fact appearing in the run as the engine's end condition.

## Decision

`class Checkout(Route[PlaceOrder, OrderPaid]): ...` with no fields of its own. The class name is the business's name; a server kind derives the address or the subcommand from it. The kind declares `request: Q` and `reply: A`, so an instance is one answered request. The route is a class of the program like any other: the engine constructs it when the reply exists, and that construction is the end of the run (0021). The request class is `Route.model_fields["request"].annotation`, read by `asked` with a `TypeIs` guard; no metadata is read.

## Evidence

`Checkout.model_fields["request"].annotation is PlaceOrder` and `["reply"].annotation is OrderPaid`. `Checkout.__pydantic_generic_metadata__` is `{"origin": None, "args": (), "parameters": ()}`, so a route is found among a module's classes as one with no origin and no open parameters. `answer` returned a `Checkout` whose `reply.model_dump_json()` was `{"total":"7.50","charges":["ch_1"]}`.

## Consequences

Unwritable: `RouteName`, a `name` field, a route instance on a page. A reader finds routes by walking a module for `Route` subclasses. A server kind serializes `answered.reply`. The proof names a route whose reply cannot exist at `(Checkout, reply)`. Refuted by one contract needing two names; that is two routes.
