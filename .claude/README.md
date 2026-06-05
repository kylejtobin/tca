# The TCA crew

This `.claude/` directory is the agent crew that builds Type Construction Architecture
code under a deterministic purity gate, so a language model never hand-writes a
non-conforming type. The cure for drift is structural, not motivational: remove the room
to drift.

The complete description of the system, its architecture, the build loop, the model
bindings, how to run it, and how to port it to another project, is the single source:

> **`docs/tca-construction-crew.md`** (the operating manual)

What lives here:

- `agents/` the architect, the six forge specialists (one construct layer each), the reviewer
- `scripts/` `tca_gate.py` (the deterministic gate), and `tca_review_hook.py` with
  `tca-purity-review.md` (the semantic coverage review)
- `workflows/` `tca-build.js` (the build run: architect, then forge, then review)
- `settings.json` wires the gate (`PreToolUse`) and the review (`PostToolUse`)

The doctrine the crew builds toward is `docs/type-construction-architecture.md` and its
companions. The crew grounds in those documents as its single source of meaning and never
restates them.
