# type-construction-http

Serves a TCA program's routes over HTTP: an ASGI application over the engine's running program, and the server that binds it.

```python
from type_construction.http import Bind, Exposed, FailureStatus, Method, PathPattern, Refusal, serve

serve(
    ShopConfig,
    Bind,
    Refusal(route=checkout, reply=OrderRefused, status=FailureStatus(402)),
    Exposed(route=quote, method=Method.GET, path=PathPattern("/quote/{amount}")),
)
```

- A transport, not part of the engine. The engine knows no protocol; this package adapts Starlette and uvicorn to the engine's running program: `serve`, `ask`, `asks`. They are named in `app.py` and nowhere else.
- `serve(config, bind, *declarations)` reads the program's config and the `Bind` (`HTTP_HOST`, `HTTP_PORT`) from the environment and runs the application there until stopped; `application(config, *declarations, **clients)` is the ASGI application for any server, over a config instance and, in tests, given clients.
- Every route of the program is served. Undeclared, a route is `POST /<name>` and reads its request from the body with `model_validate_json`. `Exposed(route, method, path)` says otherwise: a `GET` route reads its request from the path's parameters, `/quote/{amount}`, and the query, as strings, with `model_validate_strings`; such a request is flat scalars. A request that is not the contract is answered `422` with Pydantic's errors as its body.
- Which replies are failures on the wire, and with what status, the deployment declares: `Refusal(route, reply, status)` per refused reply. A reply carries no status.
- A route without partial replies answers once, as JSON, with the reply's status: `200`, or the refusal's. A route with partial replies answers as a stream of server-sent events: `event: partial` for each partial reply as the program works, then `event: reply` or `event: refused` with the reply.
- Constructing `Http` is the proof, all faults at once: a refusal of a reply its route does not answer, a reply refused twice, a path naming a field the request lacks, a `GET` route whose request is not flat scalars, a route exposed twice, a declaration for a route the program does not declare.
- The program runs for the application's life: its connections are opened when it starts and closed when it stops.
- The transport's own world is `world.py`; the shop in `type-construction-demo` is served by its `main.py` and crossed over a bound socket in its tests.
