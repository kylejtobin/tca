# TCA Architecture Design

**Status:** Architectural foundation for detailed design  
**Owner:** Kyle Tobin  
**Date:** October 30, 2026  
**Product:** [TCA Product Definition](../product.md)

This document establishes the executable model, native responsibility allocation, and requirements for detailed design. The selected foundations are Pydantic, FastStream, and NATS/JetStream. Detailed design resolves their concrete integration and delivers the artifacts and evidence in section 9.

## 1. The typed graph is the program

TCA is a declarative application framework. Its program is a graph of composable Pydantic business types and explicit relationships: values, computations, decisions, prerequisites, capabilities, and outcomes. The graph expresses business meaning once. TCA derives native construction and messaging bindings from it and interprets the remaining decisions needed to pursue intent and justify effects.

The architecture follows this dependency:

**Authored typed graph → derived construction and messaging bindings → established native guarantees → justified effects and conclusions.**

Pydantic establishes value semantics through complete native construction. FastStream binds typed receiving and publishing contracts, lifecycle, and dependency injection. NATS subjects and permissions realize addressing and controlled ingress; JetStream retains evidence and commitments and delivers work durably. TCA consumes those guarantees rather than independently reconstructing them.

The graph is the business ontology, including dependency and execution relationships. NATS subjects project its addressable subjects and occurrences into a hierarchical messaging namespace. That namespace is an executable projection, not a second ontology or a complete representation of every edge. Conditional demand and business decisions remain declared semantics.

NATS/JetStream is required for execution. World modeling and declaration inspection remain ordinary Python library operations. Development uses an app dev container and one persistent NATS container.

## 2. Architectural principles

1. **Author meaning once.** Business types and relationships are authoritative; bindings and internal graph representations are derived.
2. **Model guarantees before procedure.** Encode invariants and prerequisites in reusable types and declaration structure; establish them at owning boundaries.
3. **Preserve native construction.** Pydantic determines each boundary's actual returned value or failure, including new consumer construction.
4. **Realize relationships natively.** Use construction, addresses, subscriptions, permissions, and native storage/delivery contracts wherever they establish the required relationship.
5. **Consume established guarantees.** Interpretation relies on verified bindings and boundary results instead of repeating their implementation.
6. **Separate validity, demand, and permission.** A valid or available value alone does not justify acquisition or an external operation.
7. **Preserve scope and history.** Type identity, business subject, occurrence identity, message identity, current knowledge, and committed justification remain distinct.
8. **Retain uncertainty and independent progress.** Missing, invalid, disputed, failed, or uncertain dependencies affect only work that relies on them.
9. **Respect external authority.** Provider permissions, transactions, completion evidence, and repeat safety bound effects and recovery.
10. **Resolve choices with evidence.** Name native guarantees, integration requirements, residual semantics, assumptions, and executed verification.

## 3. Authoring and binding the graph

| Authored element | Meaning | Derived realization |
|---|---|---|
| Pydantic business types and world compositions | Values, invariants, computations, decisions, and outcomes | Native construction boundaries, schemas, and located errors |
| Supplying and consuming relationships | Which occurrence supplies each dependency | Scoped bindings and typed receiving contracts |
| Source and subject relationships | Accepted ingress and business correlation | NATS addressing, subscription bindings, and permission requirements |
| Conditional dependencies and capability contracts | What is pursued and what permits an effect | Dependency interpretation and typed work delivery |
| Member identity and completion | Distinct members, repetition subjects, and collection closure | Scoped occurrence addresses and supported member progression |
| Public extensions and interface contracts | Additional semantics, adapters, and inputs | Integration through the same graph and foundations |

Distinguish type definitions from runtime realizations. A type defines value semantics; a business subject identifies what the value concerns; an occurrence identifies a realization in scope. Matching types or payloads do not create sharing. Declare supplying relationships explicitly where structure does not establish them unambiguously.

Bindings are derived at program loading or pursuit activation as the required subject values become available. Resolve references, ambiguity, native defaults, alternatives, and collection scopes together. Internal graph structures are generated representations; developers do not maintain a parallel registry of nodes, operations, or workflow steps.

