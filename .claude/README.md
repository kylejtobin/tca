# The TCA build system

This `.claude/` directory builds Type Construction Architecture code on one
principle, learned the hard way: prose shifts probability, structure deletes
options. Nothing here instructs the model to behave; everything here removes
the room for the wrong output to exist.

The loop: the design enters as `spec/model.json` (exactly one, at the repo
root), a type graph the gate validates by construction; beside it,
`spec/violation.json`, the ledger of observed breaks, proven the same way. Source files are its expansion, one
row at a time through the row's construct card, in an order the gate computes.
Every write is checked against its row; every judgment lands in an artifact a
deterministic reader refuses or admits.

What lives here:

- `agents/` two roles, never mixed: `tca-spec`, the architect, owns `spec/`
  and models the program as the catalog and sentences violations to the
  ledger (all judgment, no building);
  `tca-dev`, the builder, expands rows through cards (all building, no
  judgment), obeys verdicts, halts on the first row that will not expand,
  never marks its own work done. Subagents cannot spawn subagents, so the
  main agent orchestrates: spec models, operator reviews the table diff, dev
  expands, blocks route back to spec through the orchestrator.
- `scripts/` `tca_gate.py`, the one hook: fires on every in-scope `.py`
  write (narrowable via `TCA_GATE_PATH_SUBSTR`), denies unmodeled or
  non-conforming code, proves the catalog wherever it is consumed, prints
  the build order via `--order`
- `skills/` one `tca-*` card per construct: the row it expands, the template,
  the allowed patterns; `tca-spec` carries the catalog grammar itself
- `settings.json` wires the gate (`PreToolUse` on `Write|Edit`); the catalog
  is hook-exempt, proven at `--order` and at every source write that loads it

The doctrine is `docs/type-construction-architecture.md` and its companions;
the spec system is `spec/README.md`. The cards compile the doctrine into
fill-in shapes; nothing in this directory restates it in prose, because a
restatement is a second copy and second copies drift.
