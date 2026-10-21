# 0030. answer takes the route, the request, the config and the program, and returns the reply

Status: accepted

## Context

The CLI and the HTTP server call the engine once per request. The engine must find the program's actions to prove and run a route, and no run-time reading of generic metadata can be typed as the route's `A`.

## Rejected

`async def answer[Q, A](route: type[Route[Q, A]], request: Q, config: Config) -> A`: the body can only narrow the reply to `type[Reply[Fact]]`, so returning `A` needs a cast, and the program module is not reachable from the route alone.

## Decision

`async def answer(route: type[Route[Request, Reply[Fact]]], request: Request, config: Config, program: ModuleType) -> Reply[Fact]`. The caller holds the program module from the entry point and passes it. The reply's static type is `Reply[Fact]`; its run-time class is `A`.

## Evidence

The CLI called `answer(route, request, deployment, module)` and printed `reply.model_dump_json()`; basedpyright strict reported 0 errors with no cast.

## Consequences

A server kind passes the module it loaded. Refuted by a typed way to read a generic argument as `A` without a cast; none exists in Pydantic 2.13.5 or basedpyright.
