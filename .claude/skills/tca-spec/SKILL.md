---
name: tca-spec
description: The mechanics of the spec catalog, the row grammar of spec/model.json. MUST be read before writing or revising any spec/model.json. Carries the full row reference, the topology rules, what fails construction, and the lifecycle; the tca-spec agent's identity file deliberately contains none of this.
---

# the spec catalog

Exactly one `spec/model.json`, at the repo root `spec/`. Never more than one;
never placed next to code. It is the program's type graph: one row per domain
meaning, holding only what is not mechanically derivable. Row `file` paths
resolve from the repo root. The gate (`.claude/scripts/tca_gate.py`) validates
the table by construction at the write and afterward holds every source file
to its row, field by field. The build order is computed from the references
(`--order`), never chosen.

Every claim in this document about what the gate proves is stamped to the
gate source as of 2026-06-11. The gate is actively edited; a claim about its
coverage is verified against the source by run, never assumed from this
page.

    {"context": "order", "rows": [ ... ]}

Row names are `PascalCase` types; field and member names are `snake_case`.
Every type a field references must resolve to a row in the table. There is no
row kind for a manager, handler, repository, or pipeline; an illegal design
does not parse. The `file` column is decided by the topology, not by feel:
read the `tca-topology` skill for what goes where, what files are named, and
what each layer may import.

## Row reference

**scalar** — one domain value. `primitive` for an open space with `constraint`
the `Field(...)` arguments verbatim; or `value_space` (a `StrEnum` class) with
`members` for a closed vocabulary. Scalars live in `type.py`, only.

    {"construct": "scalar", "name": "Price", "file": "type.py", "primitive": "Decimal", "constraint": "gt=0"}
    {"construct": "scalar", "name": "CardSuit", "file": "type.py", "value_space": "Suit", "members": ["hearts", "diamonds", "clubs", "spades"]}

**collection** — a domain sequence. `element` is a row. A plain `tuple[T, ...]`
field needs no row; this row is for the sequence that is a thing itself.

    {"construct": "collection", "name": "FillList", "file": "outcome.py", "element": "Filled", "constraint": "min_length=1"}

**frozen_model** — a composite. Every field value a row name. A union variant
adds `kind`, pinning exactly one axis member.

    {"construct": "frozen_model", "name": "Filled", "file": "outcome.py", "fields": {"account_id": "AccountId", "fill_price": "Price"}, "kind": {"axis": "OrderOutcomeKind", "member": "filled"}}

**union** — a choice among structures. `axis` is the `StrEnum`, `members` its
values, `variants` frozen_model rows each pinning a distinct member. Renders
in-graph as a type alias, never a class.

    {"construct": "union", "name": "OrderOutcome", "file": "outcome.py", "axis": "OrderOutcomeKind", "members": ["filled", "rejected"], "variants": ["Filled", "Rejected"]}

**discriminated_union** — the union's crossing form where identity travels in
the data. `over` a union row; the class is `RootModel` discriminating on
`kind`. Only at crossings; an in-graph envelope is structure without meaning.

    {"construct": "discriminated_union", "name": "OrderOutcomeEnvelope", "file": "outcome.py", "over": "OrderOutcome"}

**ordered_union** — the crossing where the wire carries no identity and
failure is expected. `over` a union whose variant order is the attempt order,
failure variant last, composed from the payload itself. Legal only in
`api.py`; the gate requires the `Annotated` alias, the exact order, and
`union_mode="left_to_right"`.

    {"construct": "ordered_union", "name": "FrameCrossing", "file": "api.py", "over": "Frame"}

**derivation** — a fact a model implies. `name` is the property, `on` the
model row, `returns` a row. Lives in its model's file; a method the table
does not declare is denied at the write.

    {"construct": "derivation", "name": "notification", "file": "outcome.py", "on": "Filled", "returns": "OrderNotification"}

