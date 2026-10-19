---
name: tca-noun-list
description: "The work's one list for a TCA program: the noun table of every type by name, kind, file and layer, its schema, and the check that the code and the list agree. Use when starting a package, at every file step of the tca-modeling loop (rebuild the list, run the check), and whenever a type is added, renamed, moved or removed."
---

# TCA noun list

The list is the program's inventory of nouns, one row per type, kept whole and
checked against the code. It is the artifact the loop rebuilds after every
file and the one the list gate judges: no noun missing, redundant, misnamed,
misplaced, wrongly structured or wrongly owned.

## The row

Four columns. Two are chosen, two are derived.

| column | meaning | source |
|---|---|---|
| `name`  | the type's name, as the class is named | chosen |
| `kind`  | its construct: one of the skill's pages, `semantic scalar`, `ordered union`, `collection`, `value object`, `union`, `concept model`, `action`, `contract model`, `foreign model`, `format type`, `provider`, `transformation`, `effect interpreter`, `route`, `config`, `composition root` | chosen |
| `file`  | the file that holds it, relative to the package root | derived from the kind's page and the context or system name |
| `layer` | `Scalar`, `Value` or `Thing`; `crossing` for a construct that stands at a boundary, since crossing is not a layer | derived from the kind, or for a collection or union from its file |

Not in the row: a status (the bottom-up file order carries it) and the type's
fields (written in the file step, never in the list).

## Invariants

- One row per name.
- A row's file and layer agree with its kind's construct page.
- A collection or an alternative may sit in any file, at its members' layer.
- The list is rebuilt whole and reprinted after every file; it is never patched.

The schema is `schema.json` beside this file. The table is kept as JSON with
one `rows` array.

## Where it lives

One list per package, at the package's root beside its `pyproject.toml`, named
`nouns.json`. It is the package's data, so it is versioned with the package and
changes in the same commit as the code it describes; the gate reads the two
together. A project with several packages has several lists. This skill holds
the schema and the check and never a list. `just check` runs the check once per
package, on that package's `src` root and its `nouns.json`.

## In the loop

Three lines of the `tca-modeling` loop are this list, and the file gives each
its act:

- `add this crossing's nouns to the work's one list: name, kind, file, and layer where it carries meaning`:
  add the crossing's rows to `nouns.json`, before any of its files is written.
- `` `just check`; nonzero is not done ``: `just check` runs the noun check for
  the package, so after every file the code and the list are compared and a
  disagreement is a failed check with the loop's own recovery.
- `rebuild the whole list from what is now known and print it, every time`:
  reconcile the rows with what the file step learned, run the check until it
  agrees, and print `git diff nouns.json`; that diff is the rebuilt list.

## Working with it

- The file is the list. Never restate it in prose, never summarize it with
  counts; the check counts, and `git diff nouns.json` is the report of what
  changed. A list that needed a correction note was a list kept in two places.
- A row precedes its code. The loop's "add this crossing's nouns to the one
  list" writes rows; the file step then writes the file. Between the two, the
  check says "missing from the code", which is the plan; after the file step it
  is a fault.
- Seed once from the code, then edit. `--draft` on an existing package gives
  every settled noun in a second; from then on rows are added, renamed or
  moved by hand, in the same change as the code.
- The file order is derived, not chosen: group the rows by file, order the
  files by the skill's table, lowest first. A need below is a row edit before it
  is a code edit; a need above is a row that exists before its file does.
- A change to a noun belongs to the row that owns it. The digest of a version
  belongs to the identity that computes it, not to the run that holds the
  version; a union's variants are rows of their own; a noun that moves files
  is one row edited, not one removed and one added.
- "Listed" means a row with a file. A noun the outcome names that has no row
  before its crossing's files begin is a noun deferred, not a noun listed.
- The coordinator judges the list by running the check and by comparing the
  outcome's nouns to the rows, never by reading the modeler's account of it.
- The list covers `src`. Tests, docs and the project's tooling are not rows.

## The check

`noun-check.py` reads the code through its syntax tree and the kind-to-file map
from the Python skill's own "files in dependency order" table, so nothing is
retyped. It reports every disagreement in the gate's words and exits nonzero
when there is one.

```
python3 -I noun-check.py <python-dev-tca/SKILL.md> <package src root> <nouns.json>
python3 -I noun-check.py <python-dev-tca/SKILL.md> <package src root> --draft > nouns.json
```

Faults: `redundant` (a name twice), `missing from the list`, `missing from the
code`, `misplaced` (listed in one file, found in another), `wrongly placed` (the
kind does not live in that file), `wrongly layered`, `wrongly structured` (the
class's shape admits a different kind). `--draft` writes a first table from
existing code; the modeler corrects the chosen columns where the shape alone
cannot tell an action from a concept model or an ordered union from a scalar.

The check is for Python packages under `python-dev-tca`. Another language's
skill ships its own check against the same schema and the same fault words.
