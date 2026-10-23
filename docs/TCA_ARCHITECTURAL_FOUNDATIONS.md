# TCA: Architectural Foundations and Reference Design

## A type-driven backend framework for outcome-directed execution across events, time, and failure

**Version:** 1.0  
**Research date:** October 23, 2026  
**Repository baseline:** `kylejtobin/tca`, branch `review`, commit `cd6f44f7fcc5ffcfd8077a3622528d0c0d1dee7a`  
**Status:** Foundational target architecture and review standard. Proposed capabilities are distinguished from verified implementation.

---

## 1. Architectural decision

**TCA remains a type-driven, declarative application framework. Its execution model must become independent of request lifetimes.**

The framework’s governing principle is unchanged:

> **The declarations of a program’s types determine how the program is constructed and executed.**

Events and durable execution complete that principle. They allow the same declared program to advance when evidence arrives later, survive interrupted execution, and operate through multiple interfaces without requiring a separately authored workflow.

The selected architecture is:

**An outcome-directed construction interpreter over occurrence-bound evidence, hosted by an execution system that can admit events, preserve progress, and recover effects safely.**

A command establishes an intended outcome. A query requests information. An event reports an occurrence. An invocation connects an accepted intention or declared reaction to the evidence and execution history needed to pursue its outcome.

These concepts must remain distinct. Replacing every request with an event would erase meaningful differences without supplying durability, security, or correct execution.

### The architectural consequence

The unit of execution is a **versioned invocation**, not an HTTP request, coroutine, worker process, or delivery attempt.

The business program determines what can be constructed, what conditions apply, and what evidence an action requires. The interpreter determines the next justified work. The execution host performs that work and admits its results. A caller may wait for completion, receive an acknowledgement, inspect progress later, or have no synchronous connection to the work.

This is a refinement of TCA, not its replacement.

### What is not protected

No existing class, algorithm, module boundary, task-completion label, or prior review conclusion is entitled to preservation.

The product’s requirements and demonstrated semantic distinctions are the foundation. Implementations survive only when they satisfy those requirements more clearly and reliably than their alternatives.

Conversely, rewriting correct machinery is not evidence of architectural ambition. A replacement must improve correctness, expressiveness, operational guarantees, or sufficient simplicity.

---

## 2. Purpose and product contract

TCA is a general-purpose backend application framework in which developers describe their business using types, relationships, constraints, and capabilities.

Its intended experience is:

> **A developer models the business accurately and obtains executable application behavior from that model.**

The framework must support immediate operations, conditional decisions, external integrations, delayed approvals, persistent state transitions, event reactions, queries, and long-running work without requiring a second procedural account of the same business process.

General-purpose does not mean that one interpreter replaces a database, a stream processor, a security service, and a distributed scheduler. It means that those capabilities can participate in one application model without forcing the application into competing semantic systems.

### The developer contract

Business declarations identify the things that exist, their valid values, their relationships, the conditions establishing conclusions, the evidence required for effects, and the outcomes the application exposes.

Reusable library kinds implement computational and integration mechanisms. The framework implements occurrence resolution, execution control, evidence admission, recovery, and interface projection.

Developers should not need to write a workflow merely to restate dependencies already present in their types. They should not need artificial business classes, manual source identifiers, permissions decorators, proof annotations, or procedural branch selection to compensate for inadequate engine modeling.

Some information cannot be inferred and must be declared: the intended outcome, trusted external sources, correlation relationships, genuine business authority, timing requirements, and consistency expectations. **Declaring indispensable meaning is not unnecessary ceremony. Declaring the same meaning twice is.**

### The competitive objective

TCA’s differentiating target is not simply typed workflows or durable Python execution. Those capabilities already exist.

The target is **one declarative business model that supplies construction, execution dependencies, evidence requirements, interface contracts, and explanations**, while established infrastructure supplies reliable execution mechanics.

Superiority must be demonstrated through representative applications, less duplicated application logic, stronger guarantees, clearer diagnostics, and measured operational behavior. It is not established by architectural vocabulary or the use of advanced Python features.

---

## 3. Evidence base and current implementation

### 3.1 Evidence hierarchy

This document distinguishes four kinds of material:

| Evidence category | Meaning |
|---|---|
| **Established product requirement** | Intent and constraints repeatedly stated in the project discussion. |
| **Observed implementation** | Behavior or structure directly visible in the pinned repository source. |
| **External technical evidence** | Semantics documented by the technology’s maintainers or primary research. |
| **Design decision** | The selected architecture derived from those requirements and evidence, still requiring implementation and verification. |

Earlier assistant recommendations are not independent evidence of correctness. A review finding supported only by inspection or an isolated probe is not equivalent to a repository-level reproduction. A passing suite demonstrates its tested cases, not general architectural soundness.

The older ADRs and developer skill were not used as architectural authorities in this research. Their reconciliation belongs after the design is established and implemented.

### 3.2 Current baseline

The latest inspected commit is newer than the last implementation discussed in detail in the conversation. It introduces a goal-relative `Evaluator`, evaluates conditional dependencies before completing branches, constructs pure occurrences as demanded, and memoizes occurrence evaluation within a pass. The global pure-construction sweep and separate terminal re-traversal have been replaced. These are observed implementation changes, not merely claims inferred from the commit title. fileciteturn31file0L2-L2

The runtime still starts with a fresh in-memory scope, accepts a `Request`, evaluates a `Route`, performs an effect frontier using `TaskGroup`, and admits the pass’s records after successful completion. Its exposed outcomes remain `Run` and `Blocked`; it does not yet expose a durable continuation and external-evidence admission lifecycle. fileciteturn32file0L2-L2

The current world model provides Pydantic-backed values, facts, relations, computations, selections, actions, records, requests, replies, and deployment capabilities. `Route[Q, A]` explicitly represents receiving a request and constructing a reply. `Action[P, T]` declares its capability and returned record type. fileciteturn33file0L2-L2 fileciteturn34file0L2-L2