**verb** — a transition on the consistency model. `name` is the method, `on` the
consistency_model row, optional `accepts` and `returns` rows. Lives in the consistency
model's file. The gate holds the surface in both directions: an unmodeled
method on the consistency model is denied at the write, and a modeled verb missing
from the class is a violation. A verb that can miss or be refused by the
domain returns a union; the table demands the home.

Body-chain cells: `yields` (a row name, the fact a streaming verb yields,
mutually exclusive with `returns`); `constructs` (row names the body
constructs); `emits` (row names projected out after proof). The chain is the
transition's content and is never empty: a verb must declare at least one of
`constructs`, `emits`, or `yields`, and a verb with `returns` must declare
`constructs`, because its return is read off a fact its body constructs. The
body is the expansion of this declared chain in dependency order.

Construction is whole-fact. The authority
(docs/type-construction-architecture.md, "Where does the work happen?"):
"Inside the constructor. One `model_validate` at the root fires the entire
tree: every field coerced, every nested model constructed, every union
discriminated, every constraint proven, one call. Code written beside the
types to 'do the work' restates work the machine is already doing." Applied
to verb bodies — and this application is a ratified derivation of this
project, not yet a sentence the authority contains — a composite lifts from
a foreign client result in one construction
(`StoredObject(object_name=name, object_bytes=result.data)`), its constituents proven by coercion
inside; constructing the scalars one by one beside the composite is the
anti-pattern, work restated outside the constructor. A chain therefore
declares the facts the body constructs, not the constituents the
constructor proves on the way.

What the gate proves about verb bodies (stamped 2026-06-11): stub bodies
(`raise NotImplementedError`, bare `...`, `pass`) are denied at the write;
the signature must conform (the return annotation carries `returns`, or
`yields` with `AsyncIterator`/`Iterator`, or `None` when neither; the
`accepts` name appears in a parameter annotation, and a verb with no
`accepts` takes only `self`); every name in `constructs` and `emits` must
appear as a Name node in the body; every row-valued Name node in the
body must be declared in the chain; and `try`/`except` in a verb
body is denied unless it is the capture form (stamped 2026-06-12): one call
assigned, each declared signal reassigned as the arrived value; the
conversion is the ordered crossing's, never the verb's, and the refusal
propagates. The whole-fact form passes this audit
naturally: the composite class is a Name node and chain-declared, while the
constituents inside the dict are invisible to the scan, and under the
ratified semantics, correctly so. What the gate does not see: statement
kinds other than `try` (`if` and loops are invisible to it) and references
that never surface as a Name node (attribute access, dict-key strings). The
gate's silence licenses nothing: a stub a check misses, and a body
statement the chain cannot explain, are breaks whether or not a check
exists for them, and they belong in the ledger the moment they are seen.

    {"construct": "verb", "name": "settle", "file": "book.py", "on": "OrderBook", "accepts": "OrderOutcomeEnvelope", "returns": "OrderNotification", "constructs": ["OrderNotification"], "emits": []}
    {"construct": "verb", "name": "stream_fills", "file": "book.py", "on": "OrderBook", "accepts": "AccountId", "yields": "Filled"}

**boundary** — foreign data crossing in. Fields are domain-side names, every
value a row. Lives in the context's `api.py`.

    {"construct": "boundary", "name": "HookEventBoundary", "file": "api.py", "fields": {"tool_name": "ToolName", "tool_input": "HookToolInputBoundary"}}

**consistency_model** — the one unfrozen node. At most one per context. `clients`
name foreign classes and are legal nowhere else; `fields` are rows and are the
context's state. A row with no fields declares `stateless` with the reason; one
of the two holds, never both, never neither. Every client must be reached by
some verb's body; an unreached client is denied at the write.
`arbitrary_types_allowed` passes the gate only on this row's class. Verbs,
fields, and clients on one model share a single namespace: no name is held
twice. The collision is a violation whether or not the gate catches it.

    {"construct": "consistency_model", "name": "OrderBook", "file": "book.py", "clients": {"bus": "EventBusClient"}, "fields": {"latest": "OrderOutcomeEnvelope"}}

