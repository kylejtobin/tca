# TCA Architecture Design

**Status:** Architectural foundation for detailed design  
**Owner:** Kyle Tobin  
**Date:** October 29, 2026  
**Product:** [TCA Product Definition](../product.md)

This document establishes TCA's architectural direction and responsibility boundaries. Detailed design specifies the concrete declarations and integration protocols within this foundation. The selected foundations and their responsibilities are settled here; implementation acceptance requires the evidence in section 9.

## 1. Architectural idea

TCA is a declarative application framework in which developers express business values, rules, dependencies, and outcomes as composable Pydantic types and declared relationships. Pydantic makes those types executable through native construction, FastStream connects typed contracts to messaging, and NATS/JetStream provides communication, persistence, and distributed work delivery. TCA interprets the declared model and arriving evidence to derive justified execution, allowing the same business program to act immediately, wait for events, and continue after interruption.

These foundations form one application runtime. Pydantic realizes value meaning; FastStream integrates the typed application with NATS; NATS/JetStream carries and retains the events and work; TCA interprets the relationships that make that work justified. Their combined capabilities determine the design.

The application author writes the business model and the necessary execution relationships once. TCA derives coordination from that model. The target is a small semantic interpretation and integration layer, not a separately designed execution platform with the foundations attached afterward. No separate subsystem called an engine is presumed.

NATS with JetStream enabled is required for application execution. Development exercises this NATS-based runtime in an app dev container alongside one NATS container. World modeling and declaration inspection remain ordinary Python library operations.

## 2. Foundational principles

1. **The business model is the executable program.** Values, rules, relationships, and outcomes have one authoritative expression from which application behavior follows.
2. **World supplies composable value semantics.** Reusable values, computations, conditions, and selections compose as Pydantic types independently of messaging and execution infrastructure.
3. **Pydantic owns complete native construction.** Complete annotations and their native behavior establish the actual returned value or failure at each construction boundary.
4. **Correctness follows from the model.** Types and declared relationships express invariants; their owning boundaries establish guarantees that consumers rely on while preserving the semantics of each subsequent construction.
5. **Declare the relationships types alone cannot establish.** Sources, supplying occurrences, conditional dependencies, capability guarantees, correlations, and completion boundaries carry explicit execution meaning.
6. **TCA interprets relationships and derives justified work.** Generic interpretation realizes business meaning without application-specific branches or a second authored workflow.
7. **Construction and demand are independent judgments.** A value's availability does not establish that a particular consumer needs it or may cause an external action.
8. **Evidence establishes bounded knowledge.** Value validity, source authority, subject identity, execution attribution, and permission require their respective evidence.
9. **Uncertainty remains explicit.** Missing or inconclusive evidence supplies no invented refusal, completion, failure, or repeat safety; contradictory evidence stays visible.
10. **Legitimate progress is preserved.** Missing or disputed evidence withholds affected work while independently justified work proceeds.
11. **Composition preserves meaning.** Nesting, reuse, sharing, alternatives, collections, and repetition retain declared subjects and dependency boundaries.
12. **Retained history is trustworthy.** External mutation cannot alter established facts, and continuation preserves the meaning of previously established work.
13. **External systems retain their authority.** TCA coordinates with permissions, transactions, completion evidence, and repeat-safety guarantees established by their owning systems.
14. **The framework carries coordination.** Developers author business concepts and relationships; the foundations perform messaging, delivery, scheduling, retention, and worker mechanics.
15. **Extensions and interfaces preserve one model.** Value operations, adapters, APIs, and events use public contracts without restating business rules.
16. **Explanations use application vocabulary.** Developers can inspect what happened, its justification, what remains unknown, and what would enable progress.
17. **Every custom mechanism earns its existence.** Use Pydantic, FastStream, and NATS/JetStream for their assigned work; custom code fulfills the remaining semantic and integration responsibilities.
18. **Claims follow evidence.** Distinguish requirements, architectural choices, assumptions, documented capabilities, and demonstrated behavior.

## 3. Developer authoring model

| Developers author | The framework derives and manages |
|---|---|
| Business values and constraints as Pydantic types composed from world semantics | Complete native construction, schemas, and structured construction feedback |
| Computations, conditions, selections, and compositions | Their consequences through native construction and declared value operations |
| Accepted information, intended outcomes, and supplying relationships | Resolution of premises and the dependencies required to pursue outcomes |
| Trusted sources, correlations, conditional demand, and capability contracts | Evidence interpretation and justified acquisition or external work |
| Member relationships, repetition subjects, and completion conditions | Scoped work and conclusions supported by collection completeness |
| Reusable value extensions and external capability adapters | Integration with the same interpretation and NATS-based runtime |

