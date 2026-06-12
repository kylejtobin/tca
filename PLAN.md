# PLAN: Replace the gate script

This document replaces `.claude/scripts/tca_gate.py` as the reference for what the gate does. Avoid interacting with that script as much as possible: do not read it for guidance, do not extend it, do not refactor it in place. It remains runnable only as a differential oracle (same inputs to old and new, diff the verdicts). The rebuild works from this inventory, not from the file.

This is an inventory of the load the script carries today, not the shape of its replacement. Each load still needs a frame decision (mechanical detection vs. context surfaced for a judging reader) before it is rebuilt.

## The load: three entry points over four capabilities

### 1. Spec catalog grammar and validation (the Row/ModelTable models)

The definition of what a `spec/model.json` can say at all. Runs anywhere a table is loaded (hook, `--check`, `--order`). The violation ledger (`spec/violation.json`, the ViolationLog model: one entry per violation, four-break axis, note bounded 20-400 chars) is validated by construction at `--order` and `--check`; `--order` additionally refuses an entry whose file no longer exists.

- A grammar of 15 row kinds discriminated on `construct`: scalar, collection, frozen_model, union, discriminated_union, ordered_union, derivation, verb, boundary, consistency_model, service, route, config, main, external. A verb row is the consistency model's surface and declared body chain: name, on, optional accepts, optional returns or yields (mutually exclusive), constructs, emits; the chain must be non-empty (at least one of constructs, emits, or yields) and returns requires non-empty constructs; all referenced rows must be value types; it must sit on the consistency model, in the consistency model's file, with no duplicate (on, name). A consistency_model row holds fields (the context's state) or a `stateless` reason, never both, never neither.
- Per-row constraints: scalar has exactly one of primitive/value_space, value spaces come with >=2 members, names match casing patterns, fields/clients non-empty where required. A frozen_model row may have empty fields only when it pins a kind (identity-only variant); a row with neither payload nor identity is refused.
- Table-wide coherence: unique row names, unique (on, name) per derivation, at most one consistency model per context, every reference resolves to an existing row and a value-type row, services bind only to the consistency model, union variants each pin exactly one axis member with no duplicates and no unpinned variant, envelopes and ordered crossings sit over unions, a derivation row lives in the same file as its model, and a verb never shares its name with a field or client on its model.
- Topology rules: scalars only in `type.py` and `type.py` holds only scalars, main/config file naming, services under `service/`, routes under `api/`, boundaries and ordered crossings only in `api.py`.
- External-row verification: the claimed file exists and textually contains the class.
- A table that fails any of this blocks every build it governs.

### 2. File-versus-table conformance audit

Given a `.py` source and the single root catalog (`spec/model.json` at the repo root, found by walking up from the audited file; a second catalog on the path is denied; row file paths resolve from the root):

- Every class in the file must be claimed by a row for that file; unmodeled classes are denied ("model it before building it").
- Per-construct shape enforcement: scalar is `RootModel[...]` frozen with the exact modeled root type; collection is `RootModel[tuple[Element, ...]]`; frozen model and boundary are frozen, `extra="forbid"`, with the exact modeled field set and exact field types, and the kind pin as `Literal[Axis.MEMBER]`; config has the exact modeled fields; envelope is a frozen `RootModel` over exactly the modeled variants with `Field(discriminator="kind")`; ordered crossing has the `Annotated[...]` alias with variants in modeled order and `union_mode="left_to_right"`; consistency model is unfrozen, holds only modeled clients/fields, and every modeled client must be reached through `self.<client>` by some method body.
- A union row written as a class is denied (in-graph union must be an alias).
- Method policing on frozen constructs: only derivation-decorated methods, and only derivations the table models.
- Surface policing on the consistency model, both directions: a non-validator, non-dunder method (sync or async) not modeled as a verb row is denied, and a modeled verb missing from the class is a violation. Stub bodies (a body that is only `raise`, `...`, or `pass` after the docstring) are denied. The return annotation must name the row's `returns`, or `AsyncIterator`/`Iterator` of its `yields`, or be `None` when neither is declared. Parameters must carry `accepts` when declared and only `self` when not. Every row named in `constructs` and `emits` must appear in the body, and the negative direction holds too: a verb-body name that resolves to a value-type row outside the declared chain (accepts, returns, yields, constructs, emits) is a violation, and `try`/`except` in a verb body is denied unless it is the capture form: one statement assigning a call (awaited or not), each handler named and narrow (never Exception, BaseException, or ValidationError) and reassigning the caught signal to the same name, no else and no finally.
- Enum policing: every enum must be a modeled value space or union axis, with members exactly the modeled set.
- Validator policing: `mode="after"` denied everywhere; `mode="before"` legal only in a file a boundary or ordered-crossing row claims.
- Module-level functions denied except in route/main files.

### 3. Table-unaware "legacy" audit

Runs on every in-scope write regardless of table coverage: denies `T | None` fields, mutable container fields (`list`/`set`/`dict`), bare primitive fields, standalone-enum fields, raw string `Literal` fields, and `arbitrary_types_allowed` on anything but the named consistency model.

### 4. Build-order derivation (`--order`)

Validates the table, then topologically sorts buildable rows (dependency edges from row references, construct-rank then name as tiebreak), prints the numbered order, errors on cycles. This is the sequence tca-dev follows; it is what makes "the builder never chooses" operational.

## The wiring that makes it active

- **Hook mode** (wired in `.claude/settings.json` as PreToolUse on Write|Edit): scopes to every `.py` path by default (narrowable via `TCA_GATE_PATH_SUBSTR`), excluding `.claude/` and tests; reconstructs the post-write source from the tool input (including applying Edit replacements to the on-disk file); runs audits 1-3; emits a JSON deny with the violation list, or stays silent to allow. Empty or unparseable source passes silently.
- **`--check FILE...`**: the same audits standalone, accepting both `model.json` and `.py` files, printed violations, nonzero exit on any. This is the "rerun the gate" verification step.
- **`--order TABLE`**: as above.

That is the whole load: the spec grammar's definition and prover, the model-first write barrier, the row-conformance checker, the residual forbidden-form linter, and the build-order oracle.
