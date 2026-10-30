# TCA Architecture Design

**Owner:** Kyle Tobin  
**Status:** Approved architectural direction; concrete bindings require demonstrated integration.  
**Date:** October 30, 2026  
**Product:** [TCA Product Definition](../product.md)

## 1. Typed namespace and native execution

TCA binds declared business types and relationships into a typed, event-sourced NATS namespace. Engine is a construction propagator over that namespace: addressed events activate bound consumers, retained supplying occurrences provide their operands, and native constructions or reusable World operations produce conditionally published results.

World supplies business types and reusable operations. A business type, its declared occurrence, identity variables, supplying relationships, sources, and consumers together determine its native bindings. Reusing a Python class does not reuse an occurrence, address, source permission, or supplier.

Developers author the business model once. Engine derives its native runtime realization, not a separate business program. Type definitions, schemas, addresses, permissions, and runtime values are connected representations of those declarations; they are not interchangeable guarantees.

The computational model is typed, demand-driven incremental dataflow over retained events, with explicit effect boundaries. Declared dependencies determine propagation; retained events establish history; constructions produce derived values; version-consistent publication establishes new work. These are settled semantics. Native API and configuration choices realize them rather than determine them. They do not introduce another dataflow engine, projection service, or application workflow.

```mermaid
flowchart TB
    WORLD["World: business types and reusable operations"]
    MODEL["Application: types and declarative relationships"]
    BIND["Engine: resolve declarations and derive native bindings"]
    WORLD -->|"Composed by"| MODEL
    MODEL --> BIND

    subgraph EXECUTION["Engine-derived native propagation"]
        NATS["JetStream: addressed events and retained supplies"]
        RECEIVE["FastStream: receiving and active consumer binding"]
        READ["Native retrieval of authoritative supplying events"]
        ASSEMBLE["Derived assembly of named consumer inputs"]
        BUILD["Pydantic composition or declared World operation"]
        PUBLISH["Typed publication under native commitment"]
        CAP["Capability adapter: external interaction"]

        NATS -->|"Addressed event"| RECEIVE
        RECEIVE -->|"Bound consumer"| READ
        READ -->|"Candidate operands and versions"| ASSEMBLE
        ASSEMBLE --> BUILD
        BUILD -->|"Typed result or failure and basis"| PUBLISH
        PUBLISH -->|"Committed event"| NATS
        READ -.->|"Native supplier lookup"| NATS
        RECEIVE -->|"Retained authorized request"| CAP
        CAP -->|"Result or failure report"| PUBLISH
    end

    WORLD -.->|"Supplies types and operations"| BUILD
    BIND -.->|"Configures"| EXECUTION
```

## 2. Model-only authoring and World semantics

Application authors declare Pydantic models, constrained fields, literals, discriminated unions, nested compositions, collections, literal defaults, and explicit relationships. Sources, supplying references, conditional acquisition, capability prerequisites, completion, and outcomes are modeled relationships.

Application-authored validators, computed-property bodies, serializers, default-factory functions, callbacks, handlers, and workflow functions are forbidden. Framework configuration is derived from the model and declared deployment requirements.

World provides reusable typed values and operations for arithmetic, quantities, comparisons, Boolean composition, selection, projection, collections, and completion. Operations have explicit operand and result types. Composition and calculation have distinct execution contracts:

| Declared consumer | Execution |
|---|---|
| Business composition | Pydantic constructs the composition from its bound inputs. |
| World computation or decision | Its reusable implementation consumes the declared typed operands and produces its result. |
| Retained result receiver | Native receiving construction establishes the result without rerunning its producer operation. |

Compositions and computations publish established results through the same native event infrastructure.

Pydantic constructs declared values and checks their constraints and alternatives. Framework value implementations own their native invariant mechanisms. Consumers require the appropriate constructed prerequisite or decision alternative. A valid non-holding alternative remains business evidence, not invalid input. Unavailable operands, invalid supplied content, consumer construction failures, and capability failure reports retain their boundary and evidence basis.

World has no messaging or persistence dependency. Framework and extension authors implement reusable operations and external adapters through defined contracts. Extensions add reusable semantics or integrations; they do not hide application workflows or business decisions in validation hooks. Engine-specific execution event types belong to Engine; reusable business values and operations belong to World. Shared reference primitives may be reused without introducing messaging dependencies into World.

