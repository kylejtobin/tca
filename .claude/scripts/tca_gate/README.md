# tca_gate

Deterministic enforcement of ontology-first construction for Type Construction Architecture.

The gate is procedural code policing a declarative doctrine, and the inversion is deliberate. A language model generates by continuation over a corpus that is overwhelmingly procedural, so type-driven invariants stated as instructions compete with that prior on every token; stated as write-time constraints, they do not compete at all. The gate holds the line while constraint migrates into the grammar of what the agents can express. It becomes removable only when construct cards and row grammar constrain generation enough that this AST guard is redundant.

That makes the gate the procedural exception, not exemplary TCA domain code. Its comments and docstrings are load-bearing because an imperative AST shell cannot make its doctrine mapping evident through type structure. Do not copy this package's dense procedures, class-keyword shortcuts, or comment load into domain code; domain source follows the construct cards, where structure carries meaning.

## What it proves

The gate consumes an app environment's ontology catalog and, when present, its violation ledger. The discovery convention is `spec/ontology.json` in the target root (`<target>/spec/ontology.json`) in the edited file's ancestry, with `spec/violation.json` beside it. Row `file` paths are package-relative and resolve under the sibling `<target>/app` package, so the catalog and the topology never carry an `app/` prefix (`domain/<ctx>/type.py`, `main.py`).

The ontology catalog is a list of rows. Each row names one program meaning, assigns it one construct from the closed whitelist, names its file, and records its references to other rows. The gate proves two things:

1. **The catalog is coherent.** Every reference resolves to a row, every union variant pins its axis, there is exactly one consistency model per context, the files obey the topology, and a build order exists (a topological sort of the references). An incoherent design cannot validate, so it cannot be built on.
2. **Each source file conforms to its row.** A class in a file the ontology claims must match its row exactly: name, construct shape, frozen-ness, the exact field set, the exact field types, the kind pin. Code the ontology did not model cannot be written into a file it claims.

The row grammar itself is owned by the construct cards (`.claude/skills/tca-construct-*`) and `docs/construct.md`; the gate is their executable enforcement, not their source of truth. Deterministic means same input, same verdict, no model judgment. It does not mean the gate encodes the whole doctrine. When the doctrine changes, the cards change first and the gate follows.

## What it does not prove

- It does not prove product intent is correct.
- It does not decide whether the ontology chose the right construct.
- It does not prove runtime behavior, domain correctness, or test coverage.
- It does not run `basedpyright`; type checking is a companion verification step in the build loop.
- It does not govern unclaimed legacy files.
- Its hook does not run inside subagent writes.
- Passing `--check` does not replace human review.

## Architecture

Three modules, split so each consumer loads only what it needs:

- **`model.py`** — the declarative layer: the row grammar (one Pydantic model per construct), cross-row coherence, the topology rules, the build-order sort, and the violation ledger. No AST. This is the executable form of the catalog schema.
- **`audit.py`** — the conformance shell: the AST reader and every per-file check. The irreducibly procedural part. Split into `legacy_audit` (structural smells, catalog-independent) and `table_audit` (conformance against the catalog).
- **`cli.py`** — transport: the hook event on stdin, source reconstruction, catalog discovery, the modes, and the deny output. The only file that touches stdin, argv, and deny.
- **`__main__.py`** bootstraps `sys.path` so the package runs from any working directory; **`__init__.py`** is the package overview.

`--order` loads `model` only and never imports `audit`, so proving the catalog never pays for the conformance engine. That maps to the consumers: `tca-ontology` only needs to prove its catalog; `tca-dev` needs the full conformance audit.

## Evidence Contract

- **`--order ONTOLOGY`** validates catalog construction and prints ordered row expansion. Failure signal: nonzero exit with the construction/coherence error.
- **`--check FILE...`** audits catalogs, ledgers, and Python files. Failure signal: `path:line: rule` output and nonzero exit.
- **`--smell FILE...`** runs catalog-free structural smell detection for planning legacy migration. Failure signal: `path:line: rule` output and nonzero exit.
- **Hook mode** consumes a `PreToolUse` event from stdin and emits denial JSON only when a governed write violates the catalog. Out-of-scope or conforming writes produce no output.

Example `--order` output:

```text
1. semantic scalar Price -> domain/position/type.py
2. concept model Fill -> domain/position/fill.py
3. consistency model PositionBook -> domain/position/book.py
```

Example `--check` output:

```text
domain/position/fill.py:12: Fill: field `price` must be Price, as modeled
tca gate: 1 violation(s) across 1 file(s)
```