The repository targets Python 3.14 and configures strict type checking, linting, import-boundary checks, security tooling, and pytest. Its TODO marks Tasks 1–4 done, Task 5 delivered for review, and CLI completion and final verification outstanding. These labels are project status, not an independent certification. fileciteturn36file0L2-L2 fileciteturn29file0L2-L2

GitHub reports successful CI for the pinned commit. No fresh full-repository test run or durable-recovery experiment was performed during this research: the execution environment could not resolve GitHub for checkout. The architecture assessment below therefore rests on source inspection, reported CI, conversation evidence, and external research, not an invented production validation. fileciteturn35file0L2-L2

---

## 4. Lessons that must survive the transition

### 4.1 A class is not an occurrence

The same class may appear in different orders, collection elements, branches, invocations, and state versions.

Matching types, equal values, shared Python objects, or identical display paths do not establish that evidence belongs to the same execution relationship.

The current implementation correctly distinguishes an available instance from the scope and source identity that hold it. That distinction must survive persistence, where Python object identity disappears. fileciteturn30file0L2-L2

### 4.2 Type validity is not source authority

A correctly shaped `PaymentCaptured` object does not prove that a payment provider issued it, that it concerns the intended order, or that it authorizes shipment.

Pydantic supplies construction and validation semantics. TCA must establish admission, origin, correlation, scope, and the relationships supporting use.

