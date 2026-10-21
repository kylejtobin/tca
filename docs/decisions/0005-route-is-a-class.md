# 0005. A route is a class

Status: accepted

## Context

A program declares what it accepts and what it answers.

## Rejected

`checkout = Route[PlaceOrder, OrderPaid](name=RouteName("checkout"))`: a module-level instance with a `RouteName` scalar. The route's name appeared twice, once as the variable and once as the field, and a module-level instance is not a class the program's reader can find by subclass.

## Decision

`class Checkout(Route[PlaceOrder, OrderPaid]): ...` with no fields of its own. The class name is the business's name; a server kind derives the address or the subcommand from it. The kind holds `request: Q` and `reply: A` (0048), so the request class is read from the field annotation, not from generic metadata.

## Evidence

`Checkout.model_fields["request"].annotation is PlaceOrder`. `Checkout.__pydantic_generic_metadata__` is `{"origin": None, "args": (), "parameters": ()}`, so a route is found among a module's classes as one with no origin and no open parameters.

## Consequences

Unwritable: `RouteName`, a `name` field, a route instance on a page. A reader finds routes by walking a module for `Route` subclasses. Refuted by one contract needing two names; that is two routes.
