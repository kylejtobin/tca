---
type: Reference
description: The directory layout and the SKILL.md frontmatter of an OKF skill. Read when creating a skill or checking one's structure.
---

# Skill anatomy

```
.agents/skills/<domain-name>/
├── SKILL.md            # frontmatter: name, description. Body: routes to pages.
├── <concept>.md        # one concept per page, frontmatter: type, description
└── <concept>.md
```

`.agents/skills/` is the cross-runtime Agent Skills location. Claude Code discovers `.claude/skills/`; a symlink `.claude/skills/<domain-name>` pointing at the `.agents/skills/<domain-name>` directory makes one skill visible to both, and Claude Code loads a symlinked skill once.

## SKILL.md frontmatter

```yaml
---
name: <domain-name>
description: <see skill-description.md>
---
```

`name` matches the directory name exactly; see [naming.md](naming.md). `description` is what Claude reads to decide whether to load the skill; see [skill-description.md](skill-description.md). Every other frontmatter field is optional and changes runtime behavior (who can invoke, which tools are pre-approved, which model runs). Add one only when the skill needs that specific behavior; authoring guidance belongs in the body and pages, never in frontmatter.

## What loads when

The `description` sits in context in every session. The SKILL.md body enters context when the skill is invoked and stays there for the rest of the session. Pages enter context only when a Read opens them. This is the mechanism the whole format leans on: the persistent part stays tiny and the content is paid for only at the moment of use. See [index-body.md](index-body.md).