The public authoring contract presents World compositions and Engine-owned execution relationships coherently. Native field semantics and repetitive wiring are derived. Developers supply only meaning that cannot be inferred, change a business rule in its declaration, and receive diagnostics in application vocabulary.

## 3. Binding the graph to native facilities

An occurrence is a realization within a pursuit, identified by its declaration location and, where applicable, its declared member key. A declared business-subject projection identifies the field or typed projection describing what it concerns. Projection paths must resolve during binding; values concerning several subjects declare the relevant roles. Equal values, matching types, names, or business identifiers do not merge occurrences. Sharing follows an explicit supplying reference or an unambiguous structural relationship; ambiguity fails binding.

Engine resolves references to typed operands or declared projections. Each resolved supplying binding identifies the consuming declaration and operand position, receiving annotation, supplying occurrence, projection if any, and supported native input/construction contract. Nested fields establish composition; supplying references establish dependencies across occurrences. Static inconsistencies fail loading. Declared identity variables complete subject-dependent addresses when their values become available. Resolved identity determines addressing; assigning a shared address cannot invent a supplying relationship.

| Declared meaning | Native realization and remaining responsibility |
|---|---|
| Occurrence identity | Derive an address or address pattern from the resolved occurrence and identity values. Preserve distinct occurrences and explicitly shared suppliers. |
| Supplying relationship | Native addressing selects the receiving relationship. Retrieve the retained supplying event and assemble its declared representation at the consumer's named operand position; no generic mapper or payload matcher rediscovers the relationship. |
| Decision alternative | Derive alternative-specific publication addresses from the constructed discriminator and resolved occurrence. Applications do not separately author another alternative identifier in the subject. |
| Source authority | Enforce publication permissions for the declared source channel and consume its established identity directly. Payload validity and external execution authority retain their separate contracts. |
| Demand | Intent and constructed alternatives activate the derived dependency and acquisition bindings. General evidence reception remains available independently; receipt alone does not activate acquisition. |
| Collection membership | Derive keyed member addresses and native subscription patterns. Equal-valued members under different identities remain distinct. |
| Collection completion | A World construction consumes declared membership and completion evidence. Members can support independent work before the complete collection is established. |
| Business events and progress | JetStream retains events; native consumers provide delivery, distribution, acknowledgement, and redelivery. Do not duplicate that progress bookkeeping. |
| Deadlines | Bind declared anchors to NATS recording timestamps and native scheduled notifications. |
| Commitment | Native latest-value retrieval supplies candidate operands. Conditional or atomic publication protects the authoritative changes relevant to the consumed basis; retrieval alone is not an evidence-consistent commitment. |

Alternative-specific events retain their decision occurrence and version. A consumer requiring a current alternative binds to the version selected by the declared replacement policy across that occurrence's candidate subjects, not merely the last message retained on one alternative's subject. Only events admitted under the declared receiving and source contract are candidates; unrelated descendants, refusals, and composite outputs are not automatically evidence for that decision.

Retrieval follows the policy at an identified stream snapshot:

| Declared policy | Required native retrieval |
|---|---|
| Latest by retained order | Retrieve the latest candidate on each matching subject at the snapshot and select the greatest stream sequence across them. |
| First by retained order | Retrieve the earliest matching candidate across the occurrence's subjects, bounded by the snapshot. Do not select the minimum from latest-per-subject results. |
| Dispute, business-field ordering, or another declared history-sensitive policy | Retrieve the candidate history required by that policy through the snapshot and apply its declared World operation. A latest-per-subject query cannot replace information the policy needs. |

For example, Approved@1, Declined@2, Approved@3 yields Approved@3 for latest and Approved@1 for first. Latest-per-subject returns Approved@3 and Declined@2; taking their minimum incorrectly yields Declined@2. After an approval is replaced by a decline under the declared policy, the old approval remains history but cannot silently satisfy a current approval prerequisite.

Native batched reads must consume their completion markers, handle required pagination, and preserve the same snapshot bound. A partial response or limit error does not establish absence or completeness. Historical lookup retrieves versions; retained typed references record which versions an actual construction consumed. Historical commitments preserve their original evidence basis without deleting history or adding a truth tracker.

Accepted intent activates the dependency and acquisition bindings for its declared outcome. Required dependencies follow their suppliers; constructed alternatives activate the declared branches. Native requiredness, nullability, and defaults retain their construction meanings. A default permits omission, not acquisition. Optional acquisition that waits has an explicit stopping relationship. Deactivation stops new acquisition authorization while preserving initiated work and later observations. Queued delivery from an earlier activation does not independently authorize another effect.

