# Program Architecture

TCA is not merely a style for writing better models inside an otherwise conventional application. It is a claim about where the program should live. The domain context is the program. Routes expose it. Infrastructure starts it. Services, if they exist at all, are connectors so thin they are almost embarrassing. The app interior is railroaded by constructed certainty — there are no uncertain intermediate states.

---

## The Architectural Inversion

In conventional systems, the service layer is where the program lives. Models are passive DTOs that the service fills, transforms, and interprets. The service maps, coordinates, enriches, and decides. Domain types are bags.

TCA inverts this. The domain models own construction, derivation, classification, projection, and boundary contracts. The interpretation already lives in the modeled context. The app is not layers wrapped around a domain — it is a shell around a proof-carrying context graph.

The inversion has a measurable consequence: the service layer should shrink under pressure from better modeling. If you find yourself writing service methods that compute things from a model's own fields, that computation is a wiring defect. It belongs on the model as a projection. If you find yourself writing adapter code between two models, ask whether `from_attributes` and aliases can collapse the adapter. If you find yourself branching on a tag in service code, a discriminated union can dispatch during construction instead.

---

## Layer Responsibilities

**`main.py`** starts infrastructure: web server, database connections, dependency injection. It does not contain domain logic.

**`api/`** handles transport: routes, middleware, HTTP concerns. One route per context. The route handler receives raw data, hands it to a context-owned contract, and returns the result. It does not interpret, enrich, or compute.

**`domain/context/`** holds the actual program: frozen models, enums, constrained types, projections, and construction graphs. This is where construction, derivation, and program semantics live. The vast majority of the application's logic belongs here.

**`domain/context/api.py`** owns route-specific boundary contracts: request shapes, response projections, error envelopes. These are domain knowledge owned by the context, not transport concerns owned by the route handler.

**`service/`** is optional. When it exists, it is a thin connector — often a single function or a single-method class whose only job is to bridge infrastructure to the domain context. Many applications do not need a meaningful service layer at all.

Each layer is defined as much by what it does not own as by what it does. Routes do not interpret the domain. Services do not compute derivations. Infrastructure does not define contracts. The domain context owns the semantics.

---

## The Context As Program

The context model is not a DTO package. It is the active semantic center of the application: what is known, what can be derived, what contracts are exposed, and what proof obligations are discharged.

A context typically contains:
- Frozen models that represent the domain's core concepts
- Enums that define closed vocabularies
- Constrained types that narrow primitives to domain meaning
- Projections that derive knowledge from proven fields
- Construction graphs that compose proofs into programs
- Boundary contracts for API exposure

Cross-context type usage between different `domain/context/` directories is often correct. The goal is the most precisely modeled world the application can know. Feel free to use a proven type from another context when it increases certainty about the current context's world.

---

## Route Contracts Belong To The Context

Request types, response projections, and route-level boundary contracts belong in `domain/context/api.py`, not in the route handler. The route handler is transport plumbing. The contract is domain knowledge.

A route handler should look something like:

```python
@router.post("/retention/analyze")
async def analyze_retention(request: AnalyzeRetentionRequest) -> RetentionAnalysis:
    return RetentionAnalysis.model_validate(request)
```

`AnalyzeRetentionRequest` and `RetentionAnalysis` are defined in the context, not in the API layer. The route handler is pure transport delegation. If the handler contains logic beyond wiring a request to a construction call and returning the result, that logic likely belongs in the context.

---

## Cross-Context Certainty

Using a type from another context is often the right move when it increases the precision of the modeled world. Artificial boundaries that force translation layers between contexts reduce certainty. Tidy package boundaries are not a goal; the most precisely modeled certain world is.

Cross-context references are right when:
- The shared type represents a genuinely shared domain concept
- Using it directly avoids a translation layer that would introduce information loss
- Both contexts need the same proof about the same thing

Cross-context references indicate a problem when:
- The type means something different in each context (a customer-as-indexed vs. a customer-as-analyzed should be distinct types)
- A context is pulling in an entire dependency graph it does not need
- The sharing creates a coupling that makes independent evolution impossible

The principle is: optimize for the most precisely modeled certain world, not for organizational neatness.

---

## The Service Question

Many applications do not need a meaningful service layer. The service abstraction carries prestige from conventional architecture, where it was the only place for logic to live. In TCA, the domain context already owns the logic. The service layer collapses.

A service is still justified when:
- There is a genuinely irreducible operational concern: streaming, long-running I/O, external system coordination
- The connection between infrastructure and the domain context needs a thin integration shell
- An active operational behavior (catching streaming content, managing websocket state) cannot be expressed as pure construction

Even in these cases, the service should be so thin that it contains no domain interpretation. It connects infrastructure to context and returns proven results.

---

## What This Architecture Refuses

- **No service methods that compute intrinsic derivations.** If a computation depends only on a model's own proven fields, it belongs on the model.
- **No route handlers with domain logic.** The route handler is transport. The domain context owns the meaning.
- **No adapter layers between contexts that could share types directly.** If a translation layer exists only because of organizational tidiness, it is information loss.
- **No helper functions that duplicate dispatch expressible as a discriminated union.** If branching selects behavior based on a tag, a DU should dispatch during construction.
- **No uncertain intermediate states.** The app interior is proven context. Uncertainty belongs at the boundary. Effects belong after proof.
