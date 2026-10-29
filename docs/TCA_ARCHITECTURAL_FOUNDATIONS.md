# TCA Architecture

**Status:** Target architecture  
**Owner:** Kyle Tobin  
**Date:** October 29, 2026  
**Structure:** arc42  
**Product:** [TCA Product Definition](product.md)

This document and the decision register in `ADR.md` specify the current target architecture. They do not establish implementation acceptance.

## 1. Introduction and goals

TCA executes a business program expressed through domain types and declared relationships. The application defines values, conditions, external sources, prerequisites, and outcomes. The framework derives justified execution without a separately authored business workflow.

The architecture has two packages: `world` supplies reusable value semantics; `engine` interprets execution relationships. Pydantic performs native value construction. Python represents the graph, evidence, evaluation results, and execution protocol.

The primary quality goals are:

- **Single authored business model:** developers express business meaning once; TCA derives coordination without a second account of execution.
- **Practical authoring:** application development, composition, extension, and diagnosis use the public model rather than engine internals.
- **Correctness:** every operation has established demand, eligibility, and execution permission.
- **Progress:** missing evidence permits justified acquisition; independent work remains concurrent.
- **Composability:** shared dependencies, alternatives, collections, and repetition preserve their declared meaning.
- **Explainability:** results identify the evidence and relationships supporting execution or withholding it.
- **Simplicity:** independent facts are represented directly; decisions are derived without separately maintained competing state.

## 2. Constraints

Business meaning resides in declared types and relationships. World supplies reusable value semantics; Pydantic owns complete native construction. The engine supplies justified premises, interprets explicit execution relationships, records independent evidence, and derives justified work. Hosts execute and retain that work under the same interpretation.

Every framework mechanism must discharge a specific product or architectural obligation within this division. An observable Python distinction, an imaginable edge case, or a dependency introduced by another mechanism does not create a framework requirement.

- Python and Pydantic are the implementation foundation. Native construction is delegated to Pydantic rather than reconstructed inside the engine.
- Application declarations, reusable primitives, and adapters are trusted code. TCA is not a Python sandbox.
- Native validation at the same complete boundary with the same supplied inputs, native mode, and declared policy is deterministic. Validators perform no external effects and read no ambient clock, randomness, or mutable configuration. Supplying an existing witness to another construction is a new native attempt, not a promise of equal output.
- Engine-mediated validation uses `context=None`. Business information enters through declared premises.
- The engine contains no application-specific branches.
- Historical values must satisfy the supported ownership contract. Frozen wrappers alone do not establish ownership.
- External systems retain authority over their permissions, transactions, and guarantees of repeat safety.
- Representations and mechanisms serve the declared program and its justified execution. Their incidental size, Python observability, or dependency on another mechanism supplies no additional business meaning.

## 3. Context and scope

The developer's application combines two vocabularies:

| Vocabulary | Meaning |
|---|---|
| Domain types composed from world primitives | What values exist, what makes them valid, and what follows from their operands |
| Execution declarations | Where occurrences obtain evidence, which prerequisites govern demand, and which external work participates |

World is independent of execution. It does not know about invocations, provenance, occurrence paths, attempts, or recovery.

The engine exposes declarations, observation ingress, evaluation results, and host operations. Direct calls, CLI, APIs, and event ingress project those contracts. Commands request work, queries request information, and events report occurrences; transport does not determine their role.

Trusted adapters establish external source identity and construct observations. External callers do not deserialize complete engine observations from the wire. A valid payload alone establishes neither source authority nor execution provenance.

TCA coordinates application execution. Authoritative business storage, provider authorization, and external transaction semantics remain outside its authority.

### Application authoring contract

| Developer authors | TCA derives or manages |
|---|---|
| Business values, constraints, computations, conditions, and compositions through types | Complete native construction and actual outcomes |
| Explicit supplying occurrences and relationships where type information does not establish them | Binding resolution, shared occurrence graph, and premise acquisition |
| Conditional demand, capability contracts, permitted sources, correlations, and collection closure | Demand propagation, admission, justified proposals, dispatch coordination, and continuation |
| Reusable value operations and capability adapters through public extension boundaries | Generic interpretation without application-specific engine changes |

A business rule has one authoritative expression in the declared model. Application code does not restate it in transport handlers, workflow steps, or persistence coordination. Developers do not manually schedule dependencies or manage revisions, attempts, receiving registration, and recovery bookkeeping to express business behavior.