An incomplete composition is represented by its declared dependencies and retained operands at their supplying addresses. Engine retains no half-constructed business object and no pending table duplicating availability. A subsequent relevant event triggers another attempt through the same binding. Reconstructible caches may accelerate reads but establish no separate readiness or arrival authority.

| Observed situation | Interpretation |
|---|---|
| No usable retained event supplies a required operand | The dependency remains unavailable; the consumer is not established. |
| A supplied payload fails its receiving type, including missing required payload fields | Invalid supplied information attributed to that receiving boundary. |
| Available operands fail their consumer composition | Consumer construction failure attributed to those operand versions. |
| A World decision produces a non-holding alternative | A valid business result that does not supply a prerequisite requiring the holding alternative. |
| A capability reports operational failure | An operation report, distinct from construction failure. |

Pydantic error names alone do not classify every missing-field case as waiting. Failure observations retain their boundary and basis without erasing independently established valid evidence.

Completion follows the declared relationship, not silence or an invented timeout. Message count establishes completion only when a declared membership rule makes that count meaningful.

Generated FastStream subscribers and publishers use the declared receiving and publishing types. FastStream supplies native parsing, Pydantic integration, dependency injection, lifecycle, and acknowledgement facilities. Engine assembles declared representations at named operand positions using that supported receiving contract; it must not assume serialization names always equal validation names. Native NATS access supplements capabilities not exposed through FastStream within the same lifecycle. Bindings preserve intended fan-out and distributed-work semantics.

Business-key ingress bindings and any necessary native lookup derive from the declared business-subject projection and source relationship. An integration supplying only a business key can concern several occurrences and pursuits; preserve all declared receiving relationships. Resolve additional correlation through native addressing, retention, and lookup where needed. A shared key neither merges occurrences nor automatically requires a separate index or universal join mechanism.

These allocations do not prescribe one consumer per member, a universal selection strategy, or one stream per pursuit. Stream configuration must satisfy the native commitment boundary in section 5; a subject prefix alone is not evidence that it covers the resolved dependency graph.

## 4. Event data contract

Accepted intent or activation, evidence, operation results, authorizations, refusals, cancellations, lifecycle decisions, and conclusions are retained as public typed events. Engine-emitted authoritative facts use Pydantic event contracts and the same native construction and serialization discipline as business events. Facts needed for continuation and other readers are retained; temporary local variables do not require events. Diagnostics derive from declarations and retained facts, not inaccessible authoritative runtime structures. JetStream is the execution history; reconstructible views and caches establish no competing authority.

Event payloads use Pydantic's native JSON serialization and receiving validation through FastStream. JetStream retains and delivers the published bytes. Framework-provided message and value types own compatibility with their declared serialization/receiving path, including preservation of business fields and union alternatives.

Operation inputs and produced results have distinct contracts. Decoding a retained result constructs that result; it does not rerun its producer calculation. A published, addressed composite retains its business content, occurrence identity, typed supplying-event references, and model/operation identities. Pure assembly does not exempt an established result from retention. Its basis explains establishment, not universal reconstruction from ancestry. Transient implementation objects do not require separate events.

A declared construction may produce updated versions as its supplying evidence changes; it need not represent a terminal outcome. Each result remains derived from its recorded operand basis, with JetStream retaining authoritative history. Producing an updated value does not itself authorize capability execution; effects remain governed by declared demand, prerequisites, lifecycle, and provider contracts.

Declared supply and retained justification are one relationship before and after execution: the declaration identifies the supplying occurrence; the retained justification binds that edge to the event actually consumed.

| Typed justification payload field | Meaning |
|---|---|
| Consuming operand or declared edge | The dependency through which the value was used. |
| Supplying occurrence | The resolved occurrence that supplied it. |
| Stream identity and event sequence | The actual retained version consumed. |
| Declared projection, when applicable | The field or projection consumed from that event. |

Headers may carry routing or convenience metadata, but are not the sole authoritative representation of justification. Execution lineage is the version-bound realization of declared dependencies, not a separately authored lineage graph.

For Engine-generated alternatives, derive address agreement from the constructed discriminator. For external ingress, native receiving construction establishes the declared relationship between addressed context and payload content; enforced publication permission independently establishes the source channel.

Persistence concerns declared business data, not arbitrary Python instances or application procedures. No pickling subsystem, universal instance-restoration algorithm, or application-authored codec is required.