An occurrence identifies a particular realization of a declared value in its business subject and scope. Equal types or equal payloads do not by themselves identify the same occurrence. The public declaration contract makes supplying relationships clear, using type information where it establishes an unambiguous relationship and explicit declarations where additional meaning is required.

Applications compose without manually reproducing an internal dependency graph or writing handler-to-handler business workflows. Detailed design resolves declaration syntax, binding and scope, native defaults, ambiguity diagnostics, alternatives, and collection relationships together. Necessary declarations state business meaning rather than runtime bookkeeping.

A native default applies where the declared construction omits that input. Missing evidence for an explicitly supplying relationship is a knowledge problem, not permission to silently substitute another source or business path.

For order fulfillment, the developer models the order, payment evidence, a coverage condition, the shipping capability, and the dependency that makes shipment justified. TCA acquires declared prerequisites and connects arriving evidence to that dependency. The example illustrates the authoring contract; it does not define an order-specific framework branch.

Changes to business rules occur in the declared model. An API handler, subscriber, scheduled task, or recovery path does not contain another version of those rules.

## 4. Foundation responsibilities

The following allocation governs detailed design.

| Owner | Assigned work | TCA's integration responsibility |
|---|---|---|
| **Pydantic** | Native construction of complete declared types, including nested composition, validators, defaults, aliases, unions, and replacement values | Supply justified premises and preserve the actual native outcomes |
| **Pydantic** | Model field and annotation information, metadata, type adapters, serialization, and schema generation | Interpret execution metadata and define explicit boundary representations using the native facilities |
| **FastStream** | Application and broker connection lifecycle, typed subscriber/publisher integration, message parsing, Pydantic-backed validation and serialization, dependency injection, and acknowledgement integration | Bind declared receiving and work relationships to those facilities with the correct construction and acknowledgement boundaries |
| **NATS** | Subjects, publish/subscribe, request/reply, and communication between participants | Derive routing from declared relationships and establish trusted ingress identity |
| **JetStream** | Persistent streams, retained event history, replay, durable consumer progress, acknowledgement/redelivery, and work distribution | Select stream and consumer configuration that preserves the required history and processing semantics |
| **JetStream** | Conditional publication and atomic stream batches | Map semantic commitment and concurrent authorization to those native operations at their documented scope |
| **JetStream** | Scheduled messages and watchable key-value facilities | Connect deadlines and recoverable lookup projections to current invocation knowledge |
| **TCA** | World vocabulary, supplying relationships, consumer demand, source and subject interpretation, evidence judgments, and justified execution | Compose the foundations into the executable business model |
| **Adapters and external systems** | External operations, trustworthy source observations, provider permissions, transactions, and repeat-safety guarantees | Expose those capabilities through declared contracts without manufacturing their guarantees |

FastStream performs messaging integration through its NATS support; native NATS client operations are used for JetStream features not exposed by that integration. This is one runtime integration, not a new transport abstraction or alternate broker strategy.

TCA does not implement a separate broker, persistent event-store service, consumer-progress tracker, message redelivery system, worker-distribution system, or scheduling service. It configures and integrates the native facilities and supplies the business interpretation they do not provide.

Pydantic serialization supplies the starting representation machinery. FastStream uses it at message boundaries. Detailed design specifies the retained and transmitted contracts needed for TCA's semantics; selecting a serializer does not by itself establish faithful continuation.

