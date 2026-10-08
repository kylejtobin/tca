from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel


class NounName(RootModel[str]):
    """The domain's word for something it has: never a step, a stage of the run, or a mechanism."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[A-Z][A-Za-z0-9]*$")


class Layer(StrEnum):
    """The level a noun sits on, set by its fields: they hold only nouns from levels above it."""

    SCALAR = "Scalar"
    VALUE = "Value"
    THING = "Thing"
    ALTERNATIVE = "Alternative"
    CROSSING = "Crossing"


class Construct(StrEnum):
    """The construct a noun is declared as, one of the skill's construct pages."""

    SEMANTIC_SCALAR = "semantic scalar"
    ORDERED_UNION = "ordered union"
    COLLECTION = "collection"
    FOREIGN_MODEL = "foreign model"
    VALUE_OBJECT = "value object"
    PROMPT_TEMPLATE = "prompt template"
    SKILL = "skill"
    UNION = "union"
    CONCEPT_MODEL = "concept model"
    ACTION = "action"
    CONTRACT_MODEL = "contract model"
    CONFIG = "config"
    TRANSFORMATION = "transformation"
    EFFECT_INTERPRETER = "effect interpreter"
    ROUTE = "route"
    COMPOSITION_ROOT = "composition root"


class FilePath(RootModel[str]):
    """The file a noun lives in, which its construct's page determines."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)