Direct-call, CLI, HTTP, and event interfaces reuse the same business declarations. Representation differences introduce no competing business rules. Applications may integrate external business-data stores; those stores retain their own constraints, permissions, and transactions.

## 5. Commitment and continuation

A capability declares its prerequisite/request type, report alternatives, source relationship, and actual provider recovery guarantees. Constructed business prerequisites, declared demand, bound provenance, lifecycle, and provider authority justify work together. Constructibility alone grants no external permission.

Retain the authorized request before invocation. The adapter receives that request through its declared data contract and translates it into the provider protocol without silently changing its business content or adding another business decision.

Authorization and conclusion identify the actual supplying versions consumed and any relevant omission or completion basis. Only versions permitted by the declared currentness and replacement relationships satisfy a current dependency. A subtree is a sufficient commitment scope only if it covers those resolved suppliers, relevant authority and lifecycle changes, future arrivals that would change omission or membership, and the publication destination. Nesting alone does not establish this coverage.

Use optimistic validation of a versioned read basis:

1. Resolve a covering subject filter `F` within one JetStream stream. Include the destination so successful publication advances the checked scope. Widen to a common ancestor when a supplying reference or authority relationship lies outside the immediate subtree; use stream-wide validation when necessary.
2. Capture a stream sequence boundary `S` before reading operands. Retrieve policy-selected evidence, relevant authority, and the latest matching scope sequence `W` as of that same `S`. Complete all reads at that bound. Do not read old operands and then obtain a newer watermark that can hide an intervening change.
3. Construct from that basis. Publish with `Nats-Expected-Last-Subject-Sequence: W` and `Nats-Expected-Last-Subject-Sequence-Subject: F`. For a stream-wide check, use `Nats-Expected-Last-Sequence: S`.
4. A conflict discards the proposed publication, refreshes the relevant basis, and reconsiders the work. A prior publication under the same established basis and attempt is recognized from retained typed records, not another deduplication ledger. Publish related records atomically where their contract requires all-or-nothing establishment.

All authoritative versions validated by that commitment must be represented in its native stream scope. Evidence originating elsewhere requires an explicit retained admission relationship into that scope; this does not create an atomic transaction with the upstream system. An enlarged scope permits false conflicts from unrelated writes, not stale authorization. A shared stream's last sequence protects the shared stream, not automatically one pursuit.

The read path must establish that the snapshot is available and sufficiently current for its trigger before acknowledging an unavailable dependency. Direct Get must not be assumed read-after-write coherent across replicas; use a demonstrated freshness guarantee or leader-routed native retrieval. Expiry, purge, deletion, or incomplete retention must not remove facts needed to establish a basis or conceal a relevant authority change. No transaction is implied across arbitrary streams or external resources.

Acknowledgement follows the retained processing result. Native consumers keep work discoverable across interruption. Repeated coordination does not create another authorization for the same established attempt. Delivery, provider acceptance, business completion, and transport acknowledgement remain different facts.

Native redelivery does not grant permission to repeat an external effect. Capability contracts govern idempotent, safely repeatable, reconcilable, and intervention-required execution. Immediate and delayed reports satisfy the same declared business relationship. A report may establish content while its attribution to an attempt remains unresolved.

Source declarations determine replacement and dispute behavior; there is no undeclared latest-wins policy. New evidence changes current knowledge without rewriting historical justification. Outcomes declare completion and finality; reopening requires declared policy. Cancellation stops new authorization, with dispatch ordering preserving initiated work and provider guarantees. Intervention supplies authoritative evidence, not an invented repeat-safety guarantee.

NATS owns runtime time. Server recording timestamps anchor runtime-relative deadlines; stream sequence establishes retained order within its stream scope. Native schedules deliver declared deadline notifications. Restart does not reset deadlines, and late delivery does not redefine them. External timestamps remain typed business claims; evaluator wall clocks do not determine progression.

Retained work identifies its model and executable meaning through derived identities. Model identity covers canonicalized declarations, schemas, resolved relationships, and operation contracts. Executable identity additionally covers operation implementations and dependency artifacts that affect behavior. A manually maintained application version is a release label, not the authoritative identity of executable meaning.

Schema equality alone does not establish executable equivalence. A changed fingerprint detects change; it does not by itself establish incompatibility or provide a migration. Compatibility must preserve retained contracts and established meaning. New deployments cannot silently rerun or reinterpret retained work under different semantics.

