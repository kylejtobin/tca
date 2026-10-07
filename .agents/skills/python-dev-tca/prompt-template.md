---
type: Construct
description: "An agent's own words, named for the agent, with a {{slot}} for each field of the value object that fills them: read by a format type in parser/ into a foreign model, its body the agent's TemplateStr instructions and its value object the agent's deps. Holds text. Lives in prompts/agents/<agent>/SKILL.md."
---

```markdown
<!-- prompts/agents/decline-notice/SKILL.md -->
---
name: decline-notice
description: "Writes to a customer that their order was declined, and why. Use as the decline-notice agent's own instructions."
---

Tell {{customer}} that order {{id}} was declined, and why: {{reasons}}.
```

```python
# parser/skill.py
import json
from importlib.resources import files
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from domain.shop.type import SkillLocation


def read(location: SkillLocation) -> str:
    _, frontmatter, body = (
        files("shop").joinpath(location).read_text(encoding="utf-8").split("---\n", 2)
    )
    return json.dumps({**yaml.safe_load(frontmatter), "body": body.strip()})
```

```python
# domain/shop/value.py
class DeclineNoticeValues(BaseModel):
    """What fills the decline notice: the customer, their order, and the reasons it was declined."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId
    id: OrderId
    reasons: DeclineReasons
```
