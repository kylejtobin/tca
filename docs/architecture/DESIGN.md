# TCA Architecture Design

**Status:** Architectural foundation for detailed design  
**Owner:** Kyle Tobin  
**Date:** October 30, 2026  
**Product:** [TCA Product Definition](../product.md)

This foundation settles architectural direction and responsibility boundaries. Detailed design resolves concrete declarations and integration protocols, with the acceptance evidence in section 9. Candidate mechanisms earn their place through that derivation.

## 1. Architectural idea

TCA is a declarative application framework whose business model is the executable program. Developers express business values, computations, decisions, dependencies, and outcomes as composable Pydantic types and declared relationships. Pydantic establishes native value meaning; FastStream integrates typed messaging; NATS/JetStream communicates, retains evidence, and delivers work. TCA interprets the model and arriving evidence to derive justified execution across immediate work, waiting, and interruption.

Derive coordination from those semantics. Types and relationships determine the necessary construction, acquisition, commitment, and continuation contracts; infrastructure realizes them. Developers express business meaning once, with reusable world semantics and public extension contracts. The target is a small semantic interpretation and integration layer; no separate engine subsystem, record algebra, or module decomposition is presumed.

NATS/JetStream is required for application execution. Development uses an app dev container and one persistent NATS container. World modeling and declaration inspection remain ordinary Python library operations.

## 2. Foundational principles

1. **One executable business model.** Types and declared relationships authoritatively express values, invariants, dependencies, decisions, and outcomes.
2. **Native construction establishes meaning.** Pydantic owns complete construction at each boundary, including actual returned content and failure.
3. **Correctness follows from modeling.** Encode known invariants in types and declaration structure; establish guarantees at owning boundaries; downstream interpretation consumes them while preserving new native construction.
4. **Relationships carry execution meaning.** Declare supply, identity, sharing, authority, correlation, conditional demand, capability guarantees, and completion wherever types and structure leave meaning unresolved.
5. **Demand and permission are distinct from validity.** A constructible or available value does not establish that a consumer needs it or may cause an operation.
6. **Evidence establishes bounded knowledge.** Content, source authority, subject identity, attribution, and permission require their respective evidence.
7. **Uncertainty and legitimate progress coexist.** Missing, invalid, disputed, or inconclusive evidence withholds affected work while independently justified work proceeds.
8. **Composition preserves subjects and scope.** Nesting, sharing, alternatives, collections, and repetition preserve declared dependency boundaries.
9. **History preserves justification.** Current evidence, historical knowledge, and committed acts have distinct meanings; mutation and later observations cannot rewrite established history.
10. **Foundations carry their assigned work.** Use native Pydantic, FastStream, and NATS capabilities; justify each remaining custom mechanism by an unmet semantic or integration responsibility.
11. **External systems retain authority.** Their permissions, transactions, completion evidence, and repeat-safety guarantees bound TCA's coordination.
12. **Claims and explanations are inspectable.** Use application vocabulary and distinguish requirements, choices, assumptions, documented behavior, and executed evidence.

## 3. Developer authoring model

| Developers author | TCA derives and manages |
|---|---|
| Composable Pydantic values, computations, conditions, selections, and outcomes | Native construction, consequences, schemas, and located feedback |
| Supplying occurrences, trusted sources, correlations, and conditional dependencies | Scoped premise resolution, evidence interpretation, and justified acquisition |
| Capability prerequisites, reports, and recovery guarantees | Justified operations, attempt attribution, and continuation |
| Member identities, repetition subjects, and completeness | Independent member progress and supported collection conclusions |
| Reusable value extensions and capability adapters | Integration through the same public contracts and runtime |

An occurrence identifies a realization in a declared business subject and scope. Equal types or payloads do not establish identity. Bindings identify supplying occurrences and their consumers, using type information only where it establishes an unambiguous relationship. Additional meaning is explicit; ambiguity receives development-time diagnostics. Authors do not reproduce an internal dependency graph or handler-to-handler workflow.