Public types and declarations support reuse, nesting, alternatives, shared dependencies, and collection scopes without changing the meaning of the composed parts. Framework syntax preserves native annotations and metadata. The declaration contract specifies which relationships type information establishes, which require explicit declarations, how lexical resolution works, and how ambiguity is diagnosed. It does not require manually duplicating a dependency already established by that contract.

Value extensions implement reusable world semantics through native construction; adapters implement external capability contracts. Neither extension introduces a second business workflow. Diagnostics identify application occurrences and relationships; routine application development does not require knowledge of engine records or worker mechanics.

## 4. Solution strategy

Compile explicit construction and execution relationships into a shared graph. Evaluate that graph against an immutable invocation revision.

Keep two judgments separate:

- **Construction:** what the complete declared boundary actually constructed, or why it did not.
- **Demand:** why a particular consumer requires an occurrence and which established prerequisites justify that demand.

A demanded external operation also requires a constructed request, satisfied universal eligibility, and permission derived from execution history.

Record observations, provenance, admission, and conflicts independently. Derive permission in this order: relevant conflict, admitted logical result, latest attempt's established facts.

The host commits and executes proposals. It does not independently select business branches. Evaluation results contain their explanations; downstream code consumes their structure rather than interpreting diagnostic strings.

## 5. Building block view

### World

| Module | Responsibility |
|---|---|
| `base.py` | Value vocabulary: scalar values, composite records, and observation-oriented facts |
| `relations.py` | Reusable computations, comparisons, and finite selections |
| `refusal.py` | Reserved condition-refusal error protocol; no side-channel collector |

World models use frozen, strict configuration, forbid extra fields, revalidate model instances, and do not enable arbitrary types. Declared collection values use tuples and frozen sets. Enums express closed vocabularies.

Relations validate their operands natively before evaluating predicates. A condition that does not hold raises `PydanticCustomError` with the reserved code `tca_refuted`. Only trusted world condition implementations emit this code. Computations derive their results from validated operands; callers cannot substitute a supplied result for that computation.

Comparisons, computations, and selections share a public vocabulary without requiring identical validator implementations. An observation-oriented type does not authenticate its own origin; the engine establishes its source relationship.

World provides composable public types for value semantics through ordinary Python/Pydantic typing. Concrete validator arrangements, accessors, and stored derived fields are implementation choices constrained by native construction, validated operands, ownership, and prevention of caller-supplied substitute results. They do not impose universal idempotent revalidation on application types.

### Engine

| Module | Responsibility |
|---|---|
| `declare.py` | Execution relationships and capability declarations |
| `graph.py` | Compilation, source resolution, graph sharing, and declaration diagnostics |
| `record.py` | Identity, immutable invocation records, ownership, and envelope equivalence |
| `construct.py` | Complete native construction and outcome classification |
| `evaluate.py` | Construction, demand propagation, choice resolution, and permission |
| `admit.py` | Independent provenance and business-admission judgments |
| `host.py` | Invocation lifecycle, intent commitment, attempts, dispatch, and delivery |

Internal graph nodes, records, and result variants use typed Python structures, normally frozen dataclasses. Pydantic models express business values and their native construction boundaries.

The declaration vocabulary includes:

- `Bound`: reference to a declared supplying occurrence.
- `When[C, R]`: successful complete construction of C releases this consumer's demand for R.
- `Interaction`: source, request, report types, receipt role, correlation, eligibility, and recovery contract.
- `Receive`: a permitted external receiving relationship.
- `Members`: member evidence and the relationship closing its collection.
- `Goal` and `Program`: accepted inputs, requested outcome, declarations, and pinned artifact.

The compiler resolves bindings lexically, preserves complete annotations and metadata, and diagnoses unknown sources, conflicting bindings, impossible projections, unsupported mutable declarations, and instantaneous construction cycles. Work requests require resolved premises. Multiple collection sources require an explicit relationship rather than an inferred join.

The concrete declaration design must resolve type-directed binding, explicit occurrence references, annotation metadata, scope, defaults, and ambiguity together. Equal types do not establish shared identity or execution authority. Public syntax expresses the necessary relationships without requiring a separately authored copy of the compiled graph.

The graph distinguishes accepted inputs, references, products, conditionals, choices, work, receives, and collections. Shared identity follows declared occurrences, not class equality.

