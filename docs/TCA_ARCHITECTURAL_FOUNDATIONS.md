# TCA Architecture

**Status:** Target architecture  
**Owner:** Kyle Tobin  
**Date:** October 28, 2026\
**Structure:** arc42  
**Product:** [TCA Product Definition](product.md)

This document states the refined target design. It does not claim implementation acceptance. Where earlier architectural records conflict with the explicit decisions here, this document governs the target; those records require reconciliation.

## 1. Introduction and goals

TCA executes a business program expressed through domain types and declared relationships. The application defines values, conditions, external sources, prerequisites, and outcomes. The framework derives justified execution without a separately authored business workflow.

The architecture has two packages: `world` supplies reusable value semantics; `engine` interprets execution relationships. Pydantic performs native value construction. Python represents the graph, evidence, evaluation results, and execution protocol.

The primary quality goals are:

- **Correctness:** every operation has established demand, eligibility, and execution permission.
- **Progress:** missing evidence permits justified acquisition; independent work remains concurrent.
- **Composability:** shared dependencies, alternatives, collections, and repetition preserve their declared meaning.
- **Explainability:** results identify the evidence and relationships supporting execution or withholding it.
- **Simplicity:** independent facts are represented directly; decisions are derived without separately maintained competing state.

## 2. Constraints

- Python and Pydantic are the implementation foundation. Native construction is delegated to Pydantic rather than reconstructed inside the engine.
- Application declarations, reusable primitives, and adapters are trusted code. TCA is not a Python sandbox.
- Validators are deterministic over their supplied values, perform no external effects, and read no ambient clock, randomness, or mutable configuration.
- Engine-mediated validation uses `context=None`. Business information enters through declared premises.
- The engine contains no application-specific branches.
- Historical values must satisfy the supported ownership contract. Frozen wrappers alone do not establish ownership.
- External systems retain authority over their permissions, transactions, and guarantees of repeat safety.
- Function counts, line limits, and the number of graph variants are engineering observations, not architectural constraints.

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

While a choice is unresolved, acquire declared decision prerequisites under their own eligibility and preserve work independently justified across remaining alternatives. Withhold branch-specific result work.

For conditional alternatives, select a branch when its conditions are established and every competitor is excluded by established condition refusal. Multiple qualifying branches are ambiguous. Malformed construction does not exclude a branch as a business decision.

### Delivery and recovery

Immediate and delayed observations use the same admission rules. A receipt acknowledges an operation without completing its business result.

An attributed return that supplies no admitted result preserves execution provenance and leaves the outcome uncertain. A late valid result may satisfy the logical effect even while a later attempt is in flight. No further attempt is then proposed; the in-flight attempt remains recorded and its observations are still processed.

### Collections

An evolving collection admits identified members and has an explicit closing relationship. Per-member work can proceed before closure. Aggregate finality, absence, and uniqueness over the source require closure.

A closed collection produces a finite tuple. A closer is scoped to its declared collection occurrence; it cannot close a sibling. Later new members are recorded as rejected for that closed occurrence. Corrections require a new declared occurrence, not mutation of the closed tuple.

## 7. Deployment view

Local and durable hosts share declaration, construction, admission, and evaluation semantics. A local host retains state in memory. A durable host preserves invocation state and resumes work without retaining the original request or coroutine.

The durable protocol is:

1. Load a revision and its pinned program artifact.
2. Evaluate.
3. Commit intents and required receiving state against the expected revision.
4. Dispatch only committed work that remains justified.
5. Retain attempt observations and admission results.
6. Advance from the resulting revision.

A durable inbox retains early deliveries until their receiving relationship can be resolved. Retention is not admission.

Worker coordination rejects stale commits and duplicate dispatch authorization. External execution is not atomic with local recording; recovery depends on capability guarantees.

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