Example hook denial shape:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "TCA gate denied this write.\n- ..."
  }
}
```

## Modes

```
uv run python .claude/scripts/tca_gate --order PATH/ontology.json   # prove catalog + print build order
uv run python .claude/scripts/tca_gate --check FILE...              # full audit of files (smells + conformance)
uv run python .claude/scripts/tca_gate --smell FILE...              # structural smell scan, no catalog needed
<PreToolUse event on stdin>                                         # the hook: deny a non-conforming write
```

- **`--order ONTOLOGY`** validates the catalog and prints the build order as a numbered topological sort (`N. construct Name -> file`). The builder follows the printed order; it never chooses. Loads `model` only.
- **`--check FILE...`** audits each path standalone and prints `path:line: rule` for every violation. A `.py` file gets both the smell pass and the conformance pass (the latter needs an up-tree catalog). An `ontology.json` or `violation.json` path is validated as a catalog or ledger. Exit 1 if any violation, else 0.
- **`--smell FILE...`** runs `legacy_audit` alone: the structural smells (bare primitives, `T | None`, mutable containers, standalone enums, raw-string Literals, stray `arbitrary_types_allowed`), with no catalog required. For planning a refactor over un-modeled or legacy code. It does not run the conformance checks, which need a catalog to compare against.
- **The hook** reads a `PreToolUse` event on stdin, reconstructs the resulting source (from `content`, `old_string`/`new_string`, or the `edits` list), and denies the write if it does not conform. Deny is emitted as `permissionDecision: deny` JSON on stdout; an out-of-scope or conforming write produces nothing.

## Targeting

A write is governed only where the ontology already claims the file: a built row in the discovered up-tree ontology catalog names it. Framework files (`/.claude/`) and `/tests/` are never governed, and a tree with no ontology, or a file no row claims, is left alone. So the gate drops into an existing program safely: it governs exactly what is modeled and never blanket-condemns legacy code.

The current hook discovery path is intentionally narrow: it walks upward from the edited file and accepts exactly one `spec/ontology.json`. If app environments move their catalogs, this targeting rule must change with the code.

The "nothing unmodeled sneaks in" guarantee does not live in this passive write veto. It lives in the **row-driven build** (the dev expands rows in the printed order; it does not invent files) and in **operator review**. The gate is the guardrail, not the whole fence.

## Artifacts and wiring

- **Ontology catalog**: primary input. It names contexts, program meanings, construct homes, references, file ownership, and feature mappings.
- **Violation ledger**: optional sibling input. It records known condemned tree content so migration is explicit. It does not make that content conforming source.
- **Construct cards**: external authority for row meaning and exact source form. The gate follows them; it does not replace them.
- **Topology rules**: encoded in `model.py` from the topology doctrine and checked during catalog construction.
- **Claimed source files**: Python files named by built rows. These are the only files checked for row-to-source conformance.
- **Hook wiring**: `.claude/settings.json` runs the CLI before main-agent writes.

## How the agents use it

- **`tca-ontology`** runs `--order` to prove its catalog before any code exists. Model-only, cheap.
- **`tca-dev`** runs `--check <file>` (and `basedpyright <file>`) after every file it writes, reads the gate's output, and halts on a mismatch. The gate's visible output is the feedback that closes the loop; the dev is the construction, the gate is the proof.
- **The operator** reruns `--check` and `basedpyright` and diffs the built files against the ontology at review. This is the final backstop before declaring a build done.

Note: per the Claude Code docs, a session `PreToolUse` hook does not fire inside a subagent's tool calls. `tca-dev` is a subagent, so the hook never reaches its writes; the dev's `--check` loop is what governs it. The hook (wired in `.claude/settings.json`) governs the main agent's writes. `basedpyright` is not part of the gate package; it is the companion static type check the builder and operator run after gate checks.

## Authority boundary

- The gate enforces rows; it does not author rows.
- Construct cards and `docs/construct.md` own construct meaning and row grammar.
- `tca-ontology` owns catalog modeling and the violation ledger.
- `tca-dev` owns row expansion through construct cards.
- The operator owns final acceptance.
- A gate denial is evidence, not a design proposal.

## Where to change the gate

- Change row grammar, catalog coherence, topology checks, violation-ledger construction, or build order in `model.py`.
- Change AST conformance checks or smell detection in `audit.py`.
- Change command behavior, hook parsing, catalog discovery, source reconstruction, or denial output in `cli.py`.
- Change launch/import bootstrapping in `__main__.py`.
- Change doctrine first in `docs/construct.md` and the construct cards, then update gate enforcement.

## Invocation

The hook command is cwd-independent:

```
cd "${CLAUDE_PROJECT_DIR:-/path/to/project}" && uv run python .claude/scripts/tca_gate
```

`cd` to the project root (so `uv run` finds the environment and the relative package path resolves), then run the package. `__main__.py` then bootstraps `sys.path` so imports resolve regardless of where it was launched.

## Stack

Python 3.12+, Pydantic v2, `uv`, basedpyright. The package has no third-party dependency beyond Pydantic and the standard library `ast`.
