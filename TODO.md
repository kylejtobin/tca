# TODO

Not built, in order. The design for each is in `docs/decisions/`; the developer's side is `.agents/skills/tca-python-dev/SKILL.md`.

## Now
### Task 1: Establish the declaration-driven construction model - Done

### Task 2: Make computational results authoritative through native construction - Done

### Task 3: Runtime Construction and Execution Integrity - Done

### Task 4: Route-Local Proof and Construction Soundness - Done

### Task 5: Demand-Directed, Evidence-Eligible Effects - Delivered for review

**Derive what is performed from the route's own construction, and what it is performed with from the action's declared fields.** Do not introduce a separate policy model, a second dependency graph, or a developer-facing authorization API.

- Each pass evaluates the route's own occurrence and nothing else: an occurrence's decisions, the premises some alternative of which is conditional, are evaluated first, and while any is undecided nothing else of it is; what the evaluation reaches with every reference resolved is asked for on the spot, so what the answer needs is constructed as it is evaluated and a dormant branch never is. The frontier is the actions whose premises are all filled: the effects that produce deciding evidence while a decision is pending, and everything an established outcome needs once none is. A choice among effects nothing decides is never guessed.
- An action's eligibility is its fields: each action of the frontier is constructed from the exact occurrences bound there, of its own class and holding the very instances supplied, every one before any is performed; that construction is the only way to the effect boundary.
- The same evaluation explains a run that ends: the causes it found, a choice among effects it would not guess, or occurrences waiting on one another. Each occurrence is evaluated once per pass however many fields reach it.
- Preserve Pydantic validation, structured concurrency, at-most-once dispatch and atomic pass-level evidence admission.

**Outcome:** An effect executes only when the requested answer needs its result and the correct occurrence's own evidence supplies it. Records 0054, 0055 and 0056, the developer skill's account of `undecided`, and the feature files are reconciled in Task 7.

### Task 6: Declarative CLI Projection - Not Done

**Project the CLI directly from Pydantic declarations.** No independent CLI schema, validation language, or construction semantics.

- Support scalar, vocabulary, nested value, union, collection, optional, and defaulted inputs.
- Preserve native Pydantic admission, aliases, errors, and Python/JSON equivalence.
- Keep computed values non-writable and infrastructure configuration separate from business inputs.
- Render structured replies and diagnostics without reinterpreting their meaning.

**Outcome:** The CLI faithfully exposes the declared program without introducing another model of it.

### Task 7: End-to-End Verification and Engine Simplification - Not Done

**Prove that declarations, symbolic proof, runtime construction, effect authorization, and external interfaces implement one coherent program.**

- Compare proof conclusions against actual construction using exhaustive bounded cases and adversarial generated programs.
- Verify repeated occurrences, alternatives, conditional evidence, collections, unknown semantics, effects, cancellation, resources, provenance, and telemetry.
- Substitute concrete capability implementations without changing proof, construction, or authorization.
- Remove superseded abstractions, duplicate interpretations, compatibility machinery, and dead code. Reconcile documentation with the verified design.

**Outcome:** A production-ready, irreducible type-construction engine whose correctness follows from one authoritative declarative model.

## Next

1. Bind the feature files with pytest-bdd, so every scenario in `packages/python/*/tests/features/*.feature` and `tests/features/smell_check.feature` runs as a test. Step definitions live in each package's `tests/`, one module per feature file, with a parametrized step for each sentence shape that repeats, such as "ValidationError is raised with type {type} at loc {loc}". Add `pytest-bdd` to the dev group. Order of work: `scalar.feature` and `kinds.feature`, which need only the world; the other world features and `smell_check.feature`; then `engine.feature`; then `cli.feature`.

## Later

1. The HTTP kind (0015, 0016, 0023, 0045): `Http`, `Keyed`, `Post`, `Get` with `perform(self)` sending through the `httpx.AsyncClient` held in `self.party`'s `PrivateAttr` and returning `hear(self, response.text)`; one FastAPI path operation per route with `Q` as the body and `answered.reply` as the response, served inside `opened`; the standard OpenTelemetry instrumentations for httpx and FastAPI. Its scenarios in the http package's `tests/features/`, with httpx's `MockTransport` as the party.

