---
name: okf-wiki
description: Builds and maintains an Open Knowledge Format (OKF) wiki, a directory of markdown pages with YAML frontmatter, one concept per page, an index.md in every directory, and an optional log.md. Use when creating, editing, reorganizing, or auditing anything under wiki/, when adding a page or directory to a knowledge base, or when the user says "wiki", "OKF", "knowledge base", "index.md", or "frontmatter".
---

# OKF Wiki

[Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) v0.2 is a vendor-neutral standard: knowledge is a directory tree of UTF-8 markdown files with YAML frontmatter. No tooling is required. If you can `cat` a file you can read it; if you can `git clone` you can ship it. The full spec is [SPEC.md](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).

## Bundle Layout

```
wiki/
  index.md            # root index; the only index.md allowed frontmatter (okf_version)
  log.md              # optional; newest-first change history
  <group>/
    index.md          # lists every page and subdirectory in this directory
    <concept>.md      # one concept per file
```

`index.md` and `log.md` are reserved at every level and are never concept pages. Every other `.md` file is a concept.

## Concept Page

Frontmatter first, then the body. `type` is the only required key.

```markdown
---
type: Reference
title: Optional display name
description: One sentence. Copied verbatim into the parent index.md.
tags: [optional, short, strings]
generated: { by: human:kyle, at: 2026-09-04T00:00:00Z }
status: stable
---

# Title

Body. Favor headings, lists, tables, and fenced code over prose.
```

Rules:

- One concept per page. If a page needs two `description` sentences, it is two pages.
- `type` is a short descriptive noun: `Reference`, `Construct`, `Playbook`, `Decision`. Reuse the types already in the bundle before minting one.
- `description` is one sentence and is the page's entry in the index. Write it to stand alone in a list.
- `generated.by` uses the actor convention: `human:<name>` for a person, `<tool>/<model>` for an agent, `process:<name>` for automation. `verified: { by, at }` records a confirmation by someone other than the author.
- `status` is `draft`, `stable` (default when absent), or `deprecated`. Deprecated pages stay so links do not break.
- Link to other pages with relative markdown links, `[naming](./naming.md)` or `[definition](../doctrine/definition.md)`, so the wiki renders on GitHub. A link asserts a relationship; the surrounding sentence says which kind.

## Index Page

Every directory has an `index.md`. It carries no frontmatter (the root may carry `okf_version: "0.2"` and nothing else). Its body is a short statement of the question the directory answers, then a list, one entry per page and per subdirectory, each entry carrying the linked page's `description` verbatim.

```markdown
# Group Name

One or two sentences on what this directory holds.

## Pages

- [page-name](./page-name.md): The page's description sentence.
- [subgroup](./subgroup/index.md): What the subdirectory answers.
```

An index is a table of contents, not a page. Knowledge goes in a concept page; the index only points to it.

## Log Page

Optional, at any level, newest first, ISO dates:

```markdown
# Update Log

## 2026-09-04
* **Creation**: Added [semantic-scalar](./constructs/semantic-scalar.md).
* **Update**: Split the definition page into the four breaks.
```

## Workflow

When adding knowledge:

1. Decide which directory owns the question the knowledge answers. If none does, make a directory with its own `index.md` and add it to the parent index.
2. Write the concept page. Frontmatter with `type` and `description`, then the body.
3. Add one line to the directory's `index.md` using the page's `description` verbatim.
4. Link the new page from any existing page whose reader would need it, and link back where the relationship is two-way.
5. If the bundle keeps a `log.md`, add an entry.

When changing a page: keep `description` and its index entry identical. When deleting a page: mark it `status: deprecated` first unless nothing links to it.

## Checks Before Finishing

- Every non-reserved `.md` under the bundle has frontmatter with a non-empty `type`.
- No `index.md` has frontmatter, except the root with `okf_version`.
- Every page appears in its directory's `index.md`, and every index entry matches the page's `description`.
- Every relative link resolves.
