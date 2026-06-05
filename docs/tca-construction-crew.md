# The TCA Construction Crew

A developer's operating manual for the agent system that builds Type Construction
Architecture code. This is the single document that describes the running system: its
components, how they compose into a build, how to run it, how to extend it, and how to
carry it to another project. It is not aspirational; everything here exists in the repo
and has been run end to end.

The doctrine it builds toward is `type-construction-architecture.md` (the authority),
with `build-patterns.md` (how each construct is built) and `program-topology.md` (where
each file lives). The crew grounds in those documents as its single source of meaning and
never restates them.

---

## The thesis

A language model fails at TCA by default. Its training is overwhelmingly procedural, so
it will describe the architecture correctly and then generate the opposite on the next
token. Instruction does not fix this, because the instruction is one paragraph against a
gradient trained on billions of procedural tokens. The crew overcomes drift structurally,
not by instruction, on two channels:

- The **structural channel** decides what is admissible. A deterministic gate audits every
  write and denies a non-conforming one before it lands. The mechanical breaks are not
  discouraged, they are unconstructable.
- The **semantic channel** sets salience. The agent prompts describe the world as settled
  dispositions (the catalog is closed, a value exists only by construction, the gate is the
  floor) so the behavior follows from the description rather than from policed imperatives.
  A reviewer then covers the semantic residue a parser cannot decide.

The principle the crew enforces, it also obeys: meaning lives in structure, the gate is the
structure, and the prompts state facts rather than legislate behavior.

---

## Components

| Component | File | Role |
|:---|:---|:---|
| Doctrine | `docs/*.md` | the single source of meaning the crew grounds in |
| Deterministic gate | `.claude/scripts/tca_gate.py` | structural channel: AST audit, denies mechanical breaks |
| Reviewer instruction | `.claude/scripts/tca-purity-review.md` | the coverage-review brain, one source for both review surfaces |
| Review hook | `.claude/scripts/tca_review_hook.py` | semantic channel: sonnet coverage review after a write |
| Architect | `.claude/agents/tca-architect.md` | graphs an obligation top-down; writes nothing |
| Forge specialists | `.claude/agents/forge-*.md` | build one construct layer each, bottom-up, under the gate |
| Reviewer agent | `.claude/agents/tca-review.md` | adversarial-free coverage review; opus by default |
| Workflow | `.claude/workflows/tca-build.js` | orchestrates architect to forge to review |
| Hook wiring | `.claude/settings.json` | binds the gate (PreToolUse) and review (PostToolUse) |

### The deterministic gate (`tca_gate.py`)

The structural floor. It parses the proposed source with `ast` and reports the mechanical
breaks with certainty and zero model latency:

- a bare primitive field on a frozen model (a domain value with no scalar)
- a `match` over a union (re-dispatch of what construction already selected)
- `arbitrary_types_allowed` off the active model
- a standalone enum used as a field type (a uniform vocabulary belongs in a `StrEnum`
  wrapped as a `RootModel` scalar; a `StrEnum` as a scalar's value space is allowed and is
  not flagged)

Findings are typed (`Violation` carries the rule and the line) and the verdict is a union
(`Conforming | Rejected`), so the gate is built the way it enforces. It does not check
prose conventions; em-dash style and the like belong to writing, not to a code gate.

Two modes:

- **Hook mode** (no arguments, reads a `PreToolUse` event on stdin): emits
  `permissionDecision: "deny"` with the violations as the reason, so a non-conforming `.py`
  write is blocked before it lands.
- **Check mode** (`--check FILE...`): audits files directly and exits non-zero on any
  violation. This is what the forge agents and the review node run to verify on the
  substrate.

Scope: it gates `.py` files whose path contains `TCA_GATE_PATH_SUBSTR` (default `/tca/`),
excluding `.claude/` (its own tooling), tests, and any path you exclude. Set the env var to
point it at another project's package.

The judgment a parser cannot make (is a name vacuous, is a union actually disjoint, has a
vocabulary fused several axes) is left to the reviewer; the gate decides only what structure
settles.

### The reviewer (`tca-purity-review.md`, `tca_review_hook.py`, `tca-review`)

The semantic channel, framed for **coverage**: report every deviation, including uncertain
ones, each tagged with which of the four breaks it is (escaped, duplicated, vacuous, fused)
and a confidence, and let a later stage filter. This is deliberate: an adversarial
"find everything, when in doubt flag it" stance suppresses recall on the current models,
which follow it as a filter; a coverage stance with per-finding confidence recovers it.

The same reviewer instruction (`tca-purity-review.md`) drives two surfaces:

- **The review hook** (`tca_review_hook.py`, `PostToolUse`): runs the instruction on
  **sonnet** against each written file and surfaces findings as context. It does not block,
  because the deterministic gate already held the floor; it adds the semantic read on top.
- **The `tca-review` agent**: the same coverage review invoked directly for a deep audit,
  on **opus** by default. It verifies claims on the substrate (constructing minimal payloads
  to test disjointness, running the gate to anchor itself) rather than asserting them.

### The agents

All agents ground in the docs as single source and are written as dispositions, not
imperatives. They are bounded, single-responsibility roles, so they carry no heavy persona.

- **`tca-architect`** (sonnet, read-only): takes an obligation, names the construct whose
  existence is that certainty, composes downward to the leaf scalars, and returns a
  dependency-ordered construction graph whose nodes are catalog constructs, partitioned by
  the forge specialist that builds each layer. It writes nothing. When a forge agent returns
  a gap, the architect replans, locating the construct that already carries the missing
  meaning or specifying a new one to gate through construction-as-proof.
- **The six forge specialists** (sonnet, read/write/bash), one construct layer each:
  `forge-domain` (the frozen typed core: scalars, collections, frozen models, unions,
  derivations, boundary models), `forge-active` (the single active model), `forge-config`,
  `forge-route`, `forge-service`, `forge-main`. Each builds its partition bottom-up, verifies
  a dependency before composing it (composing it vouches for it), verifies its own files on
  the substrate, and emits a **gap** rather than improvising procedure when a node needs a
  meaning no construct carries.
- **`tca-review`** (opus by default, sonnet in the hook): the coverage reviewer above.

### The workflow (`tca-build.js`)

The orchestration, as a construction graph of activity. It runs the architect, groups the
returned nodes by their forge specialist, builds each partition in layer order (a forge gap
routes back to the architect to replan, bounded to two rounds), then runs the coverage
review. The architect's output is forced to a schema whose `kind` is the **closed catalog**
(so the planner cannot name a construct outside it) and whose `agent` is the forge
specialist; the forge output is forced to a `built | gap` union (so termination is a landed
variant, never free text). The dependency edges in the graph are the build order; nothing
authors a sequence.

The build target is the `obligation`. Set it in the `DEFAULT_OBLIGATION` constant at the top
of the script (the script also reads `args.obligation` when one threads through). Invoke the
workflow by name (`tca-build`) or by script path.

### The hooks (`settings.json`)

```json
"hooks": {
  "PreToolUse":  [ { "matcher": "Write|Edit|MultiEdit", "hooks": [ { "type": "command", "command": "... tca_gate.py" } ] } ],
  "PostToolUse": [ { "matcher": "Write|Edit|MultiEdit", "hooks": [ { "type": "command", "command": "... tca_review_hook.py" } ] } ]
}
```

The gate runs first and can deny; the review runs after a successful write and surfaces
findings.

---

## The build loop, end to end

1. **Obligation.** What must be certain, in domain language.
2. **Architect** graphs it top-down into a dependency-ordered set of catalog constructs,
   partitioned by forge specialist. Writes nothing.
3. **Forge** builds bottom-up: each node composes only nodes already built and proven
   beneath it. A node that needs a meaning no construct carries returns a **gap**.
4. **The gate** denies any non-conforming write before it lands, on every write, so the
   mechanical breaks are unconstructable.
5. **The review** covers the semantic residue: vacuous names, a vocabulary that should be a
   scalar or has fused axes, disjointness (verified by construction), obligation discharge.
6. **A gap** routes back to the architect, who replans and reissues the partition.

Top node existing is the proof the obligation holds. The two directions, design top-down and
build bottom-up, are the division of labor between the architect and the forge specialists.

---

## Model bindings

- Architect and forge specialists: **sonnet**, medium effort. They do bounded construction
  under the gate; sonnet is sufficient and the gate is the guarantee.
- `tca-review`: **opus** by default in the file (the deep, direct audit). The review **hook**
  runs the same instruction on **sonnet**, cheap enough to fire on every write. One reviewer,
  two bindings, chosen by who invokes it.

---

## Running a build

1. Set the obligation in `DEFAULT_OBLIGATION` at the top of `.claude/workflows/tca-build.js`.
2. Run the `tca-build` workflow. The architect graphs, the forge specialists build under the
   gate, the reviewer covers.
3. Verify the output yourself on the substrate: `uv run python .claude/scripts/tca_gate.py
   --check <files>`, `uv run basedpyright <dir>`, and construct the built types to confirm
   illegal values are unrepresentable and derivations resolve.

The forge agents write the `.py` files; you do not. A non-conforming write is denied by the
gate, so the only code that lands is conforming code.

---

## The worked example