Use reusable world types and value operations to establish prerequisites and meaningful alternatives with minimal application-specific validator boilerplate. Typed decision results can be required by consumers; their invariants, subjects, and supplying occurrences remain explicit.

Each consumer declares the evidence it pursues, conditional dependencies, acquisition closure, and acceptance of omission. Native defaults define omission during construction, not acquisition policy. Selection distinguishes recognition of supplied union values from choosing a path to pursue. Specify these semantics without assuming eagerness, speculative acquisition, or a universal selection strategy.

Authoring restrictions require a product-semantic justification against less restrictive native composition or explicit relationships. Scenarios test the general contract and introduce no framework policy.

## 4. Native realization and residual responsibilities

| Responsibility | Native realization | TCA responsibility |
|---|---|---|
| Value construction and invariants | Pydantic annotations, constraints, composition, validators, unions, defaults, and returned replacements | Supply declared inputs at the correct owning/consumer boundary |
| Introspection and representation | Pydantic fields, metadata, type adapters, schemas, and serialization | Read relationships and specify supported boundary contracts |
| Typed application integration | FastStream parsing, publishers/subscribers, dependency injection, lifecycle, acknowledgements, documentation, and testing | Derive and register bindings with explicit construction roles |
| Addressed message delivery | NATS subjects, wildcard subscriptions, pub/sub, and request/reply | Project declared subjects, occurrences, and interactions into addresses |
| Controlled source ingress | NATS authentication and publication/subscription permissions | Bind accepted source channels and required permissions to declarations |
| Evidence/work retention and replay | JetStream streams and native retrieval/consumers | Select retained contracts and associate them with the program |
| Processing progress and distribution | Durable consumers, acknowledgements, redelivery, and shared work delivery | Select delivery semantics and processing boundaries |
| Concurrent commitment | Native conditional publication and required atomic stream batches | Map justification and commitment to their documented atomic scope |
| Time notifications and lookup projections | Native scheduling and watchable KV | Supply declared temporal inputs and reconstructible lookup data |
| Business progression and external effects | Native facilities above plus provider contracts | Interpret demand, dependencies, justified effects, conclusions, and capability-governed recovery |

NATS addressing identifies the receiving relationship; it is not a request for a second router to rediscover it. A permission-controlled source channel establishes its declared ingress identity when actual permissions enforce that binding. Payload validity, business truth, and provider authorization remain their own contracts. Establish declared consistency between addressed subjects and payload identifiers at the receiving boundary.

Use FastStream's NATS integration and native client access as one runtime. Other supported brokers do not imply equivalent capabilities. Bindings specify fan-out versus distributed work so native consumer configuration preserves every intended consumer.

Additional correlation logic is justified only where the integration cannot address the declared occurrence directly, such as an unsolicited observation carrying only a business key. Resolve that specific gap with native addressing, retention, and lookup facilities before adding custom matching.

TCA supplies no separate broker, event-store service, delivery-progress tracker, redelivery engine, worker distributor, or scheduler. Additional registries, routers, ledgers, and replay algorithms require a concrete residual obligation; semantic distinctions alone do not prescribe subsystems.

