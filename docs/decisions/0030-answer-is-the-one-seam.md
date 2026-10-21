# 0030. answer takes the route, the request, the config and the program, and returns the route

Status: accepted

## Context

The CLI and the HTTP server call the engine once per request. The engine must find the program's classes to run a route, and no run-time reading can be typed as the route's `A`.

## Rejected

`async def answer[Q, A](route: type[Route[Q, A]], request: Q, config: Config) -> A`: the body can only narrow the reply to `Reply[Fact]`, so returning `A` needs a cast, and the program module is not reachable from the route alone. Returning the reply alone, which made the reply's fact the engine's end condition.

## Decision

`async def answer(route: type[Route[Request, Reply[Fact]]], request: Request, config: Config, program: ModuleType) -> Route[Request, Reply[Fact]]`. The caller holds the program module from the entry point and passes it. The run ends when the route constructs (0048), and that instance is returned; a server reads `.reply`, whose static type is `Reply[Fact]` and whose run-time class is `A`.

## Evidence

The CLI called `answer(route, request, deployment, module)` and printed `answered.reply.model_dump_json()`; basedpyright strict reported 0 errors with no cast.

## Consequences

A server kind passes the module it loaded and serializes the route's `reply`. Refuted by a typed way to read a generic argument as `A` without a cast; none exists in Pydantic 2.13.5 or basedpyright.
