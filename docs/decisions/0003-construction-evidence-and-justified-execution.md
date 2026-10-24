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

## Rejected rule and evidence

In `343b13b`, every open construction becomes "undecided", and conjunction dispatches work under every undecided child. This is rejected as a causal rule. A plain fact around `Pinged` causes inspection and ping to dispatch together before permission exists; the identical probe passed on `9447f67`. A minimum-length constraint directly on a goal field also permits premature ping. An evaluation probe changes accepted nested list evidence during construction.

These executed counterexamples establish failures, not a replacement algorithm. Passing the 16 earlier reviewer cases and 103 repository tests did not establish compositional correctness. Describing the remaining issue as only a waiting cost is false.

## Still to establish in outcome 1

Resolve the four §18 questions with executable declarations: interaction unification without losing distinctions; adequate pure results and reasons; logical effect identity including repetition; closed collection admission. Establish the native construction boundary, truthful provenance and causal relationships needed to exercise those questions. Contract experiments may contain enough evaluator machinery to test them; no broad runtime build or housekeeping inventory is a substitute.

This record does not select a new guard API, durable codec, storage backend, migration scheme or complete proof engine. Those choices require evidence within these constraints. An inability of the current representation to satisfy them is grounds to replace the representation, not weaken the architecture.
