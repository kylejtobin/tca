# Architectural Decisions

Agents MUST read this entire file before every compliance review.
Agents MUST NOT use grep, search, excerpts, summaries, or remembered content
to select or substitute for reading decisions.
Agents MUST assess work against every decision and satisfy every requirement
within its stated scope.
Changes require explicit human authorization. Git preserves prior versions.

Source: [TCA Architecture](TCA_ARCHITECTURAL_FOUNDATIONS.md). This register records its approved decisions; it does not establish implementation acceptance.

## Boundaries and authority

### D-001: Separate value semantics from execution (§§2–5)

- MUST: World supplies scalar values, composite records, observation-oriented facts, computations, comparisons, finite selections, and the refusal protocol; engine supplies declarations, graph compilation, records, construction integration, evaluation, admission, and host operations.
- MUST: Declared types and relationships own business meaning; Pydantic owns complete native construction; the engine supplies justified premises, interprets explicit execution relationships, records evidence, and derives justified work; every mechanism discharges a specific product or architectural obligation.
- MUST NOT: Infer framework requirements from incidental Python distinctions or dependencies introduced by other mechanisms.
- MUST NOT: World depend on execution concepts, or engine contain application-specific branches or require a separately authored business workflow.
- WHY: Business values remain reusable while one generic engine interprets declared execution relationships.

### D-002: Preserve trust and external authority (§§2–3, 8)

- MUST: Treat declarations, primitives, and adapters as trusted code; keep admission authority, business eligibility, and worker execution authority distinct, with business storage constraints, transactions, permissions, and repeat-safety guarantees enforced by their owning systems.
- MUST NOT: Treat TCA as a Python sandbox or claim atomicity between external execution and local recording.
- WHY: Coordination cannot manufacture guarantees owned by another system.

### D-003: Keep validation deterministic (§2)

- MUST: Validators compute deterministically from supplied values; engine-mediated validation uses `context=None`, with business information supplied through declared premises.
- MUST: World computations and predicates use explicit policies independent of caller configuration, yielding the same result or failure category for the same declared inputs, native mode, and policy across construction, subsequent access, composition, and reconstruction; caller configuration and arithmetic flags remain unchanged on success and failure.
- MUST NOT: Validators perform external effects or read ambient clocks, randomness, or mutable configuration.
- MUST NOT: Extend deterministic declared value semantics into a guarantee of arbitrary subsequent Python behavior or incidental object-sharing preservation.
- WHY: The same declared inputs must retain their meaning across evaluation and recovery.

## World and native construction

### D-004: Use native world value semantics (§5)

- MUST: World models use frozen, strict configuration, forbid extra fields, revalidate supplied model instances, and leave arbitrary types disabled; declared collections use tuples and frozen sets, and closed vocabularies use enums.
- MUST: Computations derive results from natively validated operands; comparisons and selections validate operands before evaluating their predicates.
- MUST: Collection operations enforce their declared operand and result requirements for empty, singleton, and multiple-member inputs; member count MUST NOT bypass those requirements.
- MUST NOT: Accept a supplied result as a substitute for computation or treat an observation-oriented type as authenticating its origin.
- WHY: Constructed domain values express their declared meaning without asserting execution authority.

### D-005: Reserve structured condition refusal (§§5, 8)

- MUST: Only trusted world condition implementations emit `PydanticCustomError` with code `tca_refuted`, after operand validation and when the declared condition does not hold.
- MUST NOT: Use a side-channel refusal collector or classify malformed operands as condition refusal.
- WHY: Native errors preserve the association between a failed condition and its construction location.

### D-006: Construct complete declared boundaries (§§2, 8)

- MUST: One engine integration boundary delegates complete construction to Pydantic, including native defaults, aliases, constraints, nested revalidation, union selection, and world computations and conditions; retain its actual returned value and supplied-premise lineage.
- MUST: Keep engine comparison of retained evidence separate from native construction.
- MUST NOT: Replace or reinterpret native construction behavior or substitute a standalone field-type adapter for complete holder construction.
- WHY: A second constructor would give declarations competing meanings.