**service / route / config / main** — the shell. Service binds a client to
the consistency model, under `service/`. Routes live under `api/`. Config fields
are scalar rows, in `config.py`. Main is `main.py`.

    {"construct": "service", "name": "OrderService", "file": "service/order.py", "binds": "EventBusClient", "to": "OrderBook"}
    {"construct": "route", "name": "OrderRoute", "file": "api/order.py"}
    {"construct": "config", "name": "OrderConfig", "file": "config.py", "fields": {"bus_url": "BusUrl"}}
    {"construct": "main", "name": "Main", "file": "main.py"}

**external** — a type that already exists, here or in a peer context. A
reference target, never a build item. The gate verifies the file really
defines it; an external row records what is, never what is wished for.

    {"construct": "external", "name": "Price", "file": "catalog/type.py"}

## The violation ledger

The second artifact, `spec/violation.json`, beside the catalog: the standing
record of violations observed in the tree. Written in the moment of
discovery; one entry per violation, `(file, found)` unique. Proven by
construction at every `--order` run and by `--check`.

    {"violations": [
      {"file": "service/ticker.py", "found": "imports OrderBlotter, a deleted surface", "breaks": "vacuous", "note": "dead caller of a killed design; nothing in the catalog explains it. Delete the import and call sites."},
      {"file": "domain/order/desk.py", "found": "OrderStatus compared as bare string literals", "breaks": "escaped", "note": "a vocabulary branched on as bare strings; wants a scalar over a StrEnum value space, or a union if members grow payloads."}
    ]}

`breaks` is one of the four: escaped, duplicated, vacuous, fused. `note`
points and never solves: fewer than 20 or more than 400 characters fails
construction. An entry is removed only when the violation no longer exists
in the tree; the ledger is managed, never append-only, and `--order` refuses
an entry whose `file` has already left the tree: the violation went, so the
entry goes with it.

## What fails construction

The gate refuses the table, not the build, for: a duplicate row name; a
reference resolving to no row; a field referencing a service, route, config,
main, or derivation; two consistency_model rows; a verb on anything but the consistency model, in a
different file than its model, or duplicated; a union variant with no kind, the
wrong axis, a member outside the axis, or a member pinned twice; a
discriminated_union or ordered_union over anything but a union; a derivation
in a different file than its model; a scalar outside `type.py`; anything but
scalars and externals in `type.py`; a boundary or ordered_union outside
`api.py`; a service outside `service/`, a route outside `api/`, config not in
`config.py`, main not in `main.py`; an external whose file does not define it. Absence and decisions have no cell at all: there is no
`Optional`, no `bool` field, no bare primitive reference. Factor the states;
that is what the table is for. A verb with both `returns` and `yields` is
refused; they are mutually exclusive. A verb whose `constructs`, `emits`, and `yields` are all empty is refused; a row that declares no chain declares no transition. A verb with `returns` and empty `constructs` is refused. A consistency_model with no fields and no `stateless` reason is refused, and so is one declaring both. A verb whose `constructs`, `emits`,
`accepts`, `returns`, or `yields` references a row that is not a value type
(scalar, collection, frozen_model, union, discriminated_union, ordered_union,
or external) is refused. A verb
sharing its name with a field or client of its consistency model is refused:
one name, one office.

## Lifecycle

1. Write the table. No hook fires on the catalog; it is proven by
   construction when `--order` runs and at every source write that loads it.
   A table that fails there is the model telling you it is not finished.
2. The orchestrator runs `--order` and hands the context to the builder;
   every source write is checked against its row.
3. A builder block comes back as a row and what would not fit. The answer is
   a table revision or an escalation to the operator, never an instruction.
4. The table is committed. Its diff is the design review: a few rows, on one
   page, before any expansion is read.