Resolve declaration syntax, scope, defaults, alternatives, and collection relationships together. Distinguish construction requirements from acquisition policy: whether each consumer pursues evidence, under what conditions, when seeking ends, and when omission is accepted. Native defaults define omission within construction; required-ness alone does not authorize acquisition. Missing evidence supplies no permission to substitute another source or business path. Combining defaults and explicit supply requires defined semantics, not a blanket prohibition or an undeclared race.

Typed decision results can make business prerequisites required fields: a decision produces alternative values and a consumer requires the relevant result. Establish their invariants, subject bindings, and provenance. This technique does not by itself prove that every conditional pursuit or selection relationship is implicit.

Every authoring restriction needs a semantic obligation and justification against less restrictive native composition or explicit relationships. Evaluation convenience does not determine permissible business modeling. Scenarios challenge the general contract; their policies do not become framework rules.

## 4. Foundation responsibilities

| Owner | Assigned work | TCA integration |
|---|---|---|
| **Pydantic** | Complete annotations, native construction, nested validation, aliases, defaults, validators, unions, and replacement values | Supply premises through explicit boundary contracts; preserve actual native outcomes |
| **Pydantic** | Field information, metadata, type adapters, serialization, and schemas | Interpret execution metadata and define boundary representations |
| **FastStream** | Connection/application lifecycle, typed publishers/subscribers, parsing, Pydantic integration, dependency injection, acknowledgement, documentation, and testing facilities | Bind declarations to messaging with explicit parsing and construction roles |
| **NATS** | Subjects, pub/sub, request/reply, and transport permissions | Derive addressing and establish trusted ingress |
| **JetStream** | Retention, replay, durable consumer progress, acknowledgement/redelivery, and work distribution | Configure authoritative history and processing guarantees |
| **JetStream** | Conditional publication and atomic stream batches | Map semantic commitments to native concurrency guarantees at their documented scope |
| **JetStream** | Scheduled messages and watchable KV | Integrate temporal evidence and recoverable lookup projections |
| **TCA** | World vocabulary, relationship interpretation, evidence judgments, demand, and justified execution | Compose the foundations without application-specific interpreter branches |
| **Adapters and external systems** | Operations, source observations, permissions, transactions, and repeat safety | Expose actual guarantees through declared contracts |

FastStream's NATS integration and native client access form one runtime; use the native client for capabilities the integration does not expose. Other supported brokers do not imply feature parity or transparent replacement of this runtime.

TCA configures native infrastructure rather than implementing a separate broker, event-store service, consumer-progress tracker, redelivery system, work-distribution system, or scheduler. Derived projections remain recoverable. Neither broker delivery nor native serialization supplies business justification or continuation fidelity by itself.

