import json
from importlib.resources import files
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from type_construction.agent.domain.agent.type import SkillLocation


def read(location: SkillLocation) -> str:
    _, frontmatter, body = (
        files("type_construction.agent")
        .joinpath(location)
        .read_text(encoding="utf-8")
        .split("---\n", 2)
    )
    return json.dumps({**yaml.safe_load(frontmatter), "body": body.strip()})