## 6. Runtime view

### Conditional construction and work

1. Establish demand from the requested goal.
2. Resolve and construct the condition's premises.
3. If evidence is missing, pursue justified acquisition or report a legitimate wait.
4. If the complete condition constructs, release this consumer's demand for its dependent result.
5. Construct the operation's request and universal eligibility.
6. Derive attempt permission and propose justified work.
7. Commit the intent, record the attempt, dispatch, and record the resulting observation.
8. Admit usable evidence and reevaluate the new revision.

A product demands its premises jointly. Field order and holder validators do not invent execution dependencies. Holder validation runs when the complete holder, including external results, can be constructed. Its failure does not erase earlier justified effects.

### Alternatives

Native union construction over available values belongs to Pydantic. Selecting branch-specific external work belongs to the engine.

Selection prerequisites are identified by explicit execution relationships. A condition's presence as a holder field alone does not make it a branch-selection prerequisite. Selection establishes justified branch work; it does not predetermine Pydantic's subsequent union outcome.

While a choice is unresolved, acquire declared decision prerequisites under their own eligibility and preserve work independently justified across remaining alternatives. Withhold branch-specific result work.

For conditional alternatives, select a branch when its conditions are established and every competitor is excluded by established condition refusal. Multiple qualifying branches are ambiguous. Malformed construction does not exclude a branch as a business decision.

### Delivery and recovery

Immediate and delayed observations use the same admission rules. A receipt acknowledges an operation without completing its business result.

An attributed return that supplies no admitted result preserves execution provenance and leaves the outcome uncertain. A late valid result may satisfy the logical effect even while a later attempt is in flight. No further attempt is then proposed; the in-flight attempt remains recorded and its observations are still processed.

### Collections

An evolving collection admits identified members and has an explicit closing relationship. Per-member work can proceed before closure. Aggregate finality, absence, and uniqueness over the source require closure.

A closed collection produces a finite tuple. A closer is scoped to its declared collection occurrence; it cannot close a sibling. Later new members are recorded as rejected for that closed occurrence. Corrections require a new declared occurrence, not mutation of the closed tuple.

## 7. Deployment view

Local and durable hosts share declaration, construction, admission, and evaluation semantics. A local host retains state in memory. A durable host preserves invocation state and resumes work independently of the live initiating request or coroutine. Necessary construction inputs, native modes, and lineage may be retained as data.

A host-specific reduction in supported construction modes or programs is an architectural contract change. Storage convenience does not authorize making Python-mode programs local-only.

The durable protocol is:

1. Load a revision and its pinned program artifact.
2. Evaluate.
3. Commit intents and required receiving state against the expected revision.
4. Dispatch only committed work that remains justified.
5. Retain attempt observations and admission results.
6. Advance from the resulting revision.

A durable inbox retains early deliveries until their receiving relationship can be resolved. Retention is not admission.

Worker coordination rejects stale commits and duplicate dispatch authorization. An outstanding authorization prevents another authorization of the same attempt even when dispatch is not established. Committed work remains discoverable for continuation across process loss; persistence and scheduling must close the gap between commitment and wakeup. External execution is not atomic with local recording; recovery depends on capability guarantees.

Each invocation retains access to its executable artifact and compatible dependencies. An unavailable artifact produces a fault rather than recovery under current code. Migration is outside the initial design.

The storage backend, scheduler, and deployment topology remain unselected. Established infrastructure should supply these mechanics without requiring a second application workflow.

## 8. Crosscutting concepts

### Native construction

One integration boundary invokes Pydantic with the complete declared type and retains its actual returned value. Pydantic applies native defaults, aliases, constraints, nested revalidation, union selection, and world validators that compute values and evaluate conditions. The engine supplies inputs and classifies the actual outcome; it does not replace or reinterpret native construction behavior. Comparing retained evidence is a separate engine responsibility.

| Input | Construction policy |
|---|---|
| Internal premise map | Field names enabled; alias reinterpretation disabled |
| External payload | Declared native mode and alias behavior |
| Omitted holder field | Leave the key out; native defaults and factories apply |
| Explicit null | Preserve as supplied input |
| Validation context | Always `None` |

Whole-value omission uses the complete boundary's native omission behavior. A standalone field-type adapter is not a substitute for holder defaults.

