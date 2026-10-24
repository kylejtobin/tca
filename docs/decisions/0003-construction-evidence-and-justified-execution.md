# 0003. Construction evidence and justified execution

**Status:** binding architectural constraints, issued by the designated independent Codex reviewer at Kyle's direction, 2026-10-23. These constraints do not assert implementation completion. They govern TODO outcomes 1–7, especially the contract and evaluator in outcomes 1–2.

**Authority:** foundations §§4–10, §16 and §18; acceptance requirements A–F and N. This record supersedes the demand rule and its claimed justification in 0002. Its experiments remain historical evidence, not authority to relax these constraints. Record ownership and acceptance are governed by [0004](0004-review-authority-and-outcome-evidence.md).

## Decision

**Business types are the program.** Pydantic owns native value construction, composition, constraints, validation and serialization. TCA interprets the additional source, occurrence, demand and effect relationships. Applications must not need an independently authored workflow, engine branches for particular business scenarios, or artificial subclasses merely to compensate for lost occurrence information.

**Construction and proof have different jobs.** Concrete construction runs through Pydantic with an explicit input mode and context. Internally assembled field dictionaries use field-name semantics, without aliases reinterpreting their bindings; external admission retains its declared alias and mode policy. Defaults and zero-required-field models have the same failure-classification obligations as other constructions. Business refutation, malformed construction and execution failure remain distinct.

Static conclusions must be established, contradicted or unproven for the particular boundary, premises and configuration. Supported native constraints and trusted primitive summaries may be analyzed; arbitrary callbacks must not be stripped away or assumed transparent. The absence of a recognized validator establishes nothing. Core-schema inspection may support bounded inference, but does not authorize a second validation implementation. No particular analyzer implementation is mandated here.

**Uncertainty never grants execution authority.** The graph must distinguish available evidence, construction uncertainty, consumer-specific demand, an action's own eligibility, and the decisions controlling that demand. An effect dispatches only with established eligibility and justified demand. A single surviving branch is not an established branch. Evidence-gathering operations require their own justification; neither their names nor uncertain downstream constructions grant it. Independent necessary work with established prerequisites must remain concurrent.

A plain wrapper or opaque identity validator must not release a previously withheld effect. Field-site constraints retain their obligations at the field where they are declared, not only when developers introduce an extra fact around them. Unknown whole-model semantics must not be executed as invented partial field validation. A validator requiring an effect's result cannot be treated as that effect's prior authorization.

Where an action universally requires permission, a typed premise can express that eligibility. Consumer-specific conditions must not silently become universal action prerequisites. If the declarations do not establish the necessary causal relationship, identify the missing relationship precisely and test the smallest declarative extension; do not invent ordering, reject all opaque validation, or serialize all work. The syntax and derivation of such relationships remain a contract question, not a settled decision.

**Occurrences and provenance survive construction.** A class, equal value or shared Python object is not a business occurrence. Bindings must be unambiguous; declaration order must not resolve contradictions. Source identity, correlation, membership and closure retain their exact subject and occurrence scope, including repeated and nested compositions.

A construction witness identifies the versioned construction and its supplied evidence occurrences, together with the actual result. It does not claim that each output field is an unchanged input occurrence unless that relationship is established. Transforming validators remain native behavior. Evaluation must not mutate admitted evidence. The value-ownership and pure-callback contract must be explicit and exercised; frozen models alone do not establish it. Environmental observations needed for replay are recorded evidence, not unrecorded validator or factory effects.

**Execution belongs to the invocation.** Pure evaluation derives work; the host executes and records it without interpreting business branches. Immediate responses and delayed deliveries both pass admission. Logical effects remain distinct from attempts; equal payloads must not collapse distinct intended occurrences. Closed collections require declared closure before finality or absence is inferred. Local and durable hosts interpret the same business program. No API request, coroutine or transport owns the program's lifetime.

## Laws every implementation must preserve

These laws constrain behavior across the refactor; they do not prescribe class names, storage layout or an algorithm. They apply as each outcome introduces the corresponding machinery. A changed representation must preserve them, and a new abstraction must explain which declared distinction it represents.