Likewise, frozen models are useful programming constraints, not a security boundary against arbitrary Python code; nested mutable values and deliberate mutation remain relevant considerations. ([pydantic.dev](https://pydantic.dev/docs/validation/2.12/concepts/models/))

### 4.3 Constructible, demanded, and permitted are different

An action may have all its prerequisites without being relevant to the requested outcome.

Its result may be relevant without its required evidence being available.

A downstream consumer can create demand for a result. It cannot weaken the action’s declared authority requirements.

The engine must establish all three properties at the effect boundary, rather than use one as a substitute for another.

### 4.4 A successful route is not an authorization premise

Proving that an action is necessary for a successful reply does not establish that performing it now is justified.

Valid invocations may block, fail externally, time out, or receive a negative business outcome. Authorization must be established before an effect without assuming eventual success.

The converse also matters: an effect that was correctly demanded and authorized does not become retrospectively unauthorized because later work fails.

### 4.5 Static possibility is not a witness

An unrefuted symbolic arrangement means the analysis has not excluded it. It does not prove that Pydantic will construct it or that an external system will produce it.

Similarly, a field default describes one construction path, not every value the type admits. Individually optional fields do not prove that their joint absence is accepted by whole-model validation.

Static analysis must distinguish type-wide guarantees, occurrence-specific knowledge, and unknown semantics.

### 4.6 One authority does not mean one representation

Declarations, a compiled construction graph, runtime observations, persisted evidence, indexes, and diagnostics are different objects serving different purposes.

They are legitimate when derived from the same meaning. They become architectural duplication when they independently redefine that meaning.

The objective is not to eliminate every intermediate structure. It is to eliminate competing interpretations.

### 4.7 Declarative does not mean implementation-free

Computations, source binding, scheduling, persistence, and protocol handling require executable machinery.

The requirement is that application authors do not duplicate business semantics in procedural orchestration. Pure computational primitives and infrastructure adapters still contain ordinary Python.

### 4.8 The review must not create the architecture through serial rejection

A stable semantic contract, difficult examples, and acceptance criteria must precede implementation. Findings can overturn the contract, but such changes must be identified as architectural amendments rather than disguised as defects against requirements that did not previously exist.

The review evaluates the whole system: semantics, developer experience, failure behavior, security, performance, and maintainability. It neither protects existing code nor manufactures endless redesign.

---

## 5. The irreducible semantic model

The following are semantic distinctions, not a mandate to introduce one class for every row.

| Concept | Meaning |
|---|---|
| **Program version** | The executable declarations, primitive semantics, schemas, and interpretation rules governing an invocation. |
| **Type** | The declared construction and validation contract for a business value or conclusion. |
| **Construction relationship** | How a particular declared occurrence obtains its premises from permitted sources. |
| **Occurrence** | A specific realization of a declaration within an invocation, scope, and evidence revision. |
| **Evidence** | An admitted value together with its origin, identity, version, and supporting relationships. |
| **Goal** | The declared outcome being pursued. |
| **Invocation** | One accepted pursuit of a goal, with its evidence, progress, and execution history. |
| **Effect intent** | A durably identifiable external operation justified by a particular construction. |
| **Receive contract** | A declared relationship through which future external evidence may enter an invocation. |
| **Projection** | A representation of an input, outcome, or execution state for an interface or observer. |

### Commands, queries, and events

A **command** requests work. A **query** requests information. An **event** reports an occurrence.

These are meanings, not transport categories. HTTP can deliver an event; a queue can deliver a command. CloudEvents supplies an interoperable event envelope, but its specification does not define an application’s business intent or execution authority. ([github.com](https://github.com/cloudevents/spec/blob/main/cloudevents/primer.md))

An event may start a declared reaction or satisfy a receiving relationship in an existing invocation. It does not automatically trigger every action made constructible by its payload.

### Facts, events, and current state

A historical event remains historical evidence even when current state changes.

`PaymentCaptured` and `OrderCurrentlyPaid` are not interchangeable. The latter may depend on refunds, reversals, the relevant order version, and other declared conditions.

An effect is a requested interaction with the external world. Its intention, attempted execution, observed outcome, and admitted result must not be collapsed into a single “done” flag.

### Products, alternatives, and collections

Required premises combine conjunctively. Alternative sources are disjunctive. A uniquely bound field requires evidence that identifies one source or a guarded runtime check before irreversible work.

Collections have an owning source and element identity. Fixed positions, repeated elements, membership, and cardinality must remain explicit. Multiple consumers of the same source share evidence; unrelated occurrences remain independent.

### Construction as evidence

The propositions-as-types perspective is valuable: a constructed business fact carries the premises supporting it.

It is not a claim that arbitrary Python is a proof assistant or that constructing a Pydantic instance establishes external truth. The guarantee is relative to the declared rules, trusted primitive implementations, admitted inputs, and enforced source relationships.

---

## 6. Selected reference architecture

The architecture has one business interpreter and several execution and interface boundaries.

```text
Python and Pydantic business declarations
                    |
         Versioned construction graph
                    |
       Structural proof and diagnostics
                    |
Command / query / event --> Admission --> Invocation state
                                              |
                                     Construction evaluator
                                              |
                         Completed / frontier / waits / blocked
                                              |
                                       Execution host
                                              |
                          Effects, timers, durable observations
                                              |
                              Validated evidence admission
                                              |
                                      Next state revision
```

### 6.1 Declaration and compilation boundary

Pydantic declarations remain authoritative for field structure and native value semantics. TCA compiles only the relationships needed for occurrence binding, source selection, conditions, and execution.

Pydantic already builds core schemas and delegates validation and serialization to `pydantic-core`. Its supported hooks allow reusable extensions; this does not justify implementing a second validator inside TCA. ([docs.pydantic.dev](https://docs.pydantic.dev/latest/internals/architecture/))

The compiled graph is immutable once published. Stable identifiers make its relationships recoverable across processes. Those identifiers are derived framework metadata, not additional application wiring.

### 6.2 Admission boundary

Every external input passes through admission before it becomes usable evidence.

Admission establishes its declared role, authenticated origin where applicable, tenant, correlation, receiving occurrence, schema version, validation mode, and duplicate identity.

A message that can be parsed is not automatically admissible. An admissible message is not automatically relevant to every invocation.

### 6.3 Construction evaluator

The evaluator operates on a program version, a goal, and an admitted state revision:

```text
advance(program, goal, state_revision)
    -> evaluation result and proposed execution changes
```

It may construct deterministic pure values, resolve references, evaluate declared conditions, and identify the next justified effects or waits.

It does not perform network I/O, read an ambient clock, generate an unrecorded identity, acquire a database connection, or silently alter durable state.

Internal memoization is compatible with this contract. Hidden environmental input is not.

### 6.4 Execution host

The host commits accepted inputs, effect intents, receive registrations, observations, and outcomes. It manages workers, retries, leases, timers, and recovery.

The host does not decide business branches or independently interpret Pydantic models.

A local in-memory host and a durable host use the same evaluator. Their durability guarantees differ; their business construction and demand semantics do not.

Established infrastructure should be reused beneath this boundary where it satisfies the contract. The framework must not acquire a distributed scheduler merely because its interpreter needs durable execution.

### 6.5 Projection boundary

CLI commands, HTTP endpoints, subscriptions, direct Python calls, progress views, and telemetry project the same entrypoints and results.

They do not introduce another request schema, workflow, authorization language, or interpretation of failure.

---

## 7. Execution semantics

### 7.1 Demand is rooted in an outcome

A goal establishes why work is being pursued. The graph establishes the source relationships that can advance it.

The evaluator follows those relationships, constructs relevant pure evidence, and identifies the **next justified effect frontier**.

It must not calculate every action that could occur somewhere in a possible completion and dispatch that set.

### 7.2 Decisions precede their dependent effects

If a conclusion requires `Allowed` and `Pinged`, and `Allowed` is obtained from an action returning `Allowed | Denied`, the deciding action must complete before the branch-specific ping becomes executable.

This remains true when there is no fallback reply for `Denied`. A single remaining branch is not an established branch.

The current tests now encode this distinction and exercise non-exhaustive outcomes, guarded execution, substitutions, and effects followed by blocking. They are useful behavioral assets for the next architecture. fileciteturn38file0L2-L2

The rule is causal, not a universal prohibition on concurrency. Independent necessary observations and effects remain concurrent once their relevant prerequisites are established.

### 7.3 Evidence-gathering is not retroactive authorization

An effect may be needed to obtain evidence for a decision. It cannot require its own result as prior authority.

However, naming an action `Check`, `Read`, or `Approve` does not make it safe to run speculatively. Its capability contract and declared inputs still determine what the operation may do and what authority it requires.

Where two effectful alternatives remain indistinguishable, the evaluator cannot invent intent. It must report the unresolved choice or await a declared deciding input.

### 7.4 Eligibility is attached to the action

An action’s declared evidence requirements remain stable when consumers are added or removed.

If every use of an operation requires approval, that requirement belongs on the action or an authority-bearing fact it requires. If only one consumer is conditional on approval, that consumer changes demand, not the operation’s universal eligibility contract.

A conditionally demanded action can legitimately have a broader eligibility domain than one consumer. Conversely, eligibility alone never creates demand.

### 7.5 Evaluation outcomes are distinct

| Outcome | Meaning |
|---|---|
| **Completed** | The requested result has been constructed. A negative business decision can be a successful result. |
| **Ready** | A justified frontier of external work can advance the invocation now. |
| **Awaiting** | A declared receive, timer, or outstanding operation may supply the required evidence. |
| **Blocked** | The current invocation cannot progress through its declared inputs and sources, and no legitimate wait explains the absence. |
| **Failed** | Construction integrity, execution, or infrastructure failed. |
| **Cancelled** | Cancellation has been resolved according to the execution contract; prior effects may still have occurred. |

An uncertain external outcome is retained separately from a known failure. A timeout is not evidence that the remote operation did not happen.

These outcomes must carry structured reasons. Interfaces render those reasons; they do not classify them again.

### 7.6 Shared dependencies remain a graph

A shared occurrence is evaluated and constructed once per relevant state revision, not once for every path reaching it.

Indexes and caches are allowed when they preserve meaning. Cache keys include the occurrence and relevant evidence revision; context-sensitive conclusions must not be reused under an incompatible demand context.

A cycle containing no established input or progress boundary cannot manufacture evidence. A long-running business cycle across later events or state versions is different from an unsupported instantaneous construction cycle.

---

## 8. Pydantic authority and the proof boundary

### 8.1 Native construction remains authoritative

The framework uses Pydantic for value admission, aliases, unions, constraints, serialization, and reusable computational schemas. `TypeAdapter` provides these facilities for declared types that are not individual model classes. ([docs.pydantic.dev](https://docs.pydantic.dev/latest/concepts/type_adapter/))

Computed evidence is derived from validated operands at its authoritative construction boundary. Callers cannot supply a computed result as a substitute for that derivation.

A legitimate condition rejection remains distinct from malformed input, failed computation, and unrelated validation errors. Mixed failures do not become a business refutation.

### 8.2 Static analysis is deliberately bounded

The proof may interpret supported native constraints and trusted TCA primitive semantics. It must not strip arbitrary executable validators and treat the remaining schema as the full program.

Pydantic before, after, plain, and wrap validators have materially different behaviors; a wrap validator can bypass inner validation, and an after-validator can transform its output. The analysis must preserve those differences. ([docs.pydantic.dev](https://docs.pydantic.dev/latest/concepts/validators/))

Every conclusion is **established, contradicted, or unproven**.

A conservative range can support exclusion when no value in that larger range satisfies a condition. Overlap cannot establish a concrete successful execution.

An unknown validator does not necessarily make an application invalid. It makes particular static conclusions unavailable. A required safety property must then be enforced by a declared runtime construction boundary before its dependent effect, or remain an explicitly unmet obligation.

### 8.3 Type domains and occurrence knowledge remain separate

A default does not restrict every instance of its type. A specific occurrence that supplies no input may nevertheless have a known default path.

Likewise, a type’s numeric range and the value available at one correlated occurrence are different sources of knowledge.

Proof must not promote site-specific information to a class-wide theorem or discard the additional information supplied by an actual binding.

### 8.4 Validation mode is part of the contract

Python, JSON, and string-oriented inputs do not have identical admission behavior. Strict JSON validation can legitimately accept representations that strict Python validation rejects. Interface consistency means preserving documented business semantics, not pretending the modes are interchangeable. ([docs.pydantic.dev](https://docs.pydantic.dev/latest/concepts/strict_mode/))

The original mode and schema version must remain available when an input is reconstructed during recovery.

### 8.5 Proof does not promise totality

A valid invocation may await evidence, end blocked, or produce a negative business outcome.

The framework must not demand artificial fallback facts merely to prove that every admissible input produces a successful reply.

It must still reject genuine source ambiguity, invalid relationships, unsupported cycles, and contradictions established by sound analysis. “Unproven” must not be mislabeled as “impossible.”

---

## 9. Events, time, and evidence closure

### 9.1 Events are admitted claims about occurrences

An event has an identity and origin. Admission determines whether its claim may be used in a particular relationship.

CloudEvents specifies a `source` and `id` combination suitable for identifying duplicate deliveries. That is useful transport identity, but it is not sufficient business correlation or authorization. ([github.com](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md))

TCA also needs the receiving invocation or entrypoint, subject identity, relevant state version, and permitted source role.

Two deliveries of the same event do not create two new business facts. Two distinct events with identical payloads are not automatically duplicates.

### 9.2 Receives are declared, not invented by missing fields

A receive contract identifies the expected evidence type, admissible source, correlation relationship, cardinality, and completion or expiry conditions.

It is not a procedural workflow step. It declares how an external premise can become available.

An arbitrary absent field cannot silently become “wait forever for a matching event.” An incoming event cannot search all active invocations for any field with the same class.

Event-triggered entrypoints and continuation receives are related but distinct. The former creates a new goal; the latter supplies an existing goal.

### 9.3 Early and out-of-order delivery are normal

An event may arrive before the worker registers its wait, after a process restarts, or out of transport order.

Durable admission must avoid the registration race: an eligible event is retained or matched transactionally rather than lost between “check for evidence” and “begin waiting.”

Ordering is established only where the source or domain contract supplies it. Timestamps alone do not establish causality.

### 9.4 Absence requires a boundary

The request-based engine usually operates over finite inputs. Event-driven execution exposes an additional question: **is this source complete, or might more evidence still arrive?**

“No approval has arrived” is not “approval was denied.”

“The collection currently contains one item” is not “the collection contains exactly one item.”

A timeout establishes that a deadline elapsed under a declared clock and delivery policy. It does not establish that an event never occurred elsewhere.

Timely Dataflow’s progress model illustrates why computation over evolving inputs needs explicit knowledge of what can still arrive before final results can be released. ([timelydataflow.github.io](https://timelydataflow.github.io/timely-dataflow/chapter_5/chapter_5_2.html))

TCA therefore requires source closure, snapshot versions, or declared windows wherever absence, uniqueness, aggregate finality, or selection depends on completeness.

### 9.5 Append-only evidence does not make every conclusion monotonic

Adding evidence may preserve a historical event while invalidating a current-state conclusion or changing a selection.

A new bid can change the maximum. A second candidate can invalidate uniqueness. Revocation can end the authority supplied by a prior grant.

The CALM research connects coordination-free consistency to monotonic program behavior. Its lesson for TCA is not that coordination disappears, but that operations relying on absence, finality, or changing exclusivity need an explicit consistency boundary. ([arxiv.org](https://arxiv.org/abs/1901.01930))

Within a sealed evidence revision, established values remain immutable. New information produces another revision, state version, or declared continuation. It does not silently mutate the premises of an already-executed effect.

---

## 10. Durable execution and recovery

### 10.1 Persistence follows semantic boundaries

The durable system records what cannot safely be regenerated:

- Accepted commands and external evidence, including their identities and admission context.
- Program version, goal, invocation identity, and state revisions.
- Receive registrations, timers, and recorded environmental observations.
- Effect intents, attempts, receipts, outcomes, and evidence-admission decisions.

Pure derived values may be reconstructed when their inputs and implementation are deterministic and version-pinned. Snapshots are an optimization, not an alternative source of business meaning.

An execution journal is not a requirement to event-source the entire application database. Event sourcing is a separate domain-storage choice with substantial tradeoffs in concurrency, evolution, and querying. ([learn.microsoft.com](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing))

### 10.2 Stable identity replaces memory identity across recovery

The durable model distinguishes:

**Program identity:** the executable version being interpreted.

**Invocation identity:** one accepted pursuit of an outcome.

**Occurrence identity:** a construction site within that invocation, its scope lineage, and relevant evidence version.

**Effect identity:** one logical operation associated with that occurrence.

**Attempt identity:** one physical attempt to execute the logical effect.

Retries retain effect identity and receive new attempt identities. A business decision to perform the operation again creates a new logical effect.

Class names, list positions, object addresses, and payload hashes alone are insufficient durable identities. Element positions remain useful within immutable collection snapshots; evolving collections require membership identities that survive reordering.

### 10.3 Advance and commit form an explicit protocol

An invocation advances from an authoritative state revision.

The evaluator proposes the next frontier or waiting state. The host validates that proposal against the expected revision and atomically records the accepted changes before releasing external work.

A single logical writer or compare-and-swap discipline prevents two workers from independently advancing the same revision. Parallel effects remain possible after their intents have been committed.

This coordination is per invocation or declared transaction scope, not a global order over the application.

### 10.4 The effect lifecycle is not a Boolean

The durable state must distinguish an operation that is prepared, dispatched, observed successful, observed rejected, failed, or uncertain.

A stable effect intent is recorded before dispatch. A returned result is validated and durably recorded before becoming admitted evidence. An acknowledgement of submission does not imply that the business operation completed.

The crash between external success and local recording cannot be eliminated by replay alone. Temporal documents this exact failure window and the need for idempotency enforced by the external operation. ([docs.temporal.io](https://docs.temporal.io/activity-definition))

Consequently, every effect capability has an explicit recovery contract: safe retry, external idempotency key, status reconciliation, or no automatic retry while the outcome is uncertain.

**TCA guarantees one logical effect identity. It does not claim universal exactly-once execution of arbitrary external side effects.**

### 10.5 Worker ownership is not business authorization

A lease or fencing token determines which worker may advance or record an invocation. It does not authorize the business operation itself.

A lease expiring also does not prove that an old worker stopped interacting with an external service. External deduplication or fencing remains necessary where duplicate physical execution would be harmful.

The execution host must reject stale state commits while retaining enough information to reconcile effects whose outcomes are unknown.

### 10.6 Fresh values are recorded inputs

The current `Instant` and `Identity` kinds use the clock and UUID generation during construction. Reconstructing them after a crash would otherwise change the program’s evidence. fileciteturn33file0L2-L2

Their durable semantics must be “allocated once for this logical occurrence,” with the allocation recorded and reused.

The same principle applies to random values, external reads, model inference, mutable configuration, and any environmental observation that influences execution.

The evaluator does not sample these implicitly. A trusted provider supplies them through a recorded boundary.

### 10.7 Recovery is not ordinary response deserialization

The current reply projection deliberately omits its supporting fact from serialized output. A client-facing representation is therefore not an execution snapshot. fileciteturn34file0L2-L2

The durable codec preserves evidence identities and construction relationships. It must not blindly dump every model and revalidate that dump as if it were the original input: aliases, excluded fields, computed values, and transformations can make that incorrect. Pydantic explicitly supports customized serialization and field exclusion. ([docs.pydantic.dev](https://docs.pydantic.dev/latest/concepts/serialization/))

A valid recovery strategy retains original boundary data and admission mode, reconstructs deterministic facts from their recorded premises, and resolves shared evidence through stable identities. Unsupported nondeterministic validators cannot silently participate in replay.

Arbitrary pickled object graphs are not the external admission or durable trust model.

### 10.8 Business joins, execution batches, and transactions are different

The existing whole-pass barrier prevents records from a failed pass entering construction. That is an established local execution contract, not proof that external effects are transactional. fileciteturn32file0L2-L2

The durable target must not allow incidental worker batching to define business atomicity.

The governing decision is:

**Validated observations are durably retained independently; admission boundaries are explicit; business conjunctions determine when combined evidence is sufficient.**

A fact requiring both `InventoryReserved` and `PaymentConfirmed` does not construct until both exist. Actual atomic database changes belong inside a transactional capability. A transactional outbox is appropriate when a database mutation and publication intent must commit together. ([docs.aws.amazon.com](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html))

A finite admission cohort may preserve an intentional all-or-none publication contract. It must have a stable identity and recovery semantics, not exist accidentally because several tasks were scheduled together.

This is an explicit refinement of the earlier pass contract. Existing barrier tests must remain as evidence of the old behavior until the new admission contract is implemented and verified. A failed sibling must never cause a completed external operation to be forgotten and blindly repeated.

### 10.9 Versioning is part of correctness

An invocation is pinned to its executable program and compatible serialization semantics.

New deployments do not reinterpret old history under changed defaults, validators, computation primitives, or construction identities.

Temporal and DBOS both treat changes to durable workflow execution as a versioning problem because old history must remain compatible with the code that resumes it. ([docs.temporal.io](https://docs.temporal.io/develop/python/versioning))

TCA requires equivalent discipline without a separately authored workflow: preserve the old program version, or perform an explicit, validated migration that carries forward evidence and already-issued effects.

A migration cannot accidentally create a fresh identity for an effect that already happened.

---

## 11. Security and consistency

### 11.1 Three authority boundaries

TCA must preserve three separate checks:

**Admission authority:** May this principal or source introduce this command or evidence?

**Business eligibility:** Does the action’s declared evidence justify this operation for this subject and version?

**Execution authority:** Is this worker currently permitted to dispatch and record this exact logical effect?

A type name or valid payload satisfies none of these by itself.

Authorization must remain least-privilege and enforced at the actual protected boundary. This is consistent with OWASP’s emphasis on explicit permission validation rather than trusting identifiers or assumed framework behavior. ([cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html))

### 11.2 Historical permission is not unlimited future permission

A historical grant can prove that an earlier operation was authorized. It does not automatically authorize a new operation after expiry or revocation.

Long-lived invocations must carry the authority semantics relevant to future dispatch: subject, scope, validity, policy version, and any required revalidation.

Recovery does not undo a completed effect because policy changed. It also does not silently reuse expired authority to issue a new effect.

### 11.3 Tenant and subject identity are binding semantics

Correlation must establish the intended tenant, business subject, invocation, and receiving relationship.

A duplicate event for one order must not complete another order merely because both await the same class. A valid approval for one version of a record must not authorize a mutation against a different version.

Internal execution-completion messages must not be forgeable through ordinary business event ingress.

### 11.4 Invocation serialization is not database consistency

Two invocations can still race to spend the same balance or reserve the same inventory.

A state-changing capability must enforce its consistency contract at the authoritative store, through a transaction, expected-version condition, reservation, or equivalent mechanism.

Serializable transactions address anomalies among concurrent transactions; per-invocation execution order is not a replacement for that guarantee. ([postgresql.org](https://www.postgresql.org/docs/current/transaction-iso.html))

### 11.5 Trusted code boundary

TCA is not a Python sandbox.

The framework enforces its own admission, construction, and dispatch paths. It does not claim to stop arbitrary trusted application code from performing I/O directly, mutating private state, or fabricating internal objects.

Untrusted executable code requires a separate isolation boundary. No expanding in-process authenticity protocol should be built to obscure this limitation.

Sensitive payload retention, encryption, access control, and deletion policies belong to the durable data contract. A journal does not imply indefinite retention of every secret or raw message.

---

## 12. Developer experience and application shape

### 12.1 One business program across interfaces

A conceptual fulfillment program contains:

```text
FulfillOrder
    requests a declared shipment outcome

OrderEligible
    derives from the order snapshot and required business conditions

PaymentConfirmed
    derives from an admitted, correlated payment outcome

ShippingAuthority
    combines the correct order, payment, and permission evidence

Ship
    requires ShippingAuthority
    produces a shipment record

Shipment
    is the requested business conclusion
```

These are relationships among business types, not an authored execution sequence.

A payment submission may return an immediate confirmation or a receipt establishing a declared wait for later evidence. A webhook may subsequently admit that evidence. The shipment action becomes demanded and eligible through the same declarations.

All supporting facts must refer to the same intended order and state version. Class compatibility alone does not establish that relationship.

### 12.2 CLI

The CLI constructs the declared input through Pydantic.

It can wait for a result, return an invocation identifier, inspect progress, or submit an authorized cancellation. Nested structures, collections, aliases, omitted values, and computed outputs retain their native semantics.

A structured input option remains available when shell flags cannot represent a model cleanly. The CLI does not define a competing schema.

### 12.3 API

An API can provide immediate results or durable acknowledgement with later status and retrieval.

Disconnecting a caller does not implicitly cancel a durably accepted operation. Acceptance and completion are separate contracts.

### 12.4 Events and subscriptions

A declared reaction maps an admitted event to a goal. A declared receive maps an admitted event to an existing invocation.

Recurring subscriptions create bounded invocations or windows rather than one immortal global scope that executes everything constructible.

### 12.5 Queries

Queries remain first-class. They need not become fictitious domain events or incur a durable workflow round trip.

External reads are observations and may be nondeterministic. When their results participate in durable execution, the observed snapshot must be retained. A query-only entrypoint does not silently acquire mutation effects.

### 12.6 Errors and observability

Diagnostics identify the business type, field, occurrence, evidence source, state version, and unresolved obligation.

The operator should be able to answer: Why is this invocation waiting? Why was this effect demanded? Which evidence made it eligible? What actually happened? What is safe to retry?

OpenTelemetry remains an observation system, not the execution ledger. Durable invocations require stable correlation across multiple worker activations, not one span held open for days. Messaging span links support relationships that are not a simple parent-child call stack. ([opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/))

Payloads and credentials remain excluded by default. Replayed computation must not masquerade as a newly performed external operation.

---

## 13. Application-pattern stress tests

The five business archetypes discussed during the project are useful test families, not an exhaustive theorem about all software.

| Application family | What TCA must express | Boundary that must remain explicit |
|---|---|---|
| **Guarded record management** | Typed input, permission evidence, reads, writes, projections | Tenant isolation and authoritative mutation checks |
| **Workflow and approval** | State transitions, delayed decisions, deadlines, human evidence | Durable receives, cancellation, and versioned state |
| **Ledger and audit** | Immutable records, derived balances, reconciliation | Transactional consistency and duplicate prevention |
| **Pipeline and aggregation** | Collections, computation, ingestion, materialized results | Source closure, windows, resource limits, and data locality |
| **Rules and decisioning** | Reusable conditions, alternative outcomes, explainable conclusions | Supported static reasoning and versioned policies |

The engine should supply common construction and execution semantics. It should not contain five application-specific subsystems.

Representative difficult cases include a shipment split after invoicing, an approval arriving after a policy change, concurrent inventory reservations, a duplicated payment callback, a late event changing an aggregate, and a blocked route following a completed external effect.

The architecture succeeds when those cases can be modeled naturally without procedural duplication. It fails when the application must maintain a second workflow merely to connect declarations the engine already understands.

---

## 14. Lessons from established systems

| System or research | Relevant contribution | Consequence for TCA |
|---|---|---|
| **Pydantic** | Executable model validation, serialization, metadata, reusable schema composition | Delegate value semantics rather than rebuilding them. |
| **Pydantic Graph** | Typed nodes, transitions, state, and explicit graph assembly | Useful machinery, but not automatically a replacement for declaration-derived construction. Its documented node methods and edges represent an explicit workflow model. ([ai.pydantic.dev](https://ai.pydantic.dev/graph/)) |
| **Temporal** | Durable execution histories, external activities, timers, signals, queries, and updates | Durability and interactive messaging can coexist. TCA should not force all interactions into one event shape. ([docs.temporal.io](https://docs.temporal.io/workflow-execution)) |
| **DBOS** | Durable Python workflows and steps, database-backed messaging and transaction integration | A mature host may supply recovery mechanics beneath TCA without becoming its business language. Its documented guarantees distinguish steps from transactions. ([docs.dbos.dev](https://docs.dbos.dev/python/tutorials/workflow-tutorial)) |
| **Prefect** | Python flows and tasks with state tracking, retries, concurrency, and operational orchestration | Operational infrastructure can be reused; it should not require a second author-written business workflow. ([docs.prefect.io](https://docs.prefect.io/v3/concepts/flows)) |
| **Datalog and Soufflé** | Declarative relationships, conjunction, alternatives, recursion, and constrained reasoning | Learn from explicit logical semantics without translating arbitrary Python into an imagined complete theorem system. ([souffle-lang.github.io](https://souffle-lang.github.io/tutorial)) |
| **Timely and differential dataflow** | Progress frontiers, incremental updates, shared computation | Evidence completeness and reusable indexes are semantic concerns, not merely optimizations. ([timelydataflow.github.io](https://timelydataflow.github.io/timely-dataflow/chapter_2/chapter_2_4.html)) |

No external framework is selected merely because it has “graph,” “event,” or “durable” in its description.

The execution-host boundary is settled by this design. The concrete durable host remains an implementation selection subject to conformance testing. That is a bounded infrastructure choice, not permission to renegotiate business semantics.

---

## 15. Disposition of the current engine

The current code is evidence and reusable material, not the architecture’s starting constraint.

| Current component | Disposition under this design |
|---|---|
| **Pydantic business kinds and computational admission** | Retain the role and demonstrated semantics. Correct purity, persistence, or identity assumptions where required. |
| **Sealed `Construction` graph and direct source references** | Retain as the candidate relationship model; add stable versioned identity and receiving-source semantics. |
| **Occurrence scopes and construction witnesses** | Preserve their distinctions; replace memory-only ownership as the durable identity mechanism. |
| **Goal-relative `Evaluator`** | Use as the current implementation candidate for the construction kernel, not as accepted proof of the new lifecycle. Separate evaluation from effect execution and durable commits. |
| **`Route[Request, Reply]` as execution root** | Generalize to typed entrypoints and goals. Keep request/reply as one projection. |
| **Monolithic `constructed()` lifecycle** | Replace as the sole execution owner with advance, commit, dispatch, and admission boundaries. |
| **Fresh clock and UUID factories** | Convert to recorded per-occurrence observations or allocations. |
| **Action and record validation boundary** | Preserve native admission; add stable effect identity, recovery contracts, and delayed-result support. |
| **Static proof** | Retain sound occurrence-bound analysis; remove any assumption that admissibility implies universal completion or that all evidence is already closed. |
| **Whole-pass admission** | Preserve its tested safety meaning during transition; replace incidental scheduling-based atomicity with explicit admission semantics. |
| **CLI** | Preserve interface derivation intent, consolidate schema interpretation, and expose invocation lifecycle. |
| **Tracing and concurrency primitives** | Retain standards-based mechanisms while adapting their lifetime to worker activations and durable invocations. |

The observed evaluator is materially closer to the desired kernel than earlier eager implementations. The durable architecture nevertheless requires new semantics, not simply wrapping the current coroutine in a queue.

A full rewrite is warranted only if the existing representation obstructs those semantics more than replacing it would. The decision is made per coherent subsystem, with preservation of behavioral evidence, not by protecting previous effort.

---

## 16. Rejected architectural directions

### Everything is an event

Rejected because commands, queries, reported occurrences, and internal execution records have different meanings. An event envelope does not supply intent, authorization, or durability by itself.

### A broker around the request loop

Rejected because durable delivery does not preserve execution progress, effect identity, waiting state, or recovery of ambiguous external outcomes.

### Mandatory event sourcing for business data

Rejected because execution durability and domain storage are different requirements. Applications may use transactional state, event sourcing, or both.

### Eager execution followed by increasingly elaborate justification

Rejected because availability does not establish demand. The correct remedy is causal, goal-relative evaluation, not a proof that every eager action might have a consumer.

### Downstream consumers granting authority

Rejected because adding a consumer must not weaken an action’s intrinsic evidence requirements.

### A complete static interpreter of arbitrary Pydantic validators

Rejected because executable callbacks cannot be treated as transparent constraints. Supported summaries and explicit unknowns are required.

### A second hand-written workflow for durable execution

Rejected because it duplicates the business program. A reusable infrastructure driver may be procedural; the application must not restate its construction logic inside that driver.

### A global event bag keyed by class

Rejected because it erases origin, subject, version, scope, and receiving authority.

### Universal exactly-once external effects

Rejected as an unconditional guarantee. The framework can provide durable logical identity and duplicate-resistant dispatch; external effect semantics require provider cooperation or reconciliation.

### Architectural purity measured by class count

Rejected because necessary distinctions must remain represented. Simplicity is the absence of unnecessary meaning and machinery, not the elimination of types that enforce real invariants.

---

## 17. Verification and acceptance

Verification must challenge the semantic contract independently of the implementation’s helper functions.

### Core conformance

| Test family | Required result |
|---|---|
| **Interface equivalence** | Equivalent CLI, API, direct-call, and event-triggered inputs produce equivalent business outcomes under their documented admission modes. |
| **Demand and eligibility** | Irrelevant effects do not execute; demanded effects lacking authority do not execute; correct effects remain valid even if later work blocks. |
| **Decision ordering** | Evidence-gathering precedes branch-specific effects, with and without fallback outcomes. |
| **Occurrence integrity** | Equal values and reused objects remain distinct across subjects, scopes, versions, and invocations. |
| **Native construction** | Derived outputs cannot be forged; ordinary validation failure is not condition refutation. |
| **Unknown semantics** | Unsupported static knowledge does not establish permission, exclusion, totality, or a fabricated witness. |
| **Collections** | Empty, fixed, variable, evolving, and closed collections retain their membership and cardinality semantics. |
| **Graph reuse** | Shared dependencies remain shared; evaluation cost does not become exponential through repeated tree expansion. |

### Durable conformance

The failure matrix includes interruption before and after input acceptance, intent recording, external dispatch, external success, outcome recording, evidence admission, and reply delivery.

Duplicate input, duplicate callback, conflicting duplicate payload, stale worker completion, late event, out-of-order event, expired authority, unavailable old program version, and concurrent state mutation are required cases.

Recovery must reconstruct the same logical evidence relationships and preserve already-issued effect identities. It must neither forget successful external work nor invent success from uncertainty.

A waiting invocation must survive process loss without keeping an open socket or coroutine alive. An early callback must not be lost. A cancelled worker must not silently cancel a durably accepted business operation.

### Business and developer conformance

The same representative applications must run without added proof ceremony or a parallel workflow.

Valid conditional programs remain valid. Truly ambiguous effects are not guessed. Diagnostics name the missing business distinction rather than instructing the developer to accommodate an internal representation limitation.

The framework must be evaluated against both errors: accepting unsafe models and rejecting legitimate models that its intended language should express.

### Evidence required for acceptance

A review identifies the exact commit, reads the full affected path, executes relevant counterexamples through the public API, and records what was actually verified.

Source inspection, isolated probes, repository tests, CI, fault injection, and production observations remain distinct evidence categories.

A green suite is necessary but insufficient. An architectural objection must nevertheless be tied to a violated invariant or a demonstrably better representation, not an untested preference.

---

## 18. Coordinated completion plan

The event-capable design changes the completion target. It is real work, not a terminology change or a deferred integration detail.

The remaining work is organized into three coherent milestones rather than an expanding tree of patches.

### Milestone 1: Complete the invocation and evidence runtime

The construction kernel gains stable logical identity, explicit receiving sources, evidence revisions, deterministic environmental inputs, and distinct completion, waiting, blocking, and failure outcomes.

The execution host owns durable acceptance, effect intent and outcome recording, recovery, and admission. A local host and one durable host demonstrate the same business semantics.

This extends the substance of Task 5 and reworks earlier components where required. Previously accepted request-lifetime assumptions are not preserved merely because their tasks were marked done.

### Milestone 2: Complete the shared interface and capability contracts

CLI, API, event ingress, status, result retrieval, cancellation, and capability bindings expose the same invocation model.

No interface owns another validation language or workflow. No durable provider requires the application author to restate the business program.

This generalizes Task 6 beyond an isolated command-line projection.

### Milestone 3: Demonstrate recoverable correctness and simplify

Independent conformance tests cover the five business-pattern families, failure windows, concurrency, upgrades, evidence closure, security boundaries, and performance.

Superseded machinery is removed as replacements land, not left for a final cosmetic cleanup. Documentation is reconciled with demonstrated behavior.

This makes Task 7 an acceptance and consolidation milestone rather than the place where the application’s missing execution architecture is first discovered.

Each milestone produces an executable vertical slice. There is no production-readiness claim until durable recovery and operational boundaries are demonstrated.

---

## 19. Evidence and decision register

| ID | Status | Statement |
|---|---|---|
| **R1** | Established requirement | TCA is a general-purpose, type-driven backend framework; business declarations remain the program. |
| **R2** | Established requirement | Correctness, expressiveness, developer experience, reliability, durability, security, and sufficient simplicity are joint design criteria. |
| **O1** | Observed source | The pinned implementation has a goal-relative, memoized evaluator and occurrence-bound witnesses. It is no longer the earlier eager-action implementation. |
| **O2** | Observed source | The exposed runtime still creates fresh in-memory scopes and completes a request/reply run; durable receiving and recovery are not established by that path. |
| **O3** | Observed source | Fresh clock/identity construction and reply serialization require explicit treatment before durable reconstruction is sound. |
| **E1** | External evidence | Durable delivery and durable execution are different mechanisms; execution histories preserve progress and external results. ([docs.temporal.io](https://docs.temporal.io/encyclopedia/event-history)) |
| **E2** | External evidence | External success followed by local failure requires idempotency or reconciliation; replay alone cannot determine whether the side effect happened. ([docs.temporal.io](https://docs.temporal.io/activity-definition)) |
| **E3** | External evidence | Progress and closure information matter when a result depends on whether further evidence can arrive. ([timelydataflow.github.io](https://timelydataflow.github.io/timely-dataflow/chapter_3/chapter_3_1.html)) |
| **D1** | Selected design | Invocation lifetime is independent of transport lifetime; events are admitted inputs, not a replacement for declared intent. |
| **D2** | Selected design | One construction evaluator serves local and durable hosts. Infrastructure does not become a second business interpreter. |
| **D3** | Selected design | Stable evidence and effect identities survive recovery; program versions preserve interpretation. |
| **D4** | Selected design | Demand, business eligibility, input authority, and worker execution rights remain distinct. |
| **D5** | Selected design | Scheduling batches do not silently define business transactions; admission and joining semantics are explicit. |
| **V1** | Verification outstanding | The latest evaluator satisfies the full causal-demand contract across the intended modeling language. |
| **V2** | Verification outstanding | A durable host preserves identity, purity, admission, and authority across all specified failure windows. |
| **V3** | Verification outstanding | The developer-facing receive and versioning vocabulary expresses the representative applications without workflow duplication. |
| **V4** | Implementation selection | The concrete durable host is chosen by conformance and operational evidence, not brand preference or presumed architectural compatibility. |

These unresolved items do not suspend the architectural direction. They identify the exact demonstrations needed before its implementation can be accepted.

---

## 20. Governing review standard

The architecture is reviewed against the complete product contract, not against the preceding implementation or the most recent defect.

A superior implementation makes the business model more expressive, preserves stronger invariants, and reduces independent mechanisms. It does not merely rename an authorization subsystem, move a classifier into another module, or wrap eager execution with additional checks.

Every component must have a precise responsibility:

**Pydantic establishes declared value semantics.  
The construction graph establishes source relationships.  
Admission establishes usable evidence.  
The evaluator establishes the next justified work.  
The execution host preserves progress and performs effects.  
Interfaces and telemetry project the same program and its history.**

A proposed change is accepted when its semantic benefit is explicit, its consequences across these boundaries are accounted for, and its adversarial tests can falsify the claim. Historical preferences and sunk cost do not count as architectural justification.

The event transition does not dilute TCA’s declarative nature. It exposes requirements that the request-bound implementation could leave implicit: evidence arriving over time, durable occurrence identity, source closure, versioned state, and uncertainty around external effects.

**The completed TCA is the same architectural idea expressed more fully: business types declare what may be constructed and what evidence justifies action; the engine realizes that program correctly across interfaces, time, concurrency, and failure.**