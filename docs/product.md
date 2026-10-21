# TCA

A Python framework. The developer writes an application as Pydantic classes and nothing else. The engine constructs them and does four things. This document states who it is for, what it promises, how the work is divided, and the checks that say the promise was kept.

## The customer

- An application developer writing a service that talks to external parties over HTTP, a database, or a queue.
- That developer on day one, with the classes written and no server, who wants to run the program from the shell and see it answer.
- An operator who needs to run one route by hand: replay a checkout against staging, requote a sku, confirm a party is reachable.
- An integrator reading the OpenAPI document, who sees the field descriptions the developer wrote on the classes and nothing written separately for them.
- A model writing that service, given the classes to write and the checker that judges them.
- A reader who knows the business and not the code, reading the program to confirm it says the business.

## The division of responsibility

The developer writes classes:

| the developer declares | as |
|---|---|
| what arrives | a `Request` |
| what an external party says | a `Record`, with the party's field names as aliases |
| what the business concludes | a `Fact` whose fields are the things it was concluded from |
| what the business asks a party | an `Action` whose fields are the fact that intends it |
| what the caller receives | a `Reply[F]` made from the fact `F`, whose computed fields are its words |
| each party | a `Connection` |
| each thing the program does | a `Route[Request, Reply]` |
| the deployment | a `Config` |

The engine does four things: deserialize the request; perform each action and deserialize its response; serialize the reply; open and close clients at startup and shutdown. It constructs the developer's classes in the order their field annotations require. It has no classes and no state of its own.

A class or field on a page that exists for the engine is a defect. A behavior in the engine that the developer should have declared is a defect.

## The promise

- No invalid state is constructible. A rule is a constrained `Scalar` or a union member, so a value the business does not have has no type.
- basedpyright in strict mode checks every reference in the program.
- A broken program fails at startup, naming the record no action hears, the field no class produces, or the cycle.
- A unit test is constructing an instance, or asserting `ValidationError`.
- There is one failure path: `ValidationError` for input and rules, the client's exception for a party that did not answer.
- The developer says each thing once, and says only their business.
- The interface is defined once. `class Checkout(Route[PlaceOrder, OrderPaid])`, with the fields and descriptions on those two classes, is the whole definition. The command line is derived from it by pydantic-settings: `shop checkout --sku tea --quantity 3` constructs `PlaceOrder` and prints `OrderPaid`'s computed fields as JSON; `shop --help` lists routes by docstring and `shop checkout --help` lists fields by description. The HTTP endpoint is derived from it by FastAPI: `POST /checkout` validates the body as `PlaceOrder`, returns 422 with Pydantic's errors, serializes `OrderPaid`, and publishes the OpenAPI document with the same descriptions. Connections come from the environment, `PAYMENTS__URL` and `PAYMENTS__KEY`, for both. Running as CLI, HTTP or both is a deployment choice that changes no class. The developer writes no parser, handler, help string, schema, entry point or output formatter.
- The documentation is the program. Help text is the field descriptions and class docstrings; the same classes produce the reference for every route, record and configuration variable. Documentation cannot drift from the code because it is read from the code.

## The acceptance test

Kept when each of these holds on the demo program and on any program written against the framework.

| # | Check | Pass |
|---|---|---|
| P1 | Search the program for `def`. | Every hit is under `@property` or `@computed_field`. |
| P2 | Run `basedpyright --strict` on the program. | Zero errors. |
| P3 | Delete the action that hears one record. Start the program. | Startup fails naming that record. |
| P4 | Give a developer who has read the Pydantic docs and the demo a second route to write. | They write it without opening the engine. |
| P5 | Give a reader who knows the business the program. | They name what each class is from its name and docstring. |
| P6 | Count the engine's public classes. | None of its own; one entry function per server kind. |
| P7 | Run the program with `--help`, then one route with `--help`. | Every route appears with its docstring; every request field appears with its description; every connection field appears with its environment variable. |
| P8 | Run one route from the shell against mock parties, and post the same request over HTTP. | The shell's output equals the HTTP response body. |
| P9 | Give an operator the program and a staging environment. | They replay a request from the shell without reading the code. |
| P10 | Open `/docs` on the served program and run `shop checkout --help`. | Every field and description in one appears in the other. |
| P11 | Send a value outside a `Scalar` constraint on the command line and in an HTTP body. | Both fail with `ValidationError` naming the field; nothing else is reported. |
| P12 | Run `shop docs`. | A reference for every route, record and configuration variable, assembled from the class docstrings and field descriptions. |

A failed check is a defect in the framework, not in the program.

## What it refuses to be

- Not a validation framework. Validation is Pydantic's; the framework adds no validator.
- Not a workflow engine. There is no step, stage, state machine or plan; the order is the annotations.
- Not a DSL. Every construct is a documented Pydantic feature.
- Not a handler framework. There is no function between the request and the reply.
- Not a CLI framework. There is no command to write; a route is the command, and the command line is derived from the request.
- No escape hatch inside a program. `perform` in a library kind is the only Python that calls a client; anything else that cannot be expressed is a missing class or a missing library kind.
