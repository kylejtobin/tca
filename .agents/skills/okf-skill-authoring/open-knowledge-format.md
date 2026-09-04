---
type: Reference
description: What OKF is, and which parts of the spec a skill keeps. Read first when the format is unfamiliar or when a spec detail is in question.
---

# Open Knowledge Format

OKF is Google Cloud's open, vendor-neutral spec for knowledge as a directory of markdown files with YAML frontmatter, cross-linked into a graph. Current version 0.2. Spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

The parts a skill uses:

- **Concept**: one unit of knowledge, one markdown file. The file path minus `.md` is the concept's identity.
- **Frontmatter**: `type` is the only required key. `description` is recommended and feeds index entries.
- **Body**: standard markdown. Structural markdown (headings, lists, tables, fenced code) is favored over freeform prose because structure scopes what a reader loads.
- **Links**: standard markdown links between concepts. The surrounding prose says what kind of relationship the link is.
- **Index**: a listing of the directory's contents, one line per entry, each carrying the entry's `description`, so a reader sees what exists before opening anything.
- **Reserved filenames**: `index.md` and `log.md` have fixed meaning at every level of a bundle and are never used for concept documents.

## How an OKF skill departs from the spec

Two deliberate departures, made so the bundle works as a Claude Code skill. Keep both.

1. **SKILL.md is the index.** The spec's index is a frontmatter-free `index.md`. A skill needs `SKILL.md` with `name` and `description` frontmatter to load at all, so SKILL.md takes the index role and no `index.md` is written. The result is OKF-shaped rather than OKF-conformant; a consumer that needs strict conformance can generate `index.md` from the SKILL.md body.
2. **Links are relative.** The spec recommends bundle-relative links with a leading slash. Inside a skill, a leading slash reads as a filesystem-absolute path to the tools that open files, so relative paths are the form that resolves for every reader. See [cross-linking.md](cross-linking.md).

The provenance, trust, and lifecycle families (`sources`, `generated`, `verified`, `status`, `stale_after`) exist for bundles exchanged across organizations. Inside one repo, git history answers who wrote what and when, so pages carry `type` and `description` only.
