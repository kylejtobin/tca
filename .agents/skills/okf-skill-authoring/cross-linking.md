---
type: Reference
description: How pages link to each other and to SKILL.md. Read when adding a link or moving a page.
---

# Cross-linking

Links are standard markdown links with relative paths: `[pages.md](pages.md)` from a sibling, `[pages.md](../pages.md)` from a subdirectory. Relative paths resolve identically for the Read tool, for git, and for a human in an editor. A leading-slash path is bundle-relative in the OKF spec but filesystem-absolute to the tools Claude uses, so it is not used inside a skill.

Every page is listed in SKILL.md, which keeps every page one link from the index. Pages also link to each other wherever one concept depends on another, and the sentence around the link says what the relationship is, because the link itself carries no type.

A link to a page that does not exist yet is allowed; it marks knowledge not yet written and is the natural way to reserve a page during restructuring.

When a page is renamed or moved, every link to it is updated in the same change, starting with its SKILL.md route line.