Each construction preserves the complete annotation and its metadata. Nested revalidation remains native behavior and its actual result is authoritative. Repeating construction from the same inputs is distinct from constructing a previously returned value again; the latter need not return an equal value.

Recovery retains original boundary inputs and mode, or uses a versioned restoration representation with demonstrated fidelity. Restoring an established value preserves recorded meaning without accidentally applying normalization again. Subsequently supplying that restored value to an enclosing construction follows that boundary's native validation behavior.

The chosen restoration protocol must specify what is retained, how native input modes are preserved, and how continuation recovers recorded meaning. Input replay requires a fidelity argument covering those boundaries; determinism and artifact pinning alone do not establish the protocol.

### Construction outcomes

| Actual native outcome | Engine result |
|---|---|
| Validation succeeds | `Witness` containing the returned value and supplied-premise lineage |
| Every reported validation error is `tca_refuted` | `Refuted` |
| Any reported validation error has another type | `Invalid` |
| A non-validation exception escapes | `Faulted` |

Classification concerns the actual native attempt, not hypothetical errors on paths Pydantic did not execute. A successful union remains successful after a refused candidate. Mixed refusal and malformed sibling errors are invalid construction.

### Ownership and caching

Ownership protects retained history from external writable aliases. It establishes neither equality, canonical form, serializability, nor preservation of arbitrary subsequent Python behavior.

Check ownership before publishing every witness or retaining accepted or admitted values. Supported content consists of immutable scalar values, owned enum values, tuples, frozen sets, and frozen models whose retained contents also satisfy ownership.

Copy externally owned mappings before exposing read-only views, and validate their contents. Retained diagnostics use owned data rather than live mutable exception objects.

Raw envelopes have a separate owned snapshot contract. Input dictionaries and lists may be represented faithfully without retaining external writable aliases; they need not satisfy the constructed business-value domain or use its restoration encoding. Validation receives fresh working containers where needed and cannot mutate retained history.

Memoization is scoped to an evaluation and its relevant occurrence and demand context. Shared construction may be reused without bypassing native enclosing validation. No cache is independent business authority.

Reusable construction outcomes remain separate from consumer-specific demand and execution justifications. Reuse cannot transfer authorization between consumers or erase surviving independent justifications when another consumer is blocked.

### Identity and provenance

Logical effect identity distinguishes invocation, artifact, interaction, construction occurrence, subject scope, and repetition. Retries retain that identity and allocate a new attempt number. Equal payloads do not merge distinct operations.

Evidence identity comes from admitted history. Collection members retain distinct identities even when their values match. No process address, incidental hash, or payload hash supplies business identity.

Direct provenance comes from actual host dispatch. Delayed provenance requires an adapter-established source and a matching dispatched attempt for the stated effect. Supplied identifiers and arrival order alone establish nothing.

Authorization to dispatch, evidence of actual dispatch, and evidence of external completion establish different facts. An authorization record alone proves neither dispatch nor completion. Failed payload construction or admission cannot erase provenance established independently.

If execution may have occurred after authorization but dispatch evidence is absent, retain that uncertainty about the authorized attempt. Do not infer that no call occurred or manufacture direct dispatch provenance. Recovery of a new attempt requires the capability's repeat-safety or reconciliation contract.

### Observation meaning and permission

| Role | Meaning |
|---|---|
| Receipt | Acknowledgement without completed business result |
| Result | Reported business outcome, including a negative business answer |
| Failed | Established non-completion of the attempt and established safety of repetition |
| Uncertain | Completion is not established either way |

Timeouts, adapter exceptions, disconnects, and local recording failures are uncertain. An adapter reports failed only when its capability contract establishes the stronger meaning.

Permission is derived centrally:

1. A relevant unresolved conflict withholds work as specified below.
2. An admitted logical result prevents further attempts.
3. Otherwise, no prior authorized attempt permits the first authorization; an outstanding authorization cannot be issued again.
4. A definitive failure of the latest attempt permits the next.
5. Uncertainty or an attributed answer without an admitted result follows recovery policy.
6. An outstanding authorization, dispatched attempt, or receipt alone waits unless established uncertainty invokes the recovery policy.

Only established observations affect attempt knowledge. Earlier attempts do not repeatedly authorize retries after a new attempt starts.

Permission accounts for authorization records to prevent duplicate calls without treating those records as proof of dispatch. A lost authorization-to-dispatch interval follows the uncertainty rule above, retaining what is known and unknown.