Primary references: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/), [serialization](https://docs.pydantic.dev/latest/concepts/serialization/), [FastStream](https://faststream.ag2.ai/latest/), [NATS broker API](https://faststream.ag2.ai/latest/api/faststream/nats/NatsBroker/), [NATS subjects](https://docs.nats.io/nats-concepts/subjects), [permissions](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/authorization), [JetStream](https://docs.nats.io/concepts/jetstream), [publication/scheduling headers](https://docs.nats.io/nats-concepts/jetstream/headers), and [KV](https://docs.nats.io/nats-concepts/jetstream/key-value-store).

## 5. Executable value composition

World provides reusable values, computations, conditions, and selections independent of messaging and persistence. Computed consequences follow from validated operands; supplied answers do not replace computations. Conditions distinguish a non-holding result from incoherent operands. Missing evidence and operational failures remain separate.

Complete native construction establishes each boundary's content and invariants. Preserve annotations and metadata, input mode, aliases, defaults and factories, validators, nested behavior, unions, and actual returned content. Native introspection supplies structural information; partial checks do not establish a valid holder.

A supplying occurrence and a consumer's constructed field can have different native values. Bind references to the intended established meaning. Any transformation that affects an operation's prerequisite belongs in the dependency used to justify it before invocation. Do not infer equivalence from purity, unchanged instance identity, or a revalidation setting.

World computations and business-value construction use declared operands rather than ambient clocks, randomness, configuration, or I/O. Adapters perform declared effects and return observations. Deterministic construction need not be idempotent when applied to its output.

Specify FastStream parsing and native construction as one receiving contract so integration neither duplicates transformations nor bypasses consumer semantics. Define ownership protection, business equivalence, and encoding separately. Representation accommodates supported value semantics; no universal JSON round trip, comparator, or reconstruction algorithm is presumed.

## 6. Irreducible interpretation of intent

The remaining generic procedure advances the declared graph:

1. **Activate intent.** An accepted command pursues a declared outcome and establishes its subject/scope bindings.
2. **Accept boundary results.** Native delivery selects the receiving binding; Pydantic establishes the supplied value or located failure. Retain required evidence through the native persistence contract.
3. **Advance dependencies.** Determine which demanded consumers have established premises; perform native computations, decisions, and compositions. Preserve each consumer's conditional demand when values are shared.
4. **Justify effects.** Require demand on the selected path, bound prerequisite evidence, native request validity, and execution knowledge consistent with the capability's guarantees.
5. **Commit and deliver.** Record the operation's authorized content and supporting versions within the chosen concurrency contract; native durable delivery reaches the adapter.
6. **Conclude or wait.** Native outcome construction plus declared completion justifies conclusion; otherwise expose the unmet dependencies. New evidence advances the same program.

This procedure defines responsibilities, not a universal serialized step order. Independent dependencies progress concurrently; field order supplies no execution ordering. Evidence acquisition can itself require justified effects.

Static bindings and verified ingress guarantees are consumed directly. Dynamic decisions remain explicit: conditional demand, selection, completeness, conflicts, and permission under prior attempts. A valid payload, echoed identifier, or constructed request alone establishes no additional authority. A report can establish business content without identifying which attempt caused it; preserve unresolved attribution.

Replacement and dispute change current knowledge according to declared source policies. Historical establishment and committed justification preserve their evidence versions and program meaning. Define derived versions and optional-input changes so authorization and conclusion consume the intended state. Silence, malformed input, and absent replacement policy establish no refusal, exclusion, or finality.

## 7. Native runtime, durability, and lifecycle

Choose stream subjects, retention, consumers, permissions, and schedules from the graph projection and its required guarantees. Retain authoritative execution information independently of acknowledgement. Evidence received before demand or correlation becomes available remains usable within declared retention bounds. Derived lookup views are reconstructible.

Map consistent justification and commitment to native conditional operations or atomic groups at their documented scope. Specify evidence/version consistency, acknowledgement points, work discoverability, and recovery between receipt, construction, commitment, and delivery. Do not imply transactions across arbitrary streams, KV keys, or external resources.

An acknowledgement establishes processing progress. Authorization, dispatch, provider acceptance, and completion establish different facts. Native redelivery resumes processing; it does not grant permission to repeat an effect. Define dispatch coordination and recovery from ambiguous results using actual provider idempotency, safe repetition, or authoritative reconciliation. Retained native triggers advance delayed results and unfinished reconciliation.

Temporal relationships name the observed occurrence, measured fact, clock authority, and historical/current interpretation. Event timestamps, receipt/knowledge time, and passage of a deadline have distinct owners. Native scheduling supplies notifications. Delayed routing, late notifications, replacement, and dispute follow the declared policy rather than evaluator timing.

Durable boundaries specify encoding, decoding, native construction, and consumer behavior. Preserve actual authorized content through retention and adapter delivery. Revalidating serialized constructed output can transform it again; retaining inputs or bypassing validation does not automatically prove fidelity. Establish the necessary native boundary contract rather than a universal restoration subsystem.

Retain sufficient data, provenance, and executable version information for continuation. Schema identity alone cannot identify validators or computed behavior. Define compatibility so new deployments cannot silently reinterpret established work. Recovery reconstructs the necessary execution view from native retained authority; no live request, coroutine, or mandatory full-history interpreter is required.

Conclusion finality, subsequent acquisition, and late evidence follow an explicit lifecycle contract. Revision or reopening requires declared policy. Cancellation preserves initiated work and later observations while stopping newly justified execution; resolve its race with committed but undispatched work. Intervention supplies evidence through actual authority and creates no repeat-safety guarantee.

### Development topology

Exactly two services: an **app dev container** with TCA, Pydantic, FastStream, and tools; and **one NATS container** with JetStream and file-backed storage on a persistent volume. Use the container network. Application and NATS restarts preserve retained state; deleting the volume resets it.

This is single-node development, not replicated high availability. Pure modeling and interpretation checks run independently; runtime integration checks use NATS. No additional datastore, broker, scheduler service, or alternate in-memory execution host is required.

## 8. Public integration and extension

World extensions add reusable semantics through native Pydantic composition. Capability adapters expose operations, report types, source relationships, and actual recovery guarantees. Extensions participate in the same graph and derived bindings without modifying generic interpretation or repeating prerequisites in handlers.

Direct calls, CLI, HTTP, and event ingress project the same program with explicit native input/output contracts. Generate schemas from Pydantic and messaging bindings; uniform meaning does not require identical interface representations.

Applications may use relational, graph, document, or other business-data stores through integrations. Those systems retain their constraints, permissions, and transactions. TCA's typed graph requires no ontology datastore.

Diagnostics expose graph bindings, construction failures, ambiguous references, missing guarantees, and blocked dependencies in application vocabulary. Explanations identify current evidence, historical conclusions, attempt justification, and legitimate next progress. Telemetry observes execution without becoming business authority.

## 9. Detailed-design deliverables and acceptance

Deliver responsibility/dependency diagrams, behavioral views, public declarations, essential internal interfaces, native integration protocols, justified decisions, and product traceability. Resolve consequential choices in that package.

Begin with a domain-independent lifecycle showing authoring, native binding, intent, evidence, construction, justified effects, and conclusion. Then test the same contracts under composition and interruption. Examples challenge semantics; they do not supply framework policy or become an application-building assignment.

| Acceptance obligation | Required evidence |
|---|---|
| One executable graph | Types and declared relationships generate the execution bindings; no second authored workflow or inventory |
| Native realization | Each guarantee names its native provider, derived binding/configuration, and actual residual TCA responsibility |
| Practical type-driven modeling | Reusable invariants, typed prerequisites, and alternatives reduce corrective checks and application-validator boilerplate |
| Faithful construction | Complete native annotations and consumer semantics agree with selected Pydantic behavior |
| Addressing and authority | Native receiving bindings, actual permissions, subjects, occurrence identity, and payload contracts compose correctly |
| Justified progression | Demand, provenance, prerequisites, execution knowledge, selection, acquisition closure, and omission justify the observed work |
| Compositional progress | Sharing, nested scopes, collections, repetition, conflicts, and completeness preserve independent work |
| Durable meaning | Authorized content, historical evidence, conclusions, and executable versions survive required retention and new construction |
| Native recovery | Concurrency, early evidence, redelivery, cancellation, uncertain effects, and reconciliation preserve progress |
| Temporal correctness | Declared clocks and observed occurrences retain meaning through delayed delivery and changing evidence |
| Minimal residual machinery | Each custom component resolves a demonstrated gap after native capabilities are used |
| Selected topology | Integration executes with the app dev container and one persistent JetStream-enabled NATS container |

Diagrams, contracts, and histories must describe the same behavior. Challenge guarantees with enclosing transformations, output revalidation, optional evidence before commitment, equal-valued distinct members, late contradictions, and overlapping workers. Test valid progress alongside prevented errors.

Use official documentation and focused version-specific checks. Distinguish requirements, choices, assumptions, source inspection, isolated experiments, and executed integration results. Unexecuted checks are not demonstrated integration guarantees. Necessary design decisions cannot be deferred to implementation or hidden behind unsupported-case restrictions.
