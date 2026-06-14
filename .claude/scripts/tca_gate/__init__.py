"""TCA gate: deterministic enforcement of ontology-first construction.

Three modules: `model` (the declarative layer, row grammar, coherence, build
order, ledger; no AST), `audit` (the AST conformance shell), `cli` (transport,
the PreToolUse hook event, `--check`, `--order`, and the deny output). `--order`
loads `model` only and never imports `audit`, so proving the catalog never pays
for the conformance engine.

The target ontology catalog (exactly one in a file's ancestry, the
`spec/ontology.json` in the target root, beside the `app` package whose
package-relative source it governs) is written freely and proven by construction
wherever it is consumed:

1. A `.py` write is denied when a built row in the up-tree catalog claims the
   file and the written class does not match its row: name, construct shape,
   frozen-ness, exact field set, exact field types. Code the ontology did not
   model cannot be written into a file it claims, and an ontology that fails
   construction blocks every build it would govern.
2. `--order ONTOLOGY` validates the ontology and prints the build order as a
   topological sort. The builder follows the printed order; it never chooses.
3. `--check FILE...` runs the same audits standalone (`ontology.json` and
   `violation.json` included).
4. `--smell FILE...` runs the structural smell pass alone, no catalog required,
   for planning a refactor over un-modeled code.

Legacy audits (bare primitives, mutable containers, Optional fields, raw
Literals, bare enums) run on every in-scope write. `arbitrary_types_allowed` is
legal on exactly the class the ontology names as the consistency model, nowhere
else. `model_validator(mode="after")` is denied everywhere; `mode="before"` is
legal only in a file an ordered union row claims, and only in the wrap form: one
return placing the bare payload under its field name.

Modes: hook (stdin PreToolUse event), --check FILE..., --order ONTOLOGY, --smell FILE...

Hook scope: a `.py` write is governed only where the ontology already claims the
file, a built row in the up-tree target catalog names it. Framework files
(`/.claude/`) and `/tests/` are never governed, and a tree with no ontology, or a
file no row claims, is left alone. So the gate drops into an existing program
safely: it governs exactly what is modeled and never blanket-condemns legacy
code. The no-unmodeled guarantee lives in the row-driven build and operator
review, not in this write-time veto.

This file is procedural code policing a declarative doctrine, and the
inversion is deliberate. A language model generates by continuation over a
corpus that is overwhelmingly procedural, so type-driven invariants stated
as instructions compete with that prior on every token; stated as
write-time constraints, they do not compete at all. The gate holds the
line while constraint migrates to where it belongs, into the grammar of
what the agents can express, and it shrinks as that migration proceeds.
It is scaffolding with a demolition date, kept exactly as long as it is
load-bearing.

Do not copy this package's style into TCA domain code. The gate is the
procedural exception that explains itself: comments and docstrings are
load-bearing here because an imperative AST shell cannot make its doctrine
mapping evident through frozen model structure. Domain code is governed by the
construct cards, where meaning belongs in constructed types instead.
"""
