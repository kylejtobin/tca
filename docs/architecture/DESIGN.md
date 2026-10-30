# TCA Architecture Design

**Status:** Architectural foundation for detailed design  
**Owner:** Kyle Tobin  
**Date:** October 30, 2026  
**Product:** [TCA Product Definition](../product.md)

This document establishes the executable model, native responsibility allocation, and requirements for detailed design. The selected foundations are Pydantic, FastStream, and NATS/JetStream. The responsibility allocations and modeling contracts below are settled architectural decisions. Detailed design derives their concrete integration and delivers the artifacts and evidence in section 9; it does not reopen these allocations to fit a preferred mechanism.

## 1. The typed graph is the program

TCA is a declarative application framework. Its program is a graph of composable Pydantic business types and explicit relationships: values, computations, decisions, prerequisites, capabilities, and outcomes. The graph expresses business meaning once. TCA derives native bindings and coordinates the declared construction dependencies. Business rules are expressed by the modeled values, computations, alternatives, and prerequisite relationships; execution does not supply a second definition of those rules.

The architecture follows this dependency:

**Authored typed graph → derived construction and messaging bindings → established native guarantees → justified effects and conclusions.**

Pydantic establishes value semantics through complete native construction. FastStream binds typed receiving and publishing contracts, lifecycle, and dependency injection. NATS subjects and permissions realize addressing and controlled ingress; JetStream retains evidence and commitments and delivers work durably. NATS/JetStream is authoritative for retained runtime facts and runtime recording time. JetStream stream sequence establishes retained order within the applicable stream scope; server-assigned message timestamps establish recording time. TCA derives business progression from that retained authority and the declared graph, consuming native guarantees rather than independently reconstructing them.

The graph is the business ontology, including dependency and execution relationships. NATS subjects project its addressable subjects and occurrences into a hierarchical messaging namespace. That namespace is an executable projection, not a second ontology or a complete representation of every edge. Conditional demand and business decisions remain declared semantics.

NATS/JetStream is required for execution. World modeling and declaration inspection remain ordinary Python library operations. Development uses an app dev container and one persistent NATS container.

## 2. Architectural principles

1. **Author meaning once.** Business types and relationships are authoritative; bindings and internal graph representations are derived.
2. **Model guarantees before procedure.** Business invariants and prerequisites belong in reusable types and compositions. Successful native construction establishes their declared guarantees; coordination consumes those guarantees.
3. **Preserve native construction.** Pydantic determines each boundary's actual returned value or failure, including new consumer construction.
4. **Construction is the business contract.** Types and explicit relationships express the values required for a business result. Framework coordination supplies operands and consumes construction results; it does not maintain equivalent business predicates beside them.
5. **Realize relationships natively.** Use construction, addresses, subscriptions, permissions, and native storage/delivery contracts wherever they establish the required relationship.
6. **Consume established guarantees.** Interpretation relies on verified bindings and boundary results instead of repeating their implementation.
7. **Separate validity, demand, and permission.** A valid or available value alone does not justify acquisition or an external operation.
8. **Preserve scope and history.** Type identity, business subject, occurrence identity, message identity, current knowledge, and committed justification remain distinct.
9. **Retain uncertainty and independent progress.** Missing, invalid, disputed, failed, or uncertain dependencies affect only work that relies on them.
10. **Respect external authority.** Provider permissions, transactions, completion evidence, and repeat safety bound effects and recovery.
11. **Resolve choices with evidence.** Name native guarantees, integration requirements, residual semantics, assumptions, and executed verification.

## 3. Authoring and binding the graph

| Authored element | Meaning | Derived realization |
|---|---|---|
| Pydantic business types and world compositions | Values, invariants, computations, decisions, and outcomes | Native construction contracts, schemas, and located errors |
| Supplying and consuming relationships | Which occurrence supplies each dependency | Scoped bindings and typed receiving contracts |
| Source and subject relationships | Accepted ingress and business correlation | NATS addressing, subscription bindings, and permission requirements |
| Conditional dependencies and capability contracts | What is pursued and what permits an effect | Declared demand relationships, constructed prerequisites, and native receiving/work-delivery bindings |
| Member identity and completion | Distinct members, repetition subjects, and collection closure | Scoped occurrence addresses and the inputs required to construct completion-dependent values |
| Public extensions and interface contracts | Additional semantics, adapters, and inputs | Integration through the same graph and foundations |