Under `retry`, the capability guarantees repeat safety or provider idempotency using the stable logical effect identity. Under `reconcile`, no automatic redispatch occurs while uncertain; authoritative evidence must resolve it. No polling operation is inferred.

### Admission, cardinality, and conflicts

Admission checks the pinned artifact, established source, native construction, all declared correlations, intent authority where required, receiving cardinality, and closure.

Deduplication identifies delivery within its source and receiving namespace, then compares role, mode, relationship, and owned envelope content under the delivery comparison contract. Delivery identity is distinct from content: equal payloads alone do not establish one delivery occurrence, and a missing transport identifier does not authorize substituting a payload digest for occurrence identity. An identity collision with different content is recorded as a rejected delivery conflict; it cannot replace admitted evidence.

Delivery comparison determines whether a repeated delivery identity carries the same retained envelope content. Result comparison determines whether an otherwise admissible claim repeats or contradicts the result for that receiving occurrence. These are separate receiving-contract judgments; they establish neither business identity, ownership, provenance, nor correlation meaning.

The concrete design must specify both comparison contracts and justify the distinctions each preserves through its receiving responsibility. Business normalization and conditions belong to declared types and relationships. Comparison does not introduce additional business distinctions merely because Python can observe them, define general equality for engine records or histories, or restrict native construction and supported values for comparator convenience.

For a single-result occurrence, the first valid correlated result fills it. A later equivalent valid result adds no second value. A materially different otherwise admissible result creates an evidence conflict while preserving the admitted result and the later claim. Invalid or unauthorized claims do not create authoritative evidence conflicts.

An admitted result and definitive failure attributed to the same attempt are incompatible established claims. Failure of one attempt and success of another are compatible. Uncertainty followed by an established result or definitive failure is resolution, not contradiction.

An unresolved evidence conflict withholds further attempts for the disputed effect and any undispatched work relying on the disputed occurrence through its request, eligibility, or demand prerequisites. Committed but undispatched intents are rechecked and withheld. A shared operation may still proceed through an independent justification if its request and eligibility are unaffected.

Previously dispatched work is not undone. Its observations remain recorded. Completed invocations are not silently reopened; later conflicts remain visible faults. Independent work continues. This design includes no engine operation for affirming a winner or clearing an authoritative conflict. External intervention supplies no new evidence authority by itself and does not establish non-completion or repeat safety. An engine conflict-resolution capability is an architectural extension requiring approval.

### Lifecycle, security, and interfaces

Dispatch requires current justification at the host's authoritative dispatch decision. A conflict or cancellation recorded afterward cannot retroactively prevent an already authorized external call.

Cancellation stops new work and retains in-flight uncertainty and prior effects. Caller disconnection is not invocation cancellation.

Admission authority, business eligibility, and worker execution authority remain distinct. Database transactions and provider permissions are enforced at their owning systems.

Interfaces derive schemas and explanations from declarations while preserving documented native input modes. Telemetry observes execution, does not control it, and excludes payloads and credentials by default.

Declaration diagnostics name missing or ambiguous relationships in the public model. Runtime explanations identify the requested outcome, relevant occurrences, established evidence, failed construction, and outstanding prerequisites. Interface and extension code consume these same contracts instead of restating business rules.

## 9. Architectural decisions

| Decision | Rationale |
|---|---|
| Separate world and engine | Value vocabulary remains reusable and independent of execution |
| Delegate complete construction to Pydantic | Avoid a second implementation of value semantics |
| Use a reserved structured refusal code | Preserve native error association without a collector |
| Use `context=None` | Keep business inputs in explicit premises |
| Separate construction and demand | Constructibility alone neither demands nor authorizes work |
| Separate provenance and admission | Invalid content cannot erase known execution; valid content cannot invent it |
| Derive permission from independent records | Avoid competing status state and arrival-order interpretation |
| Separate cardinality from conflict | One retained result does not make the first claim universally authoritative |
| Put explanations in results | Consumers inspect evidence and relationships rather than diagnostic names |
| Share semantics across hosts | Persistence and scheduling do not create another business program |

The decision register records the governing commitments and rationale consistently with these contracts. Proposed implementations are assessed against both documents.

## 10. Quality requirements

