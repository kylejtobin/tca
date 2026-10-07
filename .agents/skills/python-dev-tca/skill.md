---
type: Construct
description: "Instructions an agent loads when a task needs them: a SKILL.md naming and routing to its pages, offered by Skills apart from the agent's own words, its pages read through a read-only FileSystem. Holds text. Lives in prompts/skills/<skill>/."
---

```text
prompts/
  agents/decline-notice/SKILL.md
  skills/refunds/SKILL.md
  skills/refunds/declined.md
  skills/refunds/unsettled.md
```

```markdown
<!-- prompts/skills/refunds/SKILL.md -->
---
name: refunds
description: "How a declined or unsettled order is refunded. Use when a customer asks for their money back."
---

| When | Page |
|---|---|
| The order was declined | declined.md |
| The order is unsettled | unsettled.md |
```

```markdown
<!-- prompts/skills/refunds/declined.md -->
---
type: Page
description: "A declined order took no money, so there is nothing to refund."
---
```