Continuation uses retained events and native consumers without a live request or coroutine, arbitrary object restoration, or automatic replay of external effects.

## 6. Engine implementation boundary

Engine implements one generic propagation mechanism through the following responsibilities:

1. Resolve declarations into native bindings and typed supplying relationships.
2. Activate those bindings from declared intent, alternatives, and lifecycle.
3. Retrieve authoritative supplying events and assemble declared consumer inputs.
4. Perform native composition or invoke the declared reusable World operation.
5. Publish the typed result, failure observation, or justified request with its basis under the native commitment contract.
6. Apply capability and lifecycle contracts where delivery alone cannot establish the required fact.

An addressed event identifies affected consumers through its resolved binding. For each active consumer, the propagator retrieves candidate operands, applies the boundary distinctions in section 3, constructs or computes, and commits under section 5. Conflicts refresh the relevant basis. Native acknowledgement and redelivery remain processing mechanisms, not permission to repeat an effect.

Engine consumes business guarantees from World and enforced bindings. This is one generic propagator, not separate pending-state, demand, delivery-progress, business-rule, or lineage subsystems. Additional retained records or coordination require a specific unmet obligation; a semantic distinction alone does not prescribe a subsystem.

No separate business-validation language, router, trust engine, event-store service, scheduler, deadline scanner, delivery-progress tracker, redelivery engine, or worker distributor belongs in Engine.

Development uses one application dev container and one JetStream-enabled NATS container with persistent storage. This is a single-node development topology, not a high-availability claim.

## 7. Design evidence and acceptance

For every consequential relationship, demonstrate:

**Declaration → resolved occurrence and subject projection → address/permission → active receiving binding → native operand retrieval → input assembly → construction or operation → typed result and justification → conditional publication → downstream delivery.**

Name the actual declaration, native mechanism, and guarantee at each step, including the operand versions, construction or operation, publication condition, and retained result. For each remaining Engine operation, identify the exact fact the native composition leaves unestablished. Use the same authoring contract and bindings across the public specification, native mapping, and behavioral histories.

Acceptance requires a model-only application progressing from intent through events, constructed prerequisites, external work, interruption, and outcome. Demonstrate the histories below, pairing prevented errors with legitimate progress:

- An incomplete composition becomes constructible without a pending table; absent evidence remains distinguishable from malformed supplied content.
- Valid negative alternatives and replacement across alternative-specific subjects preserve the authoritative current version and historical justification. Approved@1, Declined@2, Approved@3 must select @3 under latest and @1 under first; history-sensitive dispute cases retain all evidence their policy requires.
- Shared suppliers, distinct collection members, completion-dependent results, and independent consumers retain their declared identities and progress.
- Business-key correlation reaches multiple legitimately related occurrences and pursuits without merging them.
- Concurrent operand changes cause basis refresh and reconsideration rather than stale commitment. Include a supplier outside the immediate subtree, an operand change before a later watermark read, an absent operand arriving during construction, competing publications, and an unrelated write outside the protected filter.
- Restart after publication but before acknowledgement preserves established work without duplicate authorization.
- Public typed Engine events support continuation and developer-visible explanations.
- Derived identities detect changes in declarations and executable behavior, while compatibility is assessed against retained meaning.
- Capability delivery and provider-governed recovery preserve authorized content without unjustified repetition.
- Conditional demand, early and delayed evidence, NATS deadlines, cancellation, and finality follow the same bindings.

Show a business-rule change made once and diagnostics explaining established facts, attempted work, blocked dependencies, and legitimate next progress in application vocabulary.

Use focused checks against selected native versions. Distinguish executed integration, isolated experiments, derived behavior, and unresolved claims. Verify actual client signatures or use the documented native request protocol; compilation is not API or integration verification. Source inspection supports native capability claims but does not establish the composed histories. Subject grammar, stream/consumer configuration, snapshot retrieval, and commitment scope require concrete demonstration. Artifact presence, schema hashes, native feature names, and diagnostic output do not substitute for the composed guarantee.

The reference read mechanisms are documented in [NATS ADR-31](https://github.com/nats-io/nats-architecture-and-design/blob/main/adr/ADR-31.md); native publication conditions are documented in [JetStream publication headers](https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/headers.md). These establish available primitives, not evidence that TCA's target protocol has been executed.

The governing acceptance rule is a complete model-only business program, faithfully realized through native facilities, with no application workflow code and no duplicated native subsystem.