### D-007: Preserve input and omission semantics (§8)

- MUST: Internal premise maps enable field names and disable alias reinterpretation; external payloads retain declared native mode and alias behavior; omitted holder fields remain absent so native defaults and factories apply; explicit null remains supplied input; whole-value omission uses the complete boundary's native behavior.
- WHY: Internal assembly and external input must preserve their documented construction contracts.

### D-008: Classify the actual native attempt (§8)

- MUST: Classify the native validation attempt as `Witness` on successful validation, `Refuted` when every reported validation error is `tca_refuted`, `Invalid` when any reported validation error has another type, and `Faulted` when a non-validation exception escapes.
- MUST NOT: Infer hypothetical errors from paths Pydantic did not execute, override successful union construction because a candidate refused, or classify mixed refusal and malformed-input errors as `Refuted`.
- WHY: Classification describes the constructor's actual outcome rather than engine speculation.

### D-009: Own retained values and envelopes (§§2, 8)

- MUST: Ownership protect retained history from external writable aliases; judge it independently of comparison, canonicalization, serialization, and durable encoding.
- MUST: Check actual returned contents before publishing witnesses or retaining accepted or admitted values; supported contents are immutable scalars, owned enum values, tuples, frozen sets, and frozen models with recursively owned contents.
- MUST: Raise a distinct engine ownership error when an engine ownership check fails, preventing publication or retention of the unowned content; keep this error separate from the native validation outcomes in D-008.
- MUST: Copy caller-owned mappings before exposing read-only views, validate their contents, retain diagnostics as owned data, and keep raw envelopes as owned snapshots separate from business values; validation receives fresh working containers when required to protect history.
- MUST NOT: Treat frozen wrappers as proof of deep ownership, retain live mutable exception objects, or permit validation to mutate retained history.
- WHY: A revision must not change through an external writable alias.

## Declarations, graph, and evaluation

### D-010: Compile explicit relationships (§5)

- MUST: Declarations express supplying occurrences, conditional demand, interactions and their capability contracts, receives, member sources and closure, accepted inputs, goals, and pinned programs; compilation resolves bindings lexically and preserves complete annotations and metadata.
- MUST: Diagnose unknown sources, conflicting bindings, impossible projections, unsupported mutable declarations, instantaneous construction cycles, and unresolved work-request premises; require an explicit relationship between multiple collection sources.
- MUST NOT: Infer a join between collection sources.
- WHY: Execution relationships must be established before runtime interpretation.

### D-011: Preserve occurrence identity in a shared graph (§5)

- MUST: Distinguish accepted inputs, references, products, conditionals, choices, work, receives, and collections; share identity by declared occurrence.
- MUST NOT: Merge occurrences because their classes are equal or impose arbitrary graph-variant counts, function counts, or line limits as architectural requirements.
- WHY: Sharing must preserve declared subjects and relationships.

### D-012: Separate construction from consumer demand (§§4, 6)

- MUST: Evaluate the graph against an immutable invocation revision, deriving demand from the goal; acquire missing condition evidence through justified work or report a legitimate wait; release a consumer's dependent demand only after its complete condition constructs.
- MUST: Require established demand, a constructed request, universal eligibility, and execution permission for every proposed operation.
- MUST NOT: Treat constructibility alone as demand or borrow another consumer's guard to authorize work.
- WHY: A value's availability does not establish a particular consumer's authority to act.

### D-013: Construct products jointly (§6)

- MUST: Products demand their premises jointly and run holder validation when the complete holder, including external results, can construct; retain earlier justified effects when holder validation fails.
- MUST NOT: Infer execution dependencies from field order or holder validators.
- WHY: Validation of a completed product does not declare causal ordering among its premises.

