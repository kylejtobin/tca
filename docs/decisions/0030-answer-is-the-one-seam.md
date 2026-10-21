# 0030. answer takes the route, the request, the config and the program, and returns the route, typed by the route's parameters

Status: accepted

## Context

The CLI and the HTTP server call the engine once per request. The engine must find the program's classes to run a route, and a caller that holds a concrete route class should get the concrete reply type back without narrowing.

## Rejected

`async def answer[Q, A](route: type[Route[Q, A]], request: Q, config: Config) -> A`: the body can only narrow the reply to `Reply[Fact]`, so returning `A` needs a cast, and the program module is not reachable from the route alone. Returning the reply alone, which made the reply's fact the engine's end condition. `answer(route: type[Route[Request, Reply[Fact]]], ...) -> Route[Request, Reply[Fact]]`: `Route`'s parameters are invariant, so a concrete `Checkout` is not assignable to it and a test or a kind holding the class cannot call it without a guard.

## Decision

`async def answer[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]], request: Q, config: Config, program: ModuleType) -> Route[Q, A]`. The caller holds the program module from the entry point and passes it. The run ends when the route constructs (0005), and `route.model_validate(run[route])` returns it typed as `Route[Q, A]`, so a server reading `.reply` gets `A`: the CLI, holding routes as `Route[Request, Reply[Fact]]`, gets `Reply[Fact]`; a test holding `Checkout` gets `OrderPaid | OrderRefused`. `prove` and `asked` take the same parameters, so the body needs no narrowing.

## Evidence

The CLI called `answer(route, request, deployment, module)` and printed `answered.reply.model_dump_json()`. The engine's test called `answer(shop.Checkout, request, config(shop)(), shop)` and returned `route.reply` from a function typed `-> shop.OrderPaid | shop.OrderRefused`; basedpyright strict reported 0 errors across the engine and its tests with no cast.

## Consequences

A server kind passes the module it loaded and serializes the route's `reply`. Refuted by nothing.
