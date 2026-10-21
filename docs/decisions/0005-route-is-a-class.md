# 0005. A route is a class

Status: accepted

## Context

A program declares what it accepts and what it answers.

## Rejected

`checkout = Route[PlaceOrder, OrderPaid](name=RouteName("checkout"))`: a module-level instance with a `RouteName` scalar. The route's name appeared twice, once as the variable and once as the field, and a module-level instance is not a class the program's reader can find by subclass.

## Decision

`class Checkout(Route[PlaceOrder, OrderPaid]): ...` with no fields. The class name is the business's name; a server kind derives the address or the subcommand from it.

## Evidence

`Checkout.__mro__` contains a parametrized base whose `__pydantic_generic_metadata__["args"]` is `(PlaceOrder, OrderPaid | OrderUnpaid)`. `Checkout.__pydantic_generic_metadata__` itself is `{"origin": None, "args": (), "parameters": ()}`; the arguments are read from the base.

## Consequences

Unwritable: `RouteName`, a `name` field, a route instance. A reader finds routes by walking a package for `Route` subclasses. Refuted by one contract needing two names; that is two routes.