`tca/payment/` is a domain the crew built from an obligation, kept as the canonical example.
It exercises the doctrine that the simpler cases do not: a disjoint `PaymentMethod` union
(`Card | BankAccount | Wallet`) selected by structure with no tag, a `Currency` semantic
scalar over a `StrEnum` value space, and a variant-carried `settlement_days` derivation. It
passes the gate with zero violations and basedpyright clean; on the substrate the union lands
the correct variant by structure, the `StrEnum` scalar proves membership, and the derivations
resolve. It was built without a human editing the `.py`.

---

## Why it is built this way

- **Dispositions, not imperatives.** Forceful prohibitions ("never write procedure") raise
  the salience of the thing they forbid and get re-litigated; settled facts get assumed. The
  prompts describe the world and lean on the gate, which is the structural enforcer.
- **The structural channel sets admissibility; the semantic channel sets salience.** The gate
  decides what can exist; the prompt and the names decide what is likely. A construct is wrong
  when it uses one channel to paper over the other.
- **Coverage, not adversarial stance, for review.** Recall comes from reporting everything
  with a confidence and filtering separately, not from a "find everything" instruction the
  model follows as a filter.
- **The four breaks.** Every forbidden pattern is one of: a meaning with no structure
  (escaped), a meaning with more than one structure (duplicated), a structure with no meaning
  (vacuous), a structure with more than one meaning (fused). The gate decides the structural
  instances; the reviewer judges the rest.

---

## Extending the system

The catalog is closed, and that is load-bearing: a forge agent can only build a catalog
construct, and the architect can only plan one (the workflow schema's `kind` is the catalog).
A new construct enters only by surviving construction-as-proof, the same bar any TCA value
meets. When a build needs a meaning no construct carries, the forge agent returns a gap and
the architect replans; that gap is the signal that a construct has not been located, not a
license for procedure.

To change what the gate decides, edit `tca_gate.py`: the break checks are small AST passes,
the findings are typed, and the gate audits itself out of scope (it lives under `.claude/`).
Keep the gate to what structure settles; push judgment to the reviewer instruction. The
over-constraint dial (a check too tight rejects a legal construct, too loose readmits drek)
is found by running real builds, not chosen in advance.

---

## Caveats

- **The obligation is set in the script.** Argument threading into a script-path-invoked
  workflow is unreliable, so set `DEFAULT_OBLIGATION` directly rather than relying on `args`.
- **The gate is a deterministic floor, not the whole conformance.** It decides the mechanical
  breaks; disjointness, vacuous names, and obligation discharge are the reviewer's, verified
  by construction.
- **The review hook calls the model on every write.** That is the semantic tier and it adds
  latency; the deterministic gate is the fast blocker, the review is the slower coverage read.
- **The coverage framing is calibrated to the current models.** If you bind the reviewer to a
  different model, confirm recall on a known-impure fixture.

---

## Porting to another project

The crew is self-contained. To carry it to another project, copy these components:

```text
docs/
  type-construction-architecture.md   # the authority (required)
  build-patterns.md                   # how each construct is built (required)
  program-topology.md                 # where each file lives (required)
  proofs-and-graph.md                 # design and audit lenses (required)
  semantic-index-types.md             # names as instruction
  executable-ontology.md              # why
  agentic-constructs.md               # the forward proposition
  tca-construction-crew.md            # this manual
.claude/
  agents/        # tca-architect, forge-domain/active/config/route/service/main, tca-review
                 # (prompt-engineer is optional, for cultivating the prompts)
  scripts/       # tca_gate.py, tca_review_hook.py, tca-purity-review.md
  workflows/     # tca-build.js
  settings.json  # the PreToolUse gate hook and PostToolUse review hook
CLAUDE.md        # the build scaffold; replace the one project-specific block
```

Then:

1. **Dependencies.** `uv add pydantic` (the doctrine and the gate use Pydantic v2). Python
   3.12+. The review hook shells out to the `claude` CLI, so it must be on PATH for the
   semantic tier; the deterministic gate needs only Python and Pydantic.
2. **Scope the gate.** `export TCA_GATE_PATH_SUBSTR=/your_package/` so the gate audits the
   target's source tree and excludes its tooling.
3. **Merge the hooks.** Add the `PreToolUse` and `PostToolUse` blocks from `settings.json`
   into the target's `.claude/settings.json`.
4. **Adapt CLAUDE.md.** Replace the single project-specific block; the rest is portable.
5. **Reload the session** so the hooks activate. Any impure `.py` write under the scope is now
   denied, and the crew builds under the gate.

The doctrine docs are the single source the agents read; the gate is the structural floor;
the workflow is the build run. Nothing else is required.