1. **Every effect has a justification.** For each proposed effect occurrence, the evaluator must be able to identify its demanding consumer or branch, validated eligibility premises, and established controlling decisions. Availability, eventual usefulness, a successful hypothetical outcome, or a source's name is not a substitute. This justification is derived from the business declarations, not supplied by a second workflow.

2. **Less knowledge cannot create more authority.** Replacing established semantic knowledge with an opaque or unsupported construction cannot, by itself, release an effect. A missing proof stays missing. Equally, more evidence is not automatically more permission: closure, cancellation and version-specific authority must be interpreted under their declared rules. Do not collapse "unknown", "rejected", "waiting" and "authorized" into one flag.

3. **Business meaning survives composition.** A semantics-preserving wrapper, extraction, shared dependency or equivalent validator formulation must not weaken the conditions for an effect, change its subject, or merge distinct occurrences. Explain any genuine semantic change rather than treating model shape as a scheduling instruction. This law does not erase native Pydantic field-order, validator-context or transformation semantics. Opaque behavior may reduce provable knowledge; it must not grant authority.

4. **Constraints and authority stay at their declared scope.** A receiving field's constraint belongs to that construction site; a default belongs to its construction path; a consumer's condition belongs to that demand; an action's eligibility belongs to the action; closure belongs to its declared source and occurrence. None may silently become a class-wide assumption, invocation-wide event, or unrelated sibling's permission. Adding a consumer cannot weaken action eligibility.

5. **Semantic distinctions survive every boundary.** If correctness depends on source, occurrence, version, logical repetition, validation mode, receipt/result role or closure, compilation, admission, evaluation and recovery must retain or soundly derive that distinction. A representation that cannot carry it must change. Dropping information and later guessing it from class, shape, equality, field order or timing is not an implementation strategy.

6. **Safety and useful progress are both obligations.** Refusing every program, withholding every effect, serializing independent work, or requiring invented business types does not implement the contract. A repair must preserve the corresponding valid case and justified concurrency as well as block the invalid case. Missing declarative information receives a precise diagnostic; supported valid programs must not be narrowed merely to simplify the engine.

7. **Optimization and infrastructure preserve meaning.** A cache, index, compiled summary, snapshot, transport or host cannot become a second business authority. Compare behavior with and without an optimization and across hosts under the same declared guarantees. Replay of the same version and recorded history preserves business results, logical identities and justified work; no such claim applies to arbitrarily reordered causal histories or unrecorded observations.

These laws make the design falsifiable. A counterexample is a reason to repair or replace the representation, or to bring an explicit contract conflict to the reviewer. It is not permission to redefine a business requirement around the implementation.

## Required reasoning: no shortcuts from uncertainty to policy

Added by reviewer after rejecting `8aed218`. These requirements constrain how architectural conclusions are derived, not just the current evaluator. They supplement the preservation laws; no one law may be used to nullify another.

**An unestablished relationship is not established independence.** "The analyzer cannot see a dependency" does not imply "the business declared no dependency." Distinguish an established dependency, established independence under the declared program, and an unresolved relationship. Only the first two support the corresponding ordering or concurrency conclusion. A diagnostic that names the unknown does not discharge it. An effect may proceed beside unrelated uncertainty only when its own eligibility and demand are justified without assuming that uncertainty resolves favorably.

**The burden of proof belongs to the proposed behavior.** Dispatch requires an affirmative derivation from the declarations and current evidence; the absence of a recognized blocker is insufficient. Rejection requires a sound contradiction or a precise unsupported obligation; the absence of a success proof is insufficient. "Do not invent ordering" prohibits guessing an order, not checking the justification for unordered execution. "Do not serialize everything" requires useful independent progress, not speculative execution. No prohibition supplies the missing premise of a positive conclusion.

**A semantic relationship cannot be replaced by a taxonomy.** Metadata categories, validator syntax, numerical ranks, class ancestry, field order or implementation convenience cannot establish causal precedence. Such representations are permissible only as encodings of relationships already justified from the program. The same business condition does not become pre-effect authority merely because one representation is analyzable, or cease to matter because another is opaque. Visibility changes knowledge, not business meaning.

