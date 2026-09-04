---
type: Playbook
description: How the `description` field is written so the skill triggers on the right requests. Read when writing or tuning a description.
---

# Skill description

The `description` is the only part of a skill Claude sees before deciding to load it, and it is truncated at 1,536 characters from the end. So the highest-value content comes first and everything about when to use the skill lives here, not in the body.

Three clauses, in order:

1. **What the skill does**, stated so a reader who has never met the domain understands it. For a domain with an unfamiliar name, the clause defines the thing as it says what the skill does with it: "Authors and maintains OKF skills, skill directories whose body is an Open Knowledge Format bundle."
2. **When to use it**, as the situations and the words a user would actually say. Claude tends to under-trigger skills, so the clause names concrete triggers ("new skill", "SKILL.md", "add a page") rather than a category.
3. **Key capabilities**, the sub-topics the pages cover, so a request about one sub-topic still matches.

Claude Code also shortens descriptions when the skill listing exceeds its budget, dropping text from the least-used skills first. Putting the key use case in the first clause protects it under both the fixed cap and the budget.

A description is tested in a fresh session: a realistic request that should load the skill, and one that should not. Context left over from authoring the skill masks gaps in the description, so the check is only meaningful when that context is gone.