Primary references: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/), [serialization](https://docs.pydantic.dev/latest/concepts/serialization/), [FastStream](https://faststream.ag2.ai/latest/), [NATS broker API](https://faststream.ag2.ai/latest/api/faststream/nats/NatsBroker/), [JetStream](https://docs.nats.io/concepts/jetstream), [publication/scheduling headers](https://docs.nats.io/nats-concepts/jetstream/headers), and [KV](https://docs.nats.io/nats-concepts/jetstream/key-value-store).

## 5. World modeling and native construction

World supplies reusable values, computations, conditions, and selections independent of messaging and recovery. Consequences follow from validated operands; supplied answers cannot replace declared computations. Conditions keep a non-holding predicate distinct from invalid operands; selections express choices over validated information. Preserve invalid information, missing evidence, and operational failure as separate outcomes.

Complete construction owns a boundary's value meaning. Preserve full annotations and metadata, input mode, omission, aliases, defaults and factories, validators, nested validation, unions, and actual returned content. Valid parts do not establish a valid holder. Native introspection and adapters support this contract; custom field processing cannot substitute for it.

Distinguish the supplying occurrence's established value from each consumer's native construction. A consumer may transform or reject supplied content. Specify which boundary establishes each fact and which established meaning each reference consumes, including facts used before an external action. Do not assume standalone and nested constructions agree or that instance input suppresses enclosing validators. Any transformation relevant to an action's prerequisite participates in the declared justification before the action.

Operations compute from declared operands, not ambient time, randomness, mutable configuration, or I/O. Determinism concerns the same boundary, inputs, mode, and policy; it implies neither idempotent revalidation nor universal equality after serialization. Configuration follows value semantics; encoding and comparison accommodate those contracts.

FastStream parsing, dependency injection, validation, and TCA's construction call sites have explicit roles. Complete native semantics must neither be applied twice accidentally nor bypassed to preserve an earlier value. Ownership protection, business equivalence, and representation are distinct responsibilities; shallow immutability or an encoding choice does not establish all three.

## 6. Relationship interpretation and justified execution

| Judgment | Required meaning |
|---|---|
| Pursuit and demand | Intended outcome, per-consumer dependencies, conditional relationships, and acquisition/closure policy |
| Supply | A particular occurrence, subject, source, correlation, and accepted boundary construction |
| Authorization | Established demand and selected path, bound prerequisite evidence and versions, complete native request validity, and prior execution knowledge under capability guarantees |
| Conclusion | Declared outcome, justified premise bindings, selection/completeness evidence, and native outcome construction |
| Progress and explanation | What is established, missing, invalid, disputed, failed, or uncertain, and what can legitimately advance it |

Native request construction contributes content and coherence; constructibility alone does not authorize execution. Valid payloads and echoed identifiers do not establish source authority. Independently established execution facts survive unusable payload content. Evidence may establish a business value without identifying which attempt caused it; unresolved attribution remains unresolved.

Dependencies follow declared composition and relationships, not field order. A condition inside a holder is not automatically a gate on acquiring sibling premises. Each consumer retains its own justification when occurrences are shared. Required fields, defaults, conditional pursuit, and acceptance of omission form one explicit contract; neither eagerness nor speculative acquisition follows automatically from native construction. Acquiring evidence can itself require capability work; justify that work through its own dependencies rather than treating all acquisition as passive.

Alternatives distinguish native recognition of supplied data from choosing a path to pursue. Establish selection and exclusion through declared evidence and relationships; class names, invalid input, and absence provide no implicit business exclusion. Selection strategies must preserve demand and prevent work on unjustified paths.

Collections establish member identity, correlation, scope, and completion separately. Equal-valued members may be distinct subjects; container restrictions require justification from those semantics. Contradictory claims remain visible and affect only dependent work. Replacement, dispute, resolution, and finality follow declared authority; silence or lack of replacement policy establishes no closure.

Separate current evidence, historical establishment, and committed justification. Derived values may change with premises; define their versions, invalidation, optional-input changes, and the versions authorization and conclusion consume. Derivation and commitment timing are explicit design choices. Historical justifications retain the premise versions and program meaning under which acts occurred; later claims do not rewrite them.

## 7. Event-driven runtime and continuation

Commands initiate or request work, queries inspect it, and events supply evidence through one declared program. JetStream retains authoritative execution information independently of acknowledgements and delivers work through durable consumers. Acknowledgement establishes processing progress; authorization, dispatch, provider acceptance, and business completion establish different facts. Redelivery resumes processing rather than authorizing repetition.

Detailed design resolves semantic commitment, evidence snapshot/version consistency, concurrency scope, acknowledgement points, and work discoverability. Use native conditional publication and required atomic batches at their documented scope; use subjects and recoverable KV where appropriate. These do not provide arbitrary transactions across streams, keys, or external systems. Prevent gaps between committed work and delivery, and between receiving evidence and its business judgment.

Delivery exclusivity and exclusive external execution are different guarantees. Specify dispatch coordination and interruption recovery; repeat only within provider idempotency, safe repetition, or authoritative reconciliation contracts. Retained triggers must advance acknowledged but unfinished obligations, including delayed results and reconciliation. A receipt, timeout, or expired lease cannot manufacture completion or external repeat safety.

Temporal declarations distinguish source event time, receipt/knowledge time, and passage of a deadline. Bind each observation to a particular occurrence or result, identify clock authority and the fact being measured, and define historical versus current interpretation. Scheduling supplies notifications, not an implicit business policy. Resolve delayed routing, delayed boundary delivery, replacement, dispute, and replay without evaluation timing silently changing declared meaning.

Continuation preserves sufficient data, provenance, and executable program-version information. Schema identity alone does not identify validators or computed behavior. Define compatibility and explicit intervention so deployment changes do not silently reinterpret prior work.

Every durable boundary specifies encoding, decoding, native construction, and subsequent consumer behavior. Demonstrate that committed operation content reaches the adapter with its intended meaning. Dumping a constructed request and validating its output can transform it again; retaining inputs or bypassing validation does not by itself prove an alternative faithful. Use native representation machinery, resolve necessary integration, and avoid imposing a universal round-trip obligation on world models. Retained data does not require a live request or coroutine.

Cancellation stops newly justified execution while retaining initiated work and later observations. Define the race with committed but undispatched work. Intervention supplies evidence through actual authority; it cannot assert knowledge or repeat safety into existence.

### Development topology

Exactly two services: the **app dev container** with TCA, Pydantic/world modeling, FastStream, and tools; and **one NATS container** with JetStream enabled and file-backed storage on a persistent volume. Connect over the container network. Application and NATS restarts preserve retained development state; deleting the volume resets it.

This is a single-node development target, not replicated high availability. No additional broker, scheduler, datastore service, or alternate in-memory execution host is required. Unit tests exercise value semantics and pure interpretation; runtime integration tests use NATS.

## 8. Public integration and extension

World extensions use native Pydantic mechanisms; capability adapters expose operations and trustworthy observations through public contracts. FastStream binds subscriptions and publishers without handlers repeating business prerequisites. Applications remain free to use relational, graph, document, or other business-data stores through integrations; those systems retain their constraints, permissions, and transactions.

Direct calls, CLI, HTTP, and event ingress project one model. Define each interface's native input and output contract; uniform business semantics need not force every interface through an identical representation. Generate schemas from declared types and messaging contracts.

Broker permissions establish transport access; application declarations establish source authority for a business relationship. Diagnostics identify type, occurrence, binding, subject, source, and located errors. Explanations distinguish current evidence from committed history, name missing or conflicting premises, and identify legitimate next progress. Telemetry observes execution without becoming authority.

## 9. Design acceptance

Deliver mutually consistent responsibility diagrams, behavioral views, public declarations, essential internal contracts, runtime protocols, justified choices, and traceability to this foundation and product requirements. Resolve consequential choices now; scenario walkthroughs exercise the architecture rather than specify it.

| Obligation | Required evidence |
|---|---|
| One authored model and practical authoring | Rules change once; schemas, bindings, diagnostics, and extensions expose the model without runtime-internal knowledge |
| Type-driven composition | Invariants and prerequisites reside in types/relationships; nesting, sharing, alternatives, and collections preserve native consumer semantics |
| Native construction | Full annotations, aliases, modes, defaults, validators, unions, returned replacements, and failure categories agree with selected Pydantic behavior |
| Justified progress | Demand, provenance, request validity, execution knowledge, and path selection jointly justify work; unrelated work continues |
| Acquisition and omission | Required/defaulted supply, conditional pursuit, closure, and optional inputs arriving between derivation and commitment have explicit outcomes |
| Current and historical evidence | Replacement and dispute update current knowledge while historical establishment and committed justifications retain their declared meaning |
| Durable content fidelity | Native transformations do not change authorized content accidentally during encoding, adapter reconstruction, restart, or new consumer construction |
| Temporal meaning | Event/knowledge clocks, observed occurrence, delayed boundary delivery, and later replacement/dispute follow the same declared policy |
| Recovery and authority | Concurrent workers, acknowledgement loss, uncertain dispatch, cancellation, and reconciliation preserve legitimate progress without invented guarantees |
| Identity and completeness | Mutation protection, equal-valued distinct members, repeated attempts, correlation, and collection closure preserve subject boundaries |
| Foundation delegation and topology | Custom mechanisms earn their role; integration runs against the app container and one persistent JetStream-enabled NATS container |

Check prevented errors and valid progress under the same contracts. Counterexamples include pure enclosing transformations, non-idempotent output revalidation, optional evidence changing before authorization, and timely evidence later disputed. Every claimed history must follow from the published contracts, including interruption and later observations.

Library claims use official documentation and focused checks against selected versions. Distinguish inspected behavior, isolated experiments, integration results, assumptions, and proposed tests. Examples cannot prove universal fidelity, written histories are not executed evidence, and compatibility questions require concrete resolution rather than new modeling restrictions.
