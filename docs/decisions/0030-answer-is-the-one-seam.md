# 0030. answer takes the route, the request, the deployment and the proof, and returns the route, typed by the route's parameters

Status: accepted

## Context

The CLI and the HTTP server call the engine once per request. The engine must know where every class of the route lives, which the proof decided at startup, and a caller that holds a concrete route class should get the concrete reply type back without narrowing.

## Rejected

`async def answer[Q, A](route: type[Route[Q, A]], request: Q, config: Config) -> A`: the body can only narrow the reply to `Reply[Fact]`, so returning `A` needs a cast, and the program module is not reachable from the route alone. Returning the reply alone, which made the reply's fact the engine's end condition. `answer(route: type[Route[Request, Reply[Fact]]], ...) -> Route[Request, Reply[Fact]]`: `Route`'s parameters are invariant, so a concrete route is not assignable to it. `answer(route, request, config, program)` taking the module and proving it inside, cached per process: the proof recomputed or hidden in a memo on every call.

## Decision

`async def answer[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]], request: Q, deployment: Config, proof: Proof) -> Route[Q, A]`. The server computes `proof = proven(module)` once at startup (0055) and passes it to every answer with the deployment it constructed from the environment. The run asks the proof where each class lives and which classes the route builds, and ends when the route constructs (0005); `route.model_validate(root.have[route])` returns it typed as `Route[Q, A]`, so a server reading `.reply` gets `A`: the CLI, holding routes as `Route[Request, Reply[Fact]]`, gets `Reply[Fact]`; a test holding `Operation` gets `Answered`.

## Evidence

The CLI called `answer(route, request, deployment(), proof)` inside `opened(deployment())` and printed `answered.reply.model_dump_json()`, `{"name":"tea","words":["yes","yes"]}`. The engine's tests called `answer(Operation, request, config(PROGRAM)(), proven(PROGRAM))` and read `.reply.of.total.root`, `5.00`. basedpyright strict reported 0 errors across the engine, the CLI and their tests with no cast.

## Consequences

A server kind proves the program once, holds the proof, and passes it with the deployment to every answer. Refuted by nothing.