The native capabilities informing this allocation are documented in [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/), [serialization](https://docs.pydantic.dev/latest/concepts/serialization/), [FastStream](https://faststream.ag2.ai/latest/), its [NATS broker API](https://faststream.ag2.ai/latest/api/faststream/nats/NatsBroker/), [JetStream](https://docs.nats.io/concepts/jetstream), [publication and scheduling headers](https://docs.nats.io/nats-concepts/jetstream/headers), and [KV](https://docs.nats.io/nats-concepts/jetstream/key-value-store).

## 5. World modeling and native construction

World is a reusable vocabulary of business value semantics expressed through Pydantic types. It supplies values, computations, conditions, and selections that application types compose. World has no dependency on NATS subjects, delivery acknowledgements, invocation processing, or recovery mechanics.

Computed consequences follow from validated operands. Conditions establish whether their declared predicates hold. Selections express business choices over validated information. The concrete world API uses native Pydantic composition and extension capabilities; a supplied answer cannot substitute for a declared computation.

Complete construction is the authority for a boundary's value meaning. Preserve its annotation and metadata, input mode, omission, aliases, defaults and factories, validators, nested validation, union behavior, and actual returned content. A partial field check does not establish that an enclosing business type constructed.

FastStream's validation and serialization are configured to participate in this complete boundary contract. Message parsing, framework dependency injection, and business construction have explicit roles so that the same meaning is not applied twice accidentally or bypassed by convenience conversions.

Each new enclosing construction retains its native semantics. Reusing a witness does not guarantee that native validators will be skipped or that the enclosing construction returns an unchanged value. Determinism concerns an attempt with the same declared boundary, supplied inputs, mode, and policy; it does not imply idempotent revalidation of an output.

Value operations compute from declared operands rather than ambient time, randomness, mutable configuration, or external side effects. Information needed by a business decision enters as declared premises. Native validation supplies actual outcomes; TCA keeps a business condition that does not hold distinct from malformed input, missing evidence, and an escaping operational error.

Protection of retained facts, business equivalence, and serialization are separate responsibilities. Their representation uses native facilities while preserving the declared contracts. Transport or storage convenience does not introduce new business distinctions or redefine permissible value meaning. Configuration choices for world types follow their declared semantics; encoding and comparison mechanisms accommodate those contracts.

## 6. Relationship interpretation and justified execution

TCA's custom interpretation connects the following questions:

| Question | Governing meaning |
|---|---|
| What value is being pursued? | The application's declared outcome and its occurrence |
| Which information supplies it? | The declared supplying relationships and business subject |
| What has been established? | Native construction and evidence from a source authorized for the declared relationship |
| Why does this consumer require work? | Its declared dependencies and satisfied conditional relationships |
| What operation is justified now? | Established demand, the operation's declared prerequisites, and knowledge of previous execution |
| What remains unknown? | Missing premises, unresolved alternatives, uncertain execution, or conflicting evidence |
| What can advance the outcome? | Justified acquisition, an expected observation, a declared completion, or capability-governed recovery |

Dependencies implied by declared composition are resolved together; field order supplies no execution ordering. A condition included in a completed holder does not by itself declare a gate on acquiring its sibling premises. Conditional pursuit and operation-wide prerequisites are explicit execution relationships.

Sharing preserves each consumer's justification. A successful condition for one consumer supplies no permission to another consumer. Missing information can justify obtaining declared evidence while unrelated work continues. Alternatives and collections preserve scope and completeness rather than treating malformed or absent information as a business exclusion.

Evidence interpretation distinguishes content, source authority, subject correlation, occurrence identity, and execution attribution. A valid payload or an echoed identifier establishes no authority beyond its source contract. Independently established execution knowledge survives unusable payload content. Unresolved attribution remains unresolved.

Repetition, conflicting claims, and collection membership are interpreted within their declared relationships. Equal-valued members can be distinct subjects. Contradictory authoritative evidence remains visible and affects only work whose justification depends on it; arrival order supplies no automatic truth.

The integration derives work from these semantics. It does not extract application-specific rules into a second evaluator, implement business branches in message handlers, or invent capabilities needed to make a workflow proceed. A separate engine architecture, record algebra, or module decomposition is not assumed.

## 7. Event-driven runtime and continuation

Application execution uses FastStream with NATS/JetStream. Commands initiate or request work, queries inspect information, and events report occurrences. These roles share one declared program and are independent of a particular HTTP or messaging interface.

JetStream stores authoritative execution events and delivers work through durable consumers. Retention preserves the invocation information needed for explanation and continuation independently of consumer acknowledgements. Derived lookup views are recoverable from retained authority rather than competing sources of execution meaning.

Acknowledgement records message-processing progress. A recorded event establishes what that event means. External completion requires the source and capability evidence declared for the operation. Message redelivery resumes processing; it does not by itself authorize another external operation.

Use native conditional publication for competing updates, native stream batches for required atomic groups within their documented scope, and native scheduling for deadline notifications. KV and subjects support recoverable routing and lookup strategies. These mechanisms do not imply arbitrary transactions across streams, KV keys, or external systems.

The concrete integration must specify the atomic semantic commitment, concurrency scope, acknowledgement point, receiving correlation, early-delivery handling, and recovery of interrupted processing. Committed work remains discoverable without a separate outbox-and-wakeup platform. Native consumer processing and retained facts are composed so that an interruption cannot strand an observation between receipt and its business judgment.

Authorization to execute, evidence that dispatch occurred, and evidence of completion establish different facts. Loss between those boundaries retains uncertainty. Repetition of external work follows the capability's guarantees of repeat safety, provider idempotency, or authoritative reconciliation. A timeout or receipt is not a completed business result.

Continuation preserves declared meaning and previously established work across application restarts. It retains sufficient data and program-version information to interpret existing work consistently. Detailed design establishes the native serialization and reconstruction behavior of those boundaries, including subsequent enclosing construction, rather than assuming that a dump, replay, or construction-bypassing call proves fidelity. Retaining required input data does not retain a live request or coroutine.

Cancellation stops newly justified execution while preserving facts about work already initiated. Later observations remain meaningful history. External intervention obtains evidence through its actual authority; it does not create knowledge or repeat safety by assertion.

### Development topology

Development consists of exactly two services:

- **App dev container:** the TCA application, Pydantic/world modeling, interpretation, FastStream integration, and development tools.
- **NATS container:** one NATS server with JetStream enabled and file-backed storage on a persistent development volume.

The app connects to the NATS service over the container network. Restarting the app does not remove JetStream data; restarting the NATS container preserves data through the volume. Deleting the volume resets that retained development state.

This is the selected development target, not a claim of replicated high availability. No PostgreSQL container, separate broker, additional scheduler service, or alternate in-memory execution host is required. Unit tests can exercise value semantics and pure interpretation independently; runtime integration tests use the NATS service.

## 8. Public integration and extension

World extensions add reusable semantics through Pydantic's native mechanisms. Capability adapters perform external operations and establish trustworthy observations. FastStream subscriptions and publishers connect those declarations to NATS. Routine application authors do not repeat business prerequisites in those handlers.

Broker authentication and permissions establish transport access; application declarations establish whether a particular source may supply evidence for a business relationship. External providers retain their own authorization and transaction boundaries.

Direct calls, CLI, HTTP interfaces, and event ingress project the same model. Schemas come from declared Pydantic types and messaging contracts. FastStream supplies its native lifecycle, dependency injection, documentation, testing, and acknowledgement integration rather than TCA rebuilding those facilities.

Diagnostics identify the relevant type, occurrence, relationship, source, and missing or conflicting evidence. Explanations connect outcomes and operations to their justification in application vocabulary. Telemetry observes those operations without becoming business authority.

## 9. Design acceptance

Detailed design must turn this foundation into mutually consistent responsibility diagrams, behavioral views, public declaration contracts, essential internal contracts, runtime protocols, and justified decisions. It resolves the concrete integration of the selected foundations; it does not reopen their assigned responsibilities or preserve the old engine's machinery.

| Obligation | Evidence required |
|---|---|
| Single authored model | A rule is expressed and changed once; interfaces, handlers, and continuation do not restate it |
| Natural composition | Reuse, nesting, shared subjects, alternatives, and collection scopes preserve meaning and native enclosing construction |
| Native construction | Boundary behavior agrees with actual Pydantic behavior for annotations, defaults, aliases, modes, validators, unions, replacements, and failures |
| Foundation delegation | Each custom mechanism has a necessary semantic or integration responsibility remaining after using the assigned native facilities |
| Justified progress | Missing evidence enables legitimate acquisition; satisfied prerequisites enable action; independent work survives unrelated withholding |
| Bounded authority | Valid content, delivery identifiers, broker acknowledgements, authorization, dispatch, and business completion establish only their respective facts |
| Historical integrity | Caller mutation and processing copies cannot rewrite retained facts; business identity is not inferred from payload equality |
| Event processing recovery | Interruption and redelivery preserve progress without duplicating execution authorization or discarding unprocessed observations |
| Continuation fidelity | Application and NATS restarts preserve meaning under retained contracts and compatible program versions, followed by correct new construction |
| Collections and conflicts | Member identities, scoped completion, contradictory evidence, and independent justifications compose coherently |
| Developer understanding | Public schemas, diagnostics, and explanations make authoring and extension practical without runtime-internal knowledge |
| Selected topology | Integration runs in the app dev container against the single JetStream-enabled NATS container |

Check both the prevented error and valid progress under the same rules. Follow complete histories through declaration, construction, evidence, work, interruption, later observations, and continuation. Diagrams and tables must describe the same behavior; every consequential guarantee has an owning boundary and a concrete mechanism.

Library claims rely on official documentation and focused checks against the selected dependency versions. Written histories and proposed tests establish design expectations, not executed results. Identify genuine compatibility questions precisely and resolve their mechanisms without silently restricting the product or inventing authority.

This foundation chooses Pydantic, FastStream, and NATS/JetStream together so that detailed design concentrates on the remaining interpretation. Success is an application whose declared business model controls immediate, event-driven, and continuing execution with minimal custom machinery.