Distinguish type definitions from runtime realizations. A type defines value semantics; a business subject identifies what the value concerns; an occurrence identifies a realization in scope. The same type, business subject, and pursuit do not establish the same occurrence. Sharing requires a supplying relationship established unambiguously by declaration structure or an explicit occurrence reference. Nested compositions, operation requests, and collections retain distinct occurrences unless that relationship establishes sharing. Generated NATS addresses preserve resolved identity; assigning the same address cannot create a supplying relationship.

Bindings are derived at program loading or pursuit activation as the required subject values become available. Resolve supplying references and collection scopes from the declared relationships; report ambiguity instead of merging occurrences by type or subject. Internal graph structures are generated representations; developers do not maintain a parallel registry of nodes, operations, or workflow steps.

Use reusable world types and value operations to establish prerequisites and meaningful alternatives with minimal application-specific validator boilerplate. Consumers express business prerequisites through the typed values and relationships required for their construction. Reusable decision results distinguish meaningful alternatives; consumers requiring a particular result depend on that result. Applications do not repeat the decision in operation handlers. Invariants, business subjects, and supplying occurrences remain explicit.

Reusable framework and extension vocabulary carries common invariants, computations, alternatives, and relationships. Developers author business-specific meaning once; derived bindings supply repetitive wiring. Precision must not require duplicate declarations or knowledge of engine internals.

Each consumer declares the evidence it pursues, conditional dependencies, and acquisition closure. Derive requiredness, nullability, and default/omission behavior from native Pydantic declarations. Author additional acquisition, selection, and closure relationships only where native declarations do not express that meaning. Do not require framework markers that repeat native field semantics. Nullability, requiredness, omission/defaults, acquisition demand, and acquisition closure are separate dimensions: a nullable annotation does not establish that omission is accepted, and native defaults do not prescribe acquisition policy. Selection distinguishes recognition of supplied union values from choosing a path to pursue. These relationships express the declared business meaning without assuming eagerness, speculative acquisition, or a universal selection strategy.

Authoring restrictions require a product-semantic justification against less restrictive native composition or explicit relationships. Field-name validation, idempotent validators, and application-authored codecs must not be required merely to fit a framework-selected encoding. Any necessary extension addresses a demonstrated boundary obligation and preserves the authored model. Encoding convenience cannot impose business-model restrictions. Scenarios test the general contract and introduce no framework policy.

## 4. Native realization and residual responsibilities

| Responsibility | Native realization | TCA responsibility |
|---|---|---|
| Value construction and invariants | Pydantic constructs declared values through annotations, constraints, composition, validators, unions, defaults, and returned replacements | Supply declared operands at the owning/consumer boundary and consume the actual result; no parallel field-validation pass |
| Introspection and representation | Pydantic fields, metadata, type adapters, schemas, and serialization | Derive relationships and boundary bindings from the native declarations |
| Typed application integration | FastStream binds declared receiving and publishing types through native parsing, dependency injection, lifecycle, acknowledgements, documentation, and testing | Derive and register the binding and supply declared operands; preserve native construction roles |
| Addressed message delivery | NATS subjects, wildcard subscriptions, pub/sub, and request/reply | Project declared subjects, occurrences, and interactions into addresses |
| Controlled source ingress | NATS authentication and publication/subscription permissions | Bind accepted source channels and required permissions to declarations |
| Evidence/work retention and replay | JetStream streams and native retrieval/consumers | Select retained contracts and associate them with the program |
| Processing progress and distribution | Durable consumers, acknowledgements, redelivery, and shared work delivery | Select delivery semantics and processing boundaries |
| Concurrent commitment | Native conditional publication and required atomic stream batches | Map justification and commitment to their documented atomic scope |
| Runtime recording time | NATS server-assigned message timestamps | Use retained recording time for runtime temporal anchors |
| Retained runtime order | JetStream stream sequence within its stream scope | Bind evidence and commitments to that order; do not infer global order from timestamps |
| Deadline notifications | Native NATS scheduling | Derive deadlines from declared anchors and interpret notifications against those retained anchors |
| Reconstructible lookup projections | Native storage and watchable KV | Derive lookup data from retained authority without creating another source of truth |
| Business progression and external effects | Native facilities above plus provider contracts | Coordinate declared demand and construction dependencies, consume constructed prerequisite and outcome values, and apply capability execution/recovery contracts |

