---
type: Reference
description: What one page holds, its frontmatter, and its body shape. Read when adding, splitting, or rewriting a page.
---

# Pages

A page carries one concept. The test for one concept: the page has a single `description` that a reader would accept as complete, and splitting the page would leave two pages that each still have a reason to be read on their own. When a page's description needs "and" to cover its contents, it is two pages.

## Frontmatter

```yaml
---
type: Reference | Playbook
description: <what it is>. Read when <situation>.
---
```

- `type` says how the page is read. `Reference` for facts consulted (what something is, what the rules are). `Playbook` for a procedure followed in order. Both values come from the OKF spec's example list. Add a third value only when a page fits neither, and use the same value for every page of that kind across the repo.
- `description` is one or two sentences. It is copied verbatim into the SKILL.md route line, so it is written for a reader deciding whether to open the page. See [index-body.md](index-body.md).

## Body

Structural markdown: headings for sub-concepts, lists for enumerations, fenced code for anything copied literally. Each rule on a page carries its reason in the same sentence or the one after it, because the reason is what lets Claude apply the rule to a case the page did not anticipate. Prose is written as standing guidance ("the route line is the page's description") rather than as a step performed once, since the page stays in context after it is read.

## Filenames

The filename is the concept's identity: lowercase-hyphenated, naming the concept (`cross-linking.md`, `skill-description.md`). `index.md` and `log.md` are reserved by OKF and are never page names.