Nested revalidation remains native behavior. Recovery must not accidentally normalize a serialized output again: retain original boundary inputs and mode, or use a versioned restoration representation with demonstrated fidelity.

### Construction outcomes

| Actual native outcome | Engine result |
|---|---|
| Validation succeeds | `Witness` containing the returned value and supplied-premise lineage |
| Every reported validation error is `tca_refuted` | `Refuted` |
| Any reported validation error has another type | `Invalid` |
| A non-validation exception escapes | `Faulted` |

Classification concerns the actual native attempt, not hypothetical errors on paths Pydantic did not execute. A successful union remains successful after a refused candidate. Mixed refusal and malformed sibling errors are invalid construction.

### Ownership and caching

Check ownership before publishing every witness or retaining accepted or admitted values. Supported content consists of immutable scalar values, owned enum values, tuples, frozen sets, and frozen models whose retained contents also satisfy ownership.

Copy externally owned mappings before exposing read-only views, and validate their contents. Retained diagnostics use owned data rather than live mutable exception objects.

Raw envelopes are owned snapshots separate from business values. Validation receives fresh working containers where needed; it cannot mutate retained history.

Memoization is scoped to an evaluation and its relevant occurrence and demand context. Shared construction may be reused without bypassing native enclosing validation. No cache is independent business authority.

### Identity and provenance

Logical effect identity distinguishes invocation, artifact, interaction, construction occurrence, subject scope, and repetition. Retries retain that identity and allocate a new attempt number. Equal payloads do not merge distinct operations.

Evidence identity comes from admitted history. Collection members retain distinct identities even when their values match. No process address, incidental hash, or payload hash supplies business identity.

Direct provenance comes from actual host dispatch. Delayed provenance requires an adapter-established source and a matching dispatched attempt for the stated effect. Supplied identifiers and arrival order alone establish nothing.

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
3. Otherwise, no dispatched attempt permits the first attempt.
4. A definitive failure of the latest attempt permits the next.
5. Uncertainty or an attributed answer without an admitted result follows recovery policy.
6. An outstanding attempt or receipt alone waits.

Only established observations affect attempt knowledge. Earlier attempts do not repeatedly authorize retries after a new attempt starts.

Under `retry`, the capability guarantees repeat safety or provider idempotency using the stable logical effect identity. Under `reconcile`, no automatic redispatch occurs while uncertain; authoritative evidence must resolve it. No polling operation is inferred.

### Admission, cardinality, and conflicts

Admission checks the pinned artifact, established source, native construction, all declared correlations, intent authority where required, receiving cardinality, and closure.

Deduplication identifies delivery within its source and receiving namespace, then compares role, mode, relationship, and owned envelope content with type-sensitive equivalence. An identity collision with different content is recorded as a rejected delivery conflict; it cannot replace admitted evidence.

Result equivalence is type-sensitive structural equivalence of complete constructed content. Comparison preserves exact types recursively and scalar representation distinctions, including Decimal sign, digits, and exponent and timestamp fields, fold, and zone. Thus `Decimal("2.5")` and `Decimal("2.50")` are different results. Applications normalize immaterial differences through declared construction; the engine does not normalize them during comparison.

Comparison returns a definite result for every pair of supported values, independently of ambient configuration and process identity, and preserves its result across independent construction and faithful restoration. Native model equality or equality of serialized outputs is not sufficient unless it preserves all distinctions required by this contract. Delivery and result comparison may share the structural comparison mechanism while comparing their respective content.

For a single-result occurrence, the first valid correlated result fills it. A later equivalent valid result adds no second value. A materially different otherwise admissible result creates an evidence conflict while preserving the admitted result and the later claim. Invalid or unauthorized claims do not create authoritative evidence conflicts.

An admitted result and definitive failure attributed to the same attempt are incompatible established claims. Failure of one attempt and success of another are compatible. Uncertainty followed by an established result or definitive failure is resolution, not contradiction.

