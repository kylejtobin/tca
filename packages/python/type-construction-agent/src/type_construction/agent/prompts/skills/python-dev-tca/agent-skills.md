---
type: Construct
description: "An agent's words and the skills it may load, as package data: its prompt a template whose {{slots}} are exactly the fields of its value object, and its skills folders it loads when a task needs them. Holds text. Lives in prompts/."
---

```text
prompts/
  agents/support.md
  skills/returns/SKILL.md
  skills/returns/window.md
```

```markdown
<!-- prompts/agents/support.md -->
---
name: support
description: "Answers a customer's question about the shop."
---

Answer {{customer}}'s question about the shop. Load the returns skill when the question is about sending something back.
```

```markdown
<!-- prompts/skills/returns/SKILL.md -->
---
name: returns
description: "How a customer returns a product. Use when a question is about sending something back."
---

| When | Page |
|---|---|
| The customer asks how long they have | window.md |
```

```markdown
<!-- prompts/skills/returns/window.md -->
---
type: Page
description: "A product can be returned within thirty days of delivery."
---
```
