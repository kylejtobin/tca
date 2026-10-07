from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.type import SkillBody, SkillDescription, SkillName


class SkillDocument(BaseModel):
    """An agent's words in the Agent Skills format: their name, what they are for, and the words."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    name: SkillName
    description: SkillDescription
    body: SkillBody