NATS addressing identifies the receiving relationship; it is not a request for a second router to rediscover it. A permission-controlled source channel establishes its declared ingress identity when actual permissions enforce that binding. Payload validity, business truth, and provider authorization remain their own contracts. Establish declared consistency between addressed subjects and payload identifiers at the receiving boundary.

Derived FastStream subscribers and publishers use the graph's declared types. Native parsing, dependency injection, lifecycle, and acknowledgement facilities perform their assigned work. Native NATS client access supplements capabilities not exposed through FastStream within the same application lifecycle; it does not create a separate transport runtime. Other supported brokers do not imply equivalent capabilities. Bindings specify fan-out versus distributed work so native consumer configuration preserves every intended consumer.

Additional correlation logic is justified only where the integration cannot address the declared occurrence directly, such as an unsolicited observation carrying only a business key. Resolve that specific gap with native addressing, retention, and lookup facilities before adding custom matching.

TCA supplies no separate broker, event-store service, delivery-progress tracker, redelivery engine, worker distributor, or scheduler. Additional registries, routers, ledgers, and replay algorithms require a concrete residual obligation; semantic distinctions alone do not prescribe subsystems.

Primary references: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/), [serialization](https://docs.pydantic.dev/latest/concepts/serialization/), [FastStream](https://faststream.ag2.ai/latest/), [NATS broker API](https://faststream.ag2.ai/latest/api/faststream/nats/NatsBroker/), [NATS subjects](https://docs.nats.io/nats-concepts/subjects), [permissions](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/authorization), [JetStream](https://docs.nats.io/concepts/jetstream), [publication/scheduling headers](https://docs.nats.io/nats-concepts/jetstream/headers), and [KV](https://docs.nats.io/nats-concepts/jetstream/key-value-store).

## 5. Executable value composition

World provides reusable values, computations, conditions, and selections independent of messaging and persistence. Conditions and decisions are constructed business results over declared operands. Computed consequences follow from those operands; supplied answers do not replace computations. A valid non-holding result remains representable but does not supply a prerequisite requiring the holding alternative. A non-holding condition, incoherent or invalid information, missing evidence, and operational failure retain distinct meanings.

A decision's meaningful alternatives are modeled results. A consumer requiring one alternative depends on that alternative's constructed value and its bound supplying relationship. Merely possessing the same Python type does not establish source authority or occurrence identity.

Complete native construction establishes each boundary's content and invariants. Preserve annotations and metadata, input mode, validation and serialization aliases, defaults and factories, transforming model validators, field validators, nested behavior, unions, and returned replacements. TCA accommodates the selected native behavior rather than relocating transformations or restricting models to simplify execution. Native introspection supplies structural information; partial checks do not establish a valid holder.

A computation or condition is modeled over its complete typed operand composition. Its constructed result supplies dependent constructions, including acquisition prerequisites. A larger composition depends on those results; evaluation does not require constructing an incomplete instance of that larger composition. The declared operand relationships derive the construction dependencies without a separately authored workflow, a mandated new class hierarchy, or a particular declaration syntax.

A construction requiring a complete collection declares the membership and completion evidence it needs. Native construction establishes the required relationship between those inputs. Available members can support independent work before completeness is established; incomplete information is not presented as a completed outcome.

A supplying occurrence and a consumer's constructed field can have different native values. Identify the supplying value, each consumer's actual constructed value, and the value whose prerequisites justify an effect. The consumer's native construction establishes the content and business prerequisites required at that boundary, including declared transformations. Subsequent execution consumes that constructed result rather than applying a second definition of business eligibility. References to supplier history record provenance but do not establish the transformed consumer result. Do not infer equivalence from purity, unchanged instance identity, or a revalidation setting.

World computations and business-value construction use declared operands rather than ambient clocks, randomness, configuration, or I/O. Adapters perform declared effects and return observations. Deterministic construction need not be idempotent when applied to its output.

The derived receiving binding uses FastStream's native parsing and Pydantic integration to establish the declared boundary value or construction failure. TCA does not repeat its field validation. A later declared consumer construction remains a distinct native boundary and preserves its own semantics; construction is not limited to one invocation across the entire program.

For each boundary, identify the value supplied, the value returned, whether mutable objects are shared, and which retained or consumer guarantees could be affected. Use the applicable native mechanisms first. Additional protection must address a demonstrated mutation path; do not presume a universal ownership subsystem.

## 6. Construction and native progression

Accepted intent demands a declared result and establishes its subject/scope bindings. The result's modeled dependencies determine which operands are pursued. Explicit supplying relationships and native delivery provide those operands at their declared receiving boundaries; native construction establishes the supplied values or located failures. Retain the evidence required for continuation through the native persistence contract.

Complete native constructions produce further business values, including decision alternatives and prerequisite compositions, or located failures. Their declared dependencies determine which constructions can progress. A supplied value does not by itself create demand, and shared values do not erase each consumer's conditional demand.

Constructed prerequisite values support demanded capability work under its bound provenance, lifecycle, authority, and execution contract. Business eligibility follows from the modeled construction; coordination does not restate its rules in a separate evaluator. Authorized work retains its actual content and supporting versions within the native concurrency contract, and native durable delivery reaches the adapter.

Retained results supply later constructions. An outcome requiring completion consumes the modeled membership and completion inputs. Its construction establishes the declared business result; lifecycle and finality relationships determine how that result is retained and exposed. Unmet dependencies remain visible without constructing a completed outcome or inventing a second definition of completeness.

Native retention, consumers, and schedules support waiting and continuation without a live request or coroutine. Independent dependencies progress concurrently; field order supplies no execution ordering. Evidence acquisition can itself require justified effects.

Declared business alternatives and prerequisites are established through modeled construction. Demand determines which constructions are pursued. Bound provenance, lifecycle, and capability contracts determine whether their results may support execution now. Static bindings and verified ingress guarantees are consumed directly. A valid payload, echoed identifier, or constructed request alone establishes no additional authority. A report can establish business content without identifying which attempt caused it; preserve unresolved attribution.

Replacement and dispute change current knowledge according to declared source policies. A derived result identifies the supplying occurrence versions and executable construction meaning on which it depends. Changes to supplied optional inputs participate in that dependency basis. Current reconstructions do not overwrite historical establishment or committed justification. Silence, malformed input, and absent replacement policy establish no refusal, exclusion, or finality.

## 7. Native runtime, durability, and lifecycle

Choose stream subjects, retention, consumers, permissions, and schedules from the graph projection and its required guarantees. JetStream holds authoritative retained execution records independently of acknowledgement. Views, indexes, and caches derive from that authority and are reconstructible; they establish no separate journal, registry, or ledger authority. Concrete records and concurrency scopes follow the graph's obligations rather than supply the starting architecture. Evidence received before demand or correlation becomes available remains usable within declared retention bounds.

Map consistent justification and commitment to native conditional operations or atomic groups at their documented scope. Specify evidence/version consistency, acknowledgement points, work discoverability, and recovery between receipt, construction, commitment, and delivery. Do not imply transactions across arbitrary streams, KV keys, or external resources.

An acknowledgement establishes processing progress. Authorization, dispatch, provider acceptance, and completion establish different facts. Native redelivery resumes processing; it does not grant permission to repeat an effect. Native consumers provide delivery coordination. Capability contracts govern whether an effect may be attempted again, using actual provider idempotency, safe repetition, or authoritative reconciliation, and how authoritative reconciliation results enter the declared model. Additional dispatch mechanics require a demonstrated gap in those guarantees. Retained native triggers advance delayed results and unfinished reconciliation.

NATS is the authoritative runtime clock. Server-assigned message timestamps establish runtime receipt/recording time; stream sequence establishes retained order within the applicable stream scope. Timestamps do not establish a globally monotonic total order across streams. Business acceptance and interpretation are established by their own retained records; message recording alone does not establish business truth.

Runtime-relative deadlines derive from the server recording time of their declared anchor. Absolute business instants arrive as typed declared values. Native NATS scheduling delivers notifications for the resulting deadline. An external occurrence timestamp is a source claim carried as typed business evidence, not an alternative runtime clock. Temporal declarations identify the observed occurrence, measured fact, anchor, and historical/current interpretation.

Evaluator wall clocks do not decide business progression. Process restart does not reset deadlines or elapsed runtime relative to retained anchors. Notification delivery time does not redefine the declared deadline. Delayed or late notifications are interpreted against the retained anchor and declared temporal relationship; replacement and dispute follow that declared policy. TCA implements no separate runtime clock, deadline scanner, or scheduler.

For each durable boundary, identify the constructed value authorized for delivery, the representation retained, the receiving construction, and the content and behavior required by that consumer. Use native serialization and transport where they satisfy that contract; add integration only for a demonstrated mismatch. Preserve actual authorized content and required consumer behavior through retention and adapter delivery. Revalidating serialized constructed output can transform it again; retaining inputs or bypassing validation does not automatically prove fidelity. A universal JSON round trip is not TCA's fidelity contract. Neither stable serialized output nor equality between a decoded value and the original, including Pydantic equality, alone establishes preservation of authorized business content. No universal comparator or reconstruction algorithm is prescribed, and business models are not forced to fit a universal restoration subsystem or round-trip gate.

Retain sufficient data, provenance, and executable version information for continuation. Schema identity alone cannot identify validators or computed behavior. Define compatibility so new deployments cannot silently reinterpret established work. Recovery reconstructs the necessary execution view from native retained authority; no live request, coroutine, or mandatory full-history interpreter is required.

Conclusion finality, subsequent acquisition, and late evidence follow an explicit lifecycle contract. Revision or reopening requires declared policy. Cancellation preserves initiated work and later observations while stopping newly justified execution; resolve its race with committed but undispatched work. Intervention supplies evidence through actual authority and creates no repeat-safety guarantee.

### Development topology

Exactly two services: an **app dev container** with TCA, Pydantic, FastStream, and tools; and **one NATS container** with JetStream and file-backed storage on a persistent volume. Use the container network. Application and NATS restarts preserve retained state; deleting the volume resets it.

This is single-node development, not replicated high availability. Pure modeling and interpretation checks run independently; runtime integration checks use NATS. No additional datastore, broker, scheduler service, or alternate in-memory execution host is required.

## 8. Public integration and extension

World extensions add reusable semantics through native Pydantic composition. Reusable computations and capability extensions express their business requirements through the same types, operand compositions, and supplying relationships. Capability adapters expose operations, report types, source relationships, and actual recovery guarantees. Adapter code performs the declared external interaction; it does not hide business eligibility or recreate prerequisite orchestration. Extensions participate in the same graph and derived bindings without modifying generic coordination.

Direct calls, CLI, HTTP, and event ingress project the same program with explicit native input/output contracts. Generate schemas from Pydantic and messaging bindings; uniform meaning does not require identical interface representations.

Interface bindings may differ in representation, but reuse the declared business constructions and relationships. Handlers do not add transport-specific business validation or prerequisite logic.

Applications may use relational, graph, document, or other business-data stores through integrations. Those systems retain their constraints, permissions, and transactions. TCA's typed graph requires no ontology datastore.

Diagnostics expose graph bindings, construction failures, ambiguous references, missing guarantees, and blocked dependencies in application vocabulary. Explanations identify current evidence, historical conclusions, attempt justification, and legitimate next progress. Telemetry observes execution without becoming business authority.

## 9. Detailed-design deliverables and acceptance

Deliver responsibility/dependency diagrams, behavioral views, public declarations, essential internal interfaces, native integration protocols, justified decisions, and product traceability. Establish the public construction model and its native realization before designing downstream protocols. Resolve consequential choices in that package.

First demonstrate **authored declarations → resolved supplying occurrences and computation operands → native construction and messaging bindings → justified progression**. Every proposed mechanism must derive from those concrete contracts and identify an obligation left unmet by the actual native bindings. Naming an abstract concern is insufficient justification for additional machinery.

Begin the behavioral explanation with a domain-independent lifecycle showing authoring, native binding, intent, evidence, construction, justified effects, and conclusion. Then test the same contracts under composition and interruption. Histories must follow the declared contracts without inventing missing evaluation behavior. Examples challenge semantics; they do not supply framework policy or become an application-building assignment.

| Acceptance obligation | Required evidence |
|---|---|
| One executable graph | Typed prerequisites and alternatives determine business behavior; explicit supplying relationships and computation operands derive native bindings, with no second business program, invented sharing, or circular construction prerequisite |
| Native realization | Each guarantee names its native provider, derived binding/configuration, and actual residual TCA responsibility |
| Practical type-driven modeling | Reusable vocabulary expresses business-specific meaning once without repeated validators, native-field markers, relationship boilerplate, or knowledge of engine internals; reduced code volume alone is insufficient |
| Faithful construction | Legitimate native annotations, transformations, and consumer construction establish and preserve declared guarantees without encoding-driven restrictions or a parallel validation system |
| Addressing and authority | Native receiving bindings, actual permissions, subjects, occurrence identity, and payload contracts compose correctly |
| Justified progression | Histories follow constructed prerequisite values and explicit supplying relationships under declared demand, bound provenance, and capability execution authority; no separate business checks supply missing semantics |
| Compositional progress | Sharing, nested scopes, collections, repetition, conflicts, and modeled completion preserve independent work; no hidden completion flag supplies a competing definition of the outcome |
| Durable meaning | Authorized content, required consumer behavior, historical evidence, conclusions, and executable versions survive retention and construction; serialization stability or equality alone does not establish fidelity |
| Native recovery | Concurrency, early evidence, redelivery, cancellation, uncertain effects, and reconciliation preserve progress |
| Temporal correctness | NATS timestamps anchor runtime deadlines, stream sequence supplies scoped order, external timestamps remain typed evidence, and restart or late notification does not reset or redefine time |
| Minimal residual machinery | Each custom component resolves a demonstrated gap after the actual native construction and messaging path has been traced; it repeats no guarantee already established by that path |
| Selected topology | Integration executes with the app dev container and one persistent JetStream-enabled NATS container |

Diagrams, contracts, and histories must describe the same behavior. Challenge guarantees with enclosing transformations, output revalidation, distinct occurrences of the same type and subject, nullable required fields, conditions controlling their enclosing composition's acquisition, optional evidence before commitment, equal-valued distinct members, late contradictions, overlapping workers, restart, and delayed deadline delivery. Verify that a declared operation cannot execute without its required business result, that an outcome cannot construct as complete while a separate engine judgment calls it incomplete, and that developers need not repeat native field semantics or a decision in markers or handlers. Test valid progress alongside prevented errors. Rejecting legitimate native models to make a mechanism safe does not satisfy acceptance.

Use official documentation and focused version-specific checks. Distinguish requirements, choices, assumptions, source inspection, isolated experiments, and executed integration results. Unexecuted checks are not demonstrated integration guarantees. Naming a mechanism, citing a native primitive, or labeling a history “Holds” does not close a guarantee. Establish that the composed contracts provide the required behavior; isolated experimental success cannot replace that derivation. Necessary design decisions cannot be deferred to implementation or hidden behind unsupported-case restrictions.