### D-014: Separate union construction from work selection (§6)

- MUST: Delegate native union construction over available values to Pydantic; while work selection is unresolved, acquire declared decision prerequisites under their own eligibility, preserve independently justified work, and withhold branch-specific result work.
- MUST: Select a conditional alternative only when its conditions are established and every competitor is excluded by established condition refusal; report multiple qualifying branches as ambiguous.
- MUST NOT: Use malformed construction to exclude a business alternative.
- WHY: Acquiring a decision and executing its selected branch are different judgments.

### D-015: Bound caching and preserve explanations (§§4–5, 8)

- MUST: Keep reusable construction outcomes separate from consumer-specific demand and authorization; preserve surviving independent justifications when another consumer is blocked.
- MUST NOT: Transfer authorization between consumers through cached construction outcomes.
- MUST: Represent internal graph nodes, records, and results with typed Python structures; return explanations as evidence and relationship structures; scope memoization to the evaluation and relevant occurrence and demand context while preserving enclosing native validation.
- MUST NOT: Use caches as independent business authority or interpret diagnostic strings to recover execution decisions.
- WHY: Optimization and presentation must not become alternate sources of execution meaning.

### D-016: Scope collection progress and finality (§6)

- MUST: Admit identified members, permit per-member work before closure, require explicit scoped closure for aggregate finality, absence, and uniqueness, and produce a finite tuple on closure.
- MUST: Reject later new members for that closed occurrence; represent corrections through a new declared occurrence.
- MUST NOT: Let a closer close a sibling collection or mutate a closed tuple.
- WHY: Incremental progress must preserve the declared boundary of a complete collection.

## History, admission, and permission

### D-017: Derive identities from declared execution and history (§8)

- MUST: Logical effect identity distinguish invocation, artifact, interaction, construction occurrence, subject scope, and repetition; retries retain effect identity and allocate a new attempt number; evidence identity comes from admitted history, preserving distinct equal-valued members.
- MUST NOT: Merge operations by equal payloads or derive business identity from process addresses, incidental hashes, or payload hashes.
- WHY: Logical work and physical attempts must remain distinguishable through replay and recovery.

### D-018: Establish provenance independently of admission (§§3–4, 8)

- MUST: Distinguish dispatch authorization, evidence of actual dispatch, and evidence of external completion; preserve independently established provenance when payload construction or admission fails.
- MUST NOT: Treat dispatch authorization alone as proof of actual dispatch or completion.
- MUST: Trusted adapters establish source identity and construct observations; direct provenance comes from actual host dispatch, and delayed provenance requires an established source and matching dispatched attempt for the stated effect.
- MUST: Record observations, provenance, admission, and conflicts independently; retain provenance when an attributed return supplies no admitted result.
- MUST NOT: Deserialize trusted observation envelopes wholesale from external input or establish authority from a valid payload, supplied identifiers, or arrival order alone.
- WHY: Invalid content cannot erase known execution, and valid content cannot invent it.

### D-019: Admit evidence through declared receiving contracts (§§6, 8)

- MUST: Apply the same admission rules to immediate and delayed observations, checking pinned artifact, established source, native construction, all correlations, required intent authority, receiving cardinality, and closure.
- WHY: Delivery timing does not change what constitutes usable business evidence.

### D-020: Deduplicate within the receiving namespace (§8)

- MUST: Identify delivery within its source and receiving namespace, comparing role, mode, relationship, and owned envelope contents under the delivery comparison contract; record same-identity different-content collisions as rejected delivery conflicts.
- MUST NOT: Replace admitted evidence with a colliding delivery.
- MUST NOT: Infer delivery occurrence identity solely from equal payload content or substitute a payload digest for occurrence identity because a transport identifier is absent.
- WHY: Transport repetition must not overwrite established evidence.

### D-021: Separate result cardinality from authoritative conflict (§8)

