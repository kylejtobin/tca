---
name: tca-noun-list
description: "The work's one list for a TCA program: the noun table of every class by name, kind, what it holds and what it is, its schema, and the check that the code and the list agree. Use when starting a package, at every file step of the tca-modeling loop (rebuild the list, run the check), and whenever a type is added, renamed, moved or removed."
---

# TCA noun list

The list is the program's inventory of nouns, one row per type, kept whole and
checked against the code. It is the artifact the loop rebuilds after every
file and the one the list gate judges: no noun missing, redundant, misnamed,
misplaced, wrongly structured or wrongly owned.

## The row

Four columns, all chosen. The file and the layer follow from the kind by
`tca-python-dev`'s table and are not written.

| column | meaning |
|---|---|
| `name`  | the class's name |
| `kind`  | the kind of the world the class subclasses: `Scalar`, `Vocabulary`, `Instant`, `Identity`, `Duration`, `Ordered`, `Many`, `Value`, `Record`, `Connection`, `Fact`, `Action`, `Request`, `Reply`, `Config` |
| `holds` | what it holds, in order: the rows its fields are typed as; for a `Scalar` its primitive; for a `Vocabulary` its words |
| `is`    | what the thing is, in one sentence a domain expert accepts; it becomes the class's docstring |

A fact's `holds` is the prior fact and the arrival, so the list read top to
bottom is the chain. An action's `holds` is the fact that intends it; what
the party may say is in its `is`, and the facts that hold each record prove it.
A streaming connection names what it streams in its `is` the same way.

## Invariants

- One row per name, one class per row.
- A class's fields are its row's `holds`, in order, and its docstring is its `is`.
- A union is not a row: a field typed `A | B` holds both rows.
- The list is rebuilt whole and reprinted after every file; it is never patched.

The schema is `schema.json` beside this file. The table is kept as JSON with
one `rows` array.

## Where it lives

One list per package, at the package's root beside its `pyproject.toml`, named
`nouns.json`. It is the package's data, so it is versioned with the package and
changes in the same commit as the code it describes; the gate reads the two
together. A project with several packages has several lists. This skill holds
the schema and the check and never a list. `just check` runs the check once per
package, on the package's root.

## In the loop

Three lines of the `tca-modeling` loop are this list, and the file gives each
its act:

- `write the chain backward from the reply, as rows of the list, before any file exists`:
  add the rows to `nouns.json`, name, kind, holds and is, before any file is written.
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
- A row precedes its code. The loop's "write the chain backward from the
  reply, as rows of the list" writes rows; the file step then writes the file. Between the two, the
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
- "Listed" means a row with its kind, its holds and its is. A noun the outcome
  names that has no row before its files begin is a noun deferred, not listed.
- The coordinator judges the list by running the check and by comparing the
  outcome's nouns to the rows, never by reading the modeler's account of it.
- The list covers `src`. Tests, docs and the project's tooling are not rows.

## The check

`noun-check.py` reads the code through its syntax tree: each class's engine
base is its kind, its field annotations in order are its holds, its docstring
is its is, and its file is judged against the kind's file in `tca-python-dev`'s
table. It reports every disagreement in the gate's words and exits nonzero
when there is one.

```
python3 -I noun-check.py <package root>
python3 -I noun-check.py <package root> --draft > nouns.json
```

Faults: `malformed` (the file is not the schema), `redundant` (a name twice),
`missing from the list`, `missing from the code`, `not a kind` (the class
subclasses no kind of the world), `wrong kind`, `wrongly held` (the fields are not
the row's holds, or a held name is not a row), `misdescribed` (the docstring is
not the row's is), `misplaced` (the kind does not live in that file), `unsaid`
(an action declares a record its row's is does not name). `--draft` writes the
rows existing code would have, in file order; nothing in it is chosen, so it
is a mirror of the code and never a plan.

The check is for Python packages under `tca-python-dev`. Another language's
skill ships its own check against the same schema and the same fault words.