**Using the authoritative library is not enough; preserve its authoritative operation.** Calling Pydantic on a stripped or reconstructed fragment does not prove equivalence to the original construction. A partial judgement must establish that omitted normalization, callbacks, defaults, context, configuration and ordering cannot change that particular conclusion. If that independence is unproven, retain the native boundary and the unknown. This applies equally to other delegated semantics: invoking the right library on a different question is still a competing interpretation.

**Preserve the problem while solving it.** A repair must retain the declared business relationships and supported input domain. Adding universal action prerequisites, inventing new business subclasses, changing inputs, or excluding a valid validator form may make a demonstration easier while changing the business program. Such a change is an explicit semantic proposal requiring reviewer adjudication, not a correctness fix. In particular, universal eligibility cannot stand in for consumer-specific demand. Paired examples with different contracts do not establish that the original contract works.

**Reject the false dilemma.** The choices are not "read arbitrary Python perfectly" or "ignore its relevance", nor "dispatch everything" or "reject/serialize everything". Separate the propositions being proved, preserve unknowns at their actual boundaries, and derive the work justified by the information that is available. If the current representation can express only unsafe alternatives, replace that representation. Adding a new label to the same unsupported inference does not repair it.

**Reason from counterexamples before generalizing.** A proposed rule must explain the supplied failing case, its valid progress counterpart and equivalent business formulations before it governs the engine. Cases that contradict the proposal remain evidence against it. Choosing which examples count according to what the implementation already supports is circular. An experiment may falsify a rule; it cannot redefine the requirement it was meant to test.

These requirements do not require a new report or approval for routine implementation choices. The reasoning must be visible in the model, the derivation of work, and independently specified tests. Implementers should resolve engineering questions through those experiments. A genuine missing business distinction or conflict between requirements must be made precise; neither silently guessing nor handing the reviewer an unexplored question satisfies that work.

## Rejected rule and evidence

In `343b13b`, every open construction becomes "undecided", and conjunction dispatches work under every undecided child. This is rejected as a causal rule. A plain fact around `Pinged` causes inspection and ping to dispatch together before permission exists; the identical probe passed on `9447f67`. A minimum-length constraint directly on a goal field also permits premature ping. An evaluation probe changes accepted nested list evidence during construction.

These executed counterexamples establish failures, not a replacement algorithm. Passing the 16 earlier reviewer cases and 103 repository tests did not establish compositional correctness. Describing the remaining issue as only a waiting cost is false.

## Reviewer finding on 8aed218

Decision records were not edited by the implementer, but their meaning was changed in code, README text and tests. The earlier model-validator and Annotated-validator regressions were renamed and their expected initial frontier changed from capture-only to capture-plus-shipment. The Annotated case also lost the assertion that no shipment intent existed after refusal. Adding a different request that universally requires eligibility changes the contract; it does not repair those regressions.

Independent execution still reproduces premature effects for opaque conditions. A further differential case is accepted by native Pydantic because a before-validator pads a tuple before its minimum-length check; the interpreter strips that validator and rejects the original one-element tuple. This falsifies the claim that its partial Pydantic call makes the same judgement. The 110 passing repository tests do not resolve those failures.

The categorical policy "opaque validators order nothing", the ranking of validator categories as causal authority, and the claim of equivalent partial validation are rejected. This does not establish that every opaque validator controls every sibling effect. The required answer is an evidenced causal relationship and faithful native construction, under the reasoning requirements above.

## Still to establish in outcome 1

Resolve the four §18 questions with executable declarations: interaction unification without losing distinctions; adequate pure results and reasons; logical effect identity including repetition; closed collection admission. Establish the native construction boundary, truthful provenance and causal relationships needed to exercise those questions. Contract experiments may contain enough evaluator machinery to test them; no broad runtime build or housekeeping inventory is a substitute.

This record does not select a new guard API, durable codec, storage backend, migration scheme or complete proof engine. Those choices require evidence within these constraints. An inability of the current representation to satisfy them is grounds to replace the representation, not weaken the architecture.