- MUST: Specify concrete delivery and result comparison contracts: delivery comparison judges retained envelope repetition for one delivery identity, and result comparison judges repetition or contradiction of otherwise admissible claims for one receiving occurrence.
- MUST: Justify comparison distinctions through the respective receiving responsibility; keep business normalization and conditions in declared types and relationships.
- MUST NOT: Use comparison to establish identity, ownership, provenance, or correlation meaning, impose general record or history equality, introduce distinctions solely because Python observes them, or narrow native construction and supported values for comparator convenience.
- MUST: Fill a single-result occurrence with its first valid correlated result; add no second value for an equivalent valid result; preserve the admitted result and later claim as an evidence conflict when a materially different result is otherwise admissible.
- MUST: Treat admitted result and definitive failure for the same attempt as incompatible, failure and success across different attempts as compatible, and uncertainty resolved by result or definitive failure as resolution.
- MUST NOT: Create authoritative evidence conflicts from invalid or unauthorized claims or choose a winner by arrival order.
- WHY: Retaining one result does not establish that later contradictory evidence can be ignored.

### D-022: Withhold precisely the work affected by conflict (§8)

- MUST: An unresolved evidence conflict withhold further attempts for its effect and undispatched work relying on the disputed occurrence through request, eligibility, or demand prerequisites, including committed intents; preserve independent work and independent justifications whose request and eligibility are unaffected.
- MUST: Retain previously dispatched work and its observations; expose later conflicts on completed invocations as visible faults.
- MUST NOT: Undo dispatched work, silently reopen completed invocations, or automatically select or clear an authoritative conflict.
- WHY: Disputed authority stops affected future execution without rewriting history or blocking unrelated progress.

### D-023: Preserve observation meanings (§§6, 8)

- MUST: A receipt mean acknowledgement without business completion; a result mean a reported business outcome including negative answers; failed mean established non-completion and established repeat safety; uncertain mean completion is not established either way.
- MUST: Treat timeouts, adapter exceptions, disconnects, local recording failures, and attributed answers without admitted results as uncertainty; permit an adapter's failed report only under the stronger capability guarantee.
- MUST NOT: Treat a negative business answer as execution failure or a receipt as a completed result.
- WHY: Recovery depends on what execution is established to have done.

### D-024: Derive permission centrally from independent facts (§8)

- MUST: Apply permission in this order: relevant conflict withholds; admitted logical result stops further attempts; no dispatched attempt permits the first; definitive failure of the latest attempt permits the next; uncertainty or an attributed answer without admitted result follows recovery policy; outstanding attempt or receipt alone waits.
- MUST: Derive attempt knowledge only from established observations and preserve equivalent permission across receipt and uncertainty arrival permutations.
- MUST NOT: Maintain competing execution-status authority or reuse an earlier attempt to authorize repeated retries after a new attempt starts.
- WHY: One derivation prevents contradictory or arrival-dependent execution permission.

### D-025: Recover under the capability contract (§§6, 8)

- MUST: `retry` rely on capability-guaranteed repeat safety or provider idempotency using stable effect identity; `reconcile` withhold automatic redispatch while uncertain until authoritative evidence resolves it.
- MUST: Let a late valid result satisfy the logical effect while a later attempt is in flight, stop further attempts, and retain and process the in-flight attempt's observations.
- MUST NOT: Infer a polling operation.
- WHY: Recovery must account for external completion without inventing repeat safety.

## Hosts, durability, and interfaces

### D-026: Dispatch only currently justified committed work (§§4, 6–8)

- MUST: The host evaluate, commit intent, record attempt before dispatch, execute through adapters, record observations and admission results, and advance revisions; recheck justification at its authoritative dispatch decision.
- MUST: Cancellation stop new work while retaining in-flight uncertainty and prior effects; caller disconnection remain distinct from cancellation.
- MUST NOT: Have the host independently select business branches or claim that a subsequently recorded conflict or cancellation prevented an already authorized external call.
- WHY: Host sequencing must preserve the evaluator's authority at the execution boundary.

