from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from type_construction.eval.domain.evaluation.type import (
    Description,
    Invariant,
    Summary,
    SystemName,
)
from type_construction.eval.domain.evaluation.value import Parts, VersionRef


class Version(BaseModel):
    """The complete definition of a system under evaluation: its name, the line a person
    refers to it by, what it is, and every part that determines its behavior. Its identity
    is the digest of its name and its parts, so the display name identifies nothing and two
    versions differ only where a part does."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    name: SystemName
    display: Summary
    description: Description
    parts: Parts


class IdentifiedVersion(BaseModel):
    """A version with the identity the record gave it, its reference naming it: the digest
    of its name and parts, which no person typed."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    version: Version
    ref: VersionRef

    @model_validator(mode="after")
    def ref_names_the_version(self) -> Self:
        if not self.ref.name == self.version.name:
            raise ValueError(Invariant.REF_NAMES_THE_VERSION)
        return self
