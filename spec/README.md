# The Program Spec

The structural companion to [the authority](../docs/type-construction-architecture.md) for the act of designing. The authority defines what the constructs are; [the topology](../docs/program-topology.md) defines where their code belongs; this document defines how a program is planned, and it begins from the same principle everything else does: **a design is a value, so it enters only by construction.**

---

## The Artifact

The repository carries exactly one spec: `spec/model.json` at the root, the program's type graph in minimal notation. One row per domain meaning. A row states exactly the information that cannot be derived mechanically and nothing more:

- which construct it is (the closed set, the union's two crossing forms included: discriminated where identity is in the data, ordered where the wire carries none)
- its name
- what it references (fields, element, variants, the union it crosses for)
- the one constraint it carries

Everything else in the source files, the imports, the `frozen=True`, the `extra="forbid"`, the `RootModel` spelling, the discriminator wiring, is expansion: derivable from the row and the construct's card (`.claude/skills/tca-*`). The spec is what remains of a TCA program after everything derivable is deleted. That this residue is small, a context in a dozen lines, is not a convenience; it is the architecture's one-to-one correspondence made visible. The program is its types, so the program collapses to its type graph and re-expands from it.

```json
{
  "context": "order",
  "rows": [
    {"construct": "scalar", "name": "Price", "file": "type.py", "primitive": "Decimal", "constraint": "gt=0"},
    {"construct": "frozen_model", "name": "Filled", "file": "outcome.py",
     "fields": {"account_id": "AccountId", "fill_price": "Price"},
     "kind": {"axis": "OrderOutcomeKind", "member": "filled"}},
    {"construct": "union", "name": "OrderOutcome", "file": "outcome.py",
     "axis": "OrderOutcomeKind", "members": ["filled", "rejected"], "variants": ["Filled", "Rejected"]},
    {"construct": "consistency_model", "name": "OrderBook", "file": "book.py",
     "clients": {"bus": "EventBusClient"}, "fields": {"latest": "OrderOutcomeEnvelope"}}
  ]
}
```

The consistency model's surface is rows too: a `verb` row declares a transition from one proven state to the next, naming the method the one mutable node carries, what it accepts, and what it returns, so the surface is statable, reviewable as a diff, and held complete by the gate in both directions. A verb row declares its body as a chain: `constructs` (the fact rows the body constructs), `emits` (the rows projected out after proof), and `yields` (the row a streaming verb yields, in place of `returns`). The chain is never empty: a verb must declare at least one of `constructs`, `emits`, or `yields`, and a verb with `returns` must declare `constructs`, because a transition that constructs nothing, emits nothing, and yields nothing is not a verb. The body is the expansion of the declared chain in the construction graph's dependency order, so behavior is modeled, reviewed, and held to, exactly as types are.

A type that already exists enters as an `external` row naming the file that defines it. The gate verifies the file does. An external row records what is, never what is wished for.

## The Second Artifact: The Violation Ledger

Beside the catalog sits `spec/violation.json`, the standing record of what the tree contains that the catalog cannot explain. Modeling happens with the tree open, and the moment a misuse is seen is the moment its diagnosis is cheapest, so the architect logs it then: the file, what was found, which of the four breaks it is, and a note that points toward the structure the meaning wants. The note is bounded by construction (20 to 400 characters): the ledger captures the scent while it is hot and refuses the essay, because the fix is a later dispatch's work and the model must keep moving. The ledger is the operator's demolition queue, and it cannot rot: it is proven at every `--order` run, `(file, found)` is unique, and an entry whose file has left the tree fails the run until the entry leaves with it. A mention of a removed system semantically resurrects it; the ledger is where such mentions are sentenced rather than obeyed.

## The Grammar Is the Doctrine Compiled

The spec is validated by construction (`.claude/scripts/tca_gate.py`), and its grammar is the authority's rules expressed as what can be written at all. The four breaks are not reviewed out of a design; they fail to parse.

- **Escaped** has no cell: every field references a declared row, so a bare primitive, a dict, an `Optional` cannot appear as a field's type.
- **Duplicated** has no cell: row names are unique, a kind is pinned in exactly one place, a derivable value has no field to be stored in, only a derivation row.
- **Vacuous** has no cell: every row is expanded and checked, and an external must really exist.
- **Fused** has no cell: absence and decisions are union rows over a named axis, every variant pins one member, and the one unfrozen node is the single `consistency_model` row, the only place a client can be held.

There is no row kind for a manager, a handler, a repository, or a pipeline. An illegal design is not denied; it is unrepresentable.

## The Lifecycle

1. **The spec precedes the code, mechanically.** The gate denies any source write in a context with no spec. Model-first is not a discipline; it is the only order of operations that exists.
2. **The spec is the design review.** A change to a context begins as a diff of `spec/model.json`: a few rows added, a field rerouted, a union grown a variant. That diff is the modeling decision, complete, on one page, reviewable before any expansion is read. Approving a design means approving rows.
3. **The build order is computed, never chosen.** `--order` prints the topological sort of the graph: leaves first, because a value cannot be constructed before the values it composes. The builder follows; nothing sequences by judgment.
4. **The spec is the contract during expansion.** Every write is checked against its row, name by name, field by field, shape by shape through the construct's card. A file that drifts from its row is denied at the write, not discovered at review.
5. **The spec cannot rot.** Every prior spec system dies of drift: the spec is a second copy of the program's meaning, kept in agreement by hand, the duplicated break at system scale. This spec is enforced against every future write, so divergence is not detected late, it is refused early. A spec that is load-bearing cannot become documentation.

## One Structure, Three Readers

The same rows serve every reader the architecture serves, which is the authority's own test applied to design:

- **The human** reads the design as the design, free of expansion noise. The file listing of rows is the context's vocabulary; the references are its structure.
- **The machine** validates the graph deterministically, computes the build order, and holds every file to its row.
- **The language model** generates against the spec as its anchor. Its modeling judgment is expressed once, into a form that refuses incorrect content, before any code exists; every generation after is a fill-in of row × card. The model is not trusted to follow the design. The design is the only thing its output can parse as.

## Completeness as a Test

Because the correspondence is one-to-one, spec × cards accounts for the entire program, bodies included: any structure in any source file that the expansion cannot explain is, by definition, one of the four breaks. A verb body's statements are the expansion of its declared chain, so a statement the chain cannot explain is a break in behavior exactly as an unaccounted field is a break in structure. The spec is not a sketch of the important parts. It is the program modulo mechanical expansion, and that makes it the standing falsifier of the architecture itself: the day a real program needs code the spec cannot represent, either a construct is missing from the doctrine or the code is a break, and the gate forces that question to be answered in the open.