### D-027: Preserve semantics across local and durable hosts (§7)

- MUST: Treat host-specific reductions in supported construction modes or programs as architectural contract changes.
- MUST NOT: Make supported Python-mode programs local-only as an incidental persistence choice.
- MUST: Local and durable hosts share declaration, construction, admission, and evaluation semantics; durable execution load pinned artifacts and revisions, commit intents and required receiving state against the expected revision, retain observations and admission, and resume without the original request or coroutine.
- MUST: Durable inboxes retain early deliveries until their receiving relationship resolves, and worker coordination reject stale commits and duplicate dispatch authorization.
- MUST NOT: Treat inbox retention as admission or introduce a second application workflow through persistence or scheduling.
- WHY: Durability changes execution mechanics without changing the business program.

### D-028: Preserve artifacts and construction fidelity (§§7–8)

- MUST: Specify the concrete continuation and restoration protocol, what it retains, how it preserves supported native input modes, and the fidelity argument establishing preservation of recorded meaning.
- MUST NOT: Treat determinism and artifact pinning alone as a complete restoration protocol or demonstration of fidelity.
- MUST: Each invocation retain access to its executable artifact and compatible dependencies; unavailable artifacts produce faults; restoration retain original boundary inputs and mode or use a versioned representation with demonstrated fidelity.
- MUST NOT: Recover under current code in place of a missing pinned artifact or accidentally normalize serialized output again.
- WHY: Recovery must preserve the meaning of work already in progress.

### D-029: Project interfaces without competing semantics (§§3, 8)

- MUST: Direct calls, CLI, APIs, and event ingress project the engine's declarations, observations, results, and host operations; derive schemas and explanations from declarations and preserve documented native input modes; distinguish commands, queries, and events by role rather than transport.
- MUST: Telemetry observe execution without controlling it and exclude payloads and credentials by default.
- WHY: Interfaces and observability must preserve the same application contract.

## Verification and decision governance

### D-030: Demonstrate guarantees through independent behavior (§10)

- MUST: Tests assert public behavior independently of evaluator helpers, pair prevention with valid progress, exercise interacting guarantees, measure shared construction on graph-shaped examples, and compare memoized with equivalent uncached evaluation.
- MUST: Tests establish the preconditions they claim to exercise: refusal-then-success cases demonstrate the candidate refusal, and post-construction environment changes occur after construction; critical safeguards demonstrate defect detection through targeted fault injection or mutation.
- MUST: Verify native construction agreement for defaults, aliases, null, factories, nested validation, and replacement values, plus refusal, mixed errors, successful unions, and escaping programmer exceptions; verify the runtime identity, authority, progress, conflict, recovery, ownership, and closure decisions above.
- MUST: Verify delivery repetition and collision behavior, result repetition and contradiction behavior, historical ownership against writable aliases, and restoration fidelity under the chosen protocol as separate contracts; these checks do not require universal record or history equality.
- MUST: Durable acceptance inject faults around intent commitment, dispatch, provider completion, recording, admission, and response delivery, including process loss and stale workers.
- MUST NOT: Claim durable guarantees from isolated native construction probes.
- WHY: Passing isolated examples cannot establish compositional or durable correctness.

### D-031: Keep implementation choices distinct from architectural changes (§§7, 9, 11)

- MUST: Reviewers distinguish a violated rule from a newly discovered design problem; architectural amendments require explicit human approval and consistent architecture and register updates; reconcile obsolete records rather than treating them as alternate authority.
- MUST NOT: Present storage, scheduler, topology, durable codec, artifact packaging, or worker coordination choices as already decided by the architecture when they remain open, or introduce migration into the initial design.
- WHY: Open implementation work cannot silently change approved guarantees.