An unresolved evidence conflict withholds further attempts for the disputed effect and any undispatched work relying on the disputed occurrence through its request, eligibility, or demand prerequisites. Committed but undispatched intents are rechecked and withheld. A shared operation may still proceed through an independent justification if its request and eligibility are unaffected.

Previously dispatched work is not undone. Its observations remain recorded. Completed invocations are not silently reopened; later conflicts remain visible faults. Independent work continues. This design provides no automatic conflict winner or conflict-clearing mechanism.

### Lifecycle, security, and interfaces

Dispatch requires current justification at the host's authoritative dispatch decision. A conflict or cancellation recorded afterward cannot retroactively prevent an already authorized external call.

Cancellation stops new work and retains in-flight uncertainty and prior effects. Caller disconnection is not invocation cancellation.

Admission authority, business eligibility, and worker execution authority remain distinct. Database transactions and provider permissions are enforced at their owning systems.

Interfaces derive schemas and explanations from declarations while preserving documented native input modes. Telemetry observes execution, does not control it, and excludes payloads and credentials by default.

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

These decisions refine the earlier architecture. Individual ADRs may record rationale and evidence, but must not silently restore conflicting rules or duplicate this specification.

## 10. Quality requirements

| Scenario | Required result |
|---|---|
| Pure refusal, mixed errors, successful union, programmer exception | Correct construction classification |
| Defaults, aliases, null, factories, nested validation, replacements | Agreement with native calls under matching inputs and `context=None` |
| Missing, refused, and successful prerequisite | Acquisition, withholding, and release respectively; independent progress preserved |
| Shared consumers and conditional alternatives | No borrowed guard, speculative branch work, or malformed-input fallback |
| Forged identifiers and correctly attributed invalid returns | No invented authority; established provenance retained |
| Receipt/uncertainty permutations | Equivalent execution permission |
| Definitive failure and result for one attempt | Explicit conflict; affected undispatched work withheld |
| Failure and success across different attempts | Compatible history |
| Retry followed by reevaluation and late completion | No repeated permission; no further retry after completion; in-flight history retained |
| Mutable replacement or caller mutation | No unowned witness and no historical mutation |
| Independent construction and faithful restoration | Equivalent retained content compares consistently; exact type and scalar representation differences remain distinguishable; hashing, where provided, agrees with equality |
| Open and closed collections | Per-member progress, scoped closure, and stable final tuple |
| Process loss and stale workers | Stable identities, retained effects, and rejection of stale commits |

Tests assert public behavior independently of evaluator helpers. Pair prevention with valid progress. Measure shared construction on graph-shaped examples and compare memoized behavior with equivalent uncached evaluation.

Durable acceptance requires fault injection around intent commitment, dispatch, provider completion, recording, admission, and response delivery. Native construction probes do not establish those guarantees.

## 11. Risks and technical debt

- The executable contract still requires composition testing; local fixes can preserve examples while breaking shared demand or alternatives.
- Adapters must not report uncertainty as definitive failure or populate trusted fields directly from untrusted envelopes.
- Ownership checks must cover actual replacement values and retained metadata, not only declared field types.
- The durable codec, artifact packaging, storage backend, and worker coordination require implementation selection and evidence.
- Unresolved authoritative conflicts require intervention; automatic resolution is outside this design.
- Isolated mechanics were checked on Pydantic 2.14.1. Repository compatibility must be verified against its selected lockfile.
- Earlier ADRs and repository instructions need reconciliation where they conflict with this refinement. Their presence is not implementation acceptance.
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
| Attempt | One physical dispatch of a logical effect |
| Admission | Establishment of usable evidence from an observation |
| Closure | Established completion boundary for an evolving source |
| Conflict | Incompatible established claims retained without overwriting history |
| Cardinality | Number of values a receiving occurrence admits |
| Owned value | Retained content without external writable aliases within the supported domain |
| Host | Execution and persistence machinery for justified work |
