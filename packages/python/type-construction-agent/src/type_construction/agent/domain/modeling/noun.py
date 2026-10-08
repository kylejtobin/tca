from pydantic import BaseModel, ConfigDict, Field, RootModel

from type_construction.agent.domain.modeling.type import Construct, FilePath, Layer, NounName


class Noun(BaseModel):
    """One thing the domain has, placed on its layer, declared as its construct, in its file."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    name: NounName = Field(
        description=(
            "Write the word the domain uses for this thing. If the word names what something does "
            "(an estimate, a handler, a check), find the thing it produces and name that instead."
        )
    )
    layer: Layer = Field(
        description=(
            "Place it on the one layer its fields allow: a noun holds only nouns from the layers "
            "above it. If no layer fits, it is procedure, not a noun: remove it."
        )
    )
    kind: Construct = Field(
        description=(
            "Choose the construct this noun is declared as. If the construct and the layer "
            "disagree, one of them is wrong: fix it before writing the next noun."
        )
    )
    file: FilePath = Field(
        description=(
            "Write the file the construct's page names. Fill in only the context or system; "
            "never choose a file the construct does not allow."
        )
    )


class NounList(RootModel[tuple[Noun, ...]]):
    """Every noun the domain needs, bottom up by their files: the whole state of the modeling."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Noun, ...] = Field(
        description=(
            "List every noun, whole, never as a change. Before writing the list, ask which noun is "
            "missing, named twice, named for an act, stored where it should be derived, carried as "
            "a tag where structure belongs, or on the wrong layer; when the answer is none, ask "
            "again from each crossing's purpose."
        )
    )
