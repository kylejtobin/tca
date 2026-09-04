---
type: Playbook
description: How the SKILL.md body is written as routes to pages. Read when writing or editing any SKILL.md body.
---

# The index body

The SKILL.md body is a list of routes. One line per page, and every line has the same two parts: what the page is, then when to read it.

```markdown
# <Skill title>

- [<page>.md](<page>.md): <what it is>. Read when <situation>.
```

The route line for a page is that page's frontmatter `description`, copied verbatim. Write the description on the page first, then paste it into SKILL.md. When a page's description changes, the SKILL.md line changes with it. Because the line is a copy and not a summary, the index and the pages cannot drift apart without the drift being visible as a text mismatch.

Content lives on pages. Definitions, rules, rationale, examples, and procedures all belong to the page that owns the concept. The SKILL.md body persists in context for the whole session at a recurring token cost per line, while a page costs tokens only when opened, so every sentence of content moved from body to page is a sentence Claude reads at the moment it applies instead of on every turn.

One orienting sentence above the routes is allowed when it does work the routes cannot, such as "This directory is itself an OKF skill. Copy its shape." A heading and the route list are otherwise the whole body.

A skill small enough that a single page would hold everything is still written as SKILL.md plus that one page. The threshold for adopting the format is the repo, not the skill's size.