| Scenario | Required result |
|---|---|
| Business rule changes | One authoritative rule changes in the declared model; orchestration and transport code do not repeat the change |
| Reuse, nesting, and extension | Composition preserves declared meaning, scopes, and native enclosing construction; new value operations or adapters require no application-specific engine branch |
| Declaration authoring | Necessary relationships are expressible without manually reproducing the compiled graph; ambiguity is diagnosed rather than guessed |
| Developer diagnosis | Explanations trace behavior through application types, occurrences, relationships, and evidence without requiring engine-internal knowledge |
| Pure refusal, mixed errors, successful union, programmer exception | Correct construction classification |
| Defaults, aliases, null, factories, nested validation, replacements | Agreement with native calls under matching inputs and `context=None` |
| Missing, refused, and successful prerequisite | Acquisition, withholding, and release respectively; independent progress preserved |
| Shared consumers and conditional alternatives | No borrowed guard, speculative branch work, or malformed-input fallback |
| Forged identifiers and correctly attributed invalid returns | No invented authority; established provenance retained |
| Receipt/uncertainty permutations | Equivalent execution permission |
| Definitive failure and result for one attempt | Explicit conflict; affected undispatched work withheld |
| Failure and success across different attempts | Compatible history |
| Retry followed by reevaluation and late completion | No repeated permission; no further retry after completion; in-flight history retained |
| Repeated delivery identity | Delivery comparison distinguishes repetition from changed envelope content; collisions cannot replace admitted evidence |
| Repeated otherwise admissible result | Result comparison distinguishes repetition from contradiction within its receiving contract |
| Owned retained history | Caller mutation and validation working copies cannot change retained facts; ownership does not depend on record equality |
| Durable continuation | The chosen restoration protocol preserves recorded meaning and supported native input modes under the pinned artifact |
| Open and closed collections | Per-member progress, scoped closure, and stable final tuple |
| Process loss and stale workers | Stable identities, retained effects, and rejection of stale commits |
| Loss between authorization and established dispatch | No duplicate authorization, no invented dispatch fact, and capability-governed recovery |
| Committed work before scheduling | Continuation discovers the work after process loss; a missing wakeup cannot strand it |

Tests assert public behavior independently of evaluator helpers. Pair prevention with valid progress. Measure shared construction on graph-shaped examples and compare memoized behavior with equivalent uncached evaluation.

Durable acceptance requires fault injection around intent commitment, dispatch, provider completion, recording, admission, and response delivery. Native construction probes do not establish those guarantees.

## 11. Risks and technical debt

- The executable contract still requires composition testing; local fixes can preserve examples while breaking shared demand or alternatives.
- Adapters must not report uncertainty as definitive failure or populate trusted fields directly from untrusted envelopes.
- Ownership checks must cover actual replacement values and retained metadata, not only declared field types.
- The restoration representation and protocol, artifact packaging, storage backend, and worker coordination require concrete design selection and evidence.
- Unresolved authoritative conflicts remain visible and withhold affected work; external intervention has no engine conflict-clearing authority under this design.
- Isolated mechanics were checked on Pydantic 2.14.1. Repository compatibility must be verified against its selected lockfile.
- Review findings must distinguish a violated rule from a newly discovered design problem. Changes to these rules are explicit architectural amendments.

## 12. Glossary

| Term | Meaning |
|---|---|
| World | Reusable native business-value vocabulary |
| Execution declaration | A relationship supplying occurrence, source, demand, or capability meaning |
| Construction | Native validation of a complete declared boundary |
| Witness | Actual constructed value with its occurrence and supplied-premise lineage |
| Demand | A consumer's justified need for an occurrence |
| Eligibility | An operation's universal prerequisites |
| Observation | A report constructed by a trusted adapter or host boundary |
| Evidence | An admitted value with identity, origin, and receiving occurrence |
| Provenance | Established association of an observation with an executed attempt |
| Occurrence | One declared realization in its invocation and subject scope |
| Invocation | One accepted pursuit of an outcome |
| Artifact | Immutable executable program and compatible dependencies |
| Logical effect | One intended external operation, independent of physical retries |
| Attempt | One numbered execution attempt for a logical effect; authorization alone does not establish dispatch |
| Admission | Establishment of usable evidence from an observation |
| Closure | Established completion boundary for an evolving source |
| Conflict | Incompatible established claims retained without overwriting history |
| Cardinality | Number of values a receiving occurrence admits |
| Owned value | Retained content without external writable aliases within the supported domain |
| Host | Execution and persistence machinery for justified work |
