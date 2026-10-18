from typing import Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from type_construction.eval.domain.evaluation.type import (
    CaseId,
    DatasetName,
    Description,
    Digest,
    Invariant,
    PartName,
    Summary,
    SystemName,
)
from type_construction.eval.domain.evaluation.value import (
    DatasetRef,
    Expectation,
    Input,
    Part,
    Parts,
)
from type_construction.eval.domain.evaluation.version import Version


class Case(BaseModel):
    """One input and the expectation a correct output meets, placing each path once between
    them. The expectation lives here and never with the system, or the system could see its
    own answer key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    id: CaseId
    description: Description
    input: Input
    expectation: Expectation

    @model_validator(mode="after")
    def each_path_once(self) -> Self:
        if not len(
            {file.path for file in self.input.files.root + self.expectation.files.root}  # pyright: ignore[reportUnhashable]
        ) == len(self.input.files.root) + len(self.expectation.files.root):
            raise ValueError(Invariant.EACH_PATH_ONCE_IN_CASE)
        return self


class Cases(RootModel[tuple[Case, ...]]):
    """The cases of one dataset in order, at least one, each named once."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Case, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def each_case_once(self) -> Self:
        if not len({case.id for case in self.root}) == len(self.root):  # pyright: ignore[reportUnhashable]
            raise ValueError(Invariant.EACH_CASE_ONCE)
        return self


class Dataset(BaseModel):
    """A versioned set of cases: a body of work a system is judged on. Its version is the
    digest of its cases in order, so an experiment pins exactly which cases it ran and a case
    added later is a new version."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    name: DatasetName
    description: Description
    cases: Cases


class IdentifiedDataset(BaseModel):
    """A dataset with the identity the record gave it, its reference naming it: what a run is
    made of, since an address needs a version the record issued. Its oracle derives from
    it: the expectation itself as a version whose one part is the dataset at this identity,
    so no one authors an oracle and it cannot drift from its dataset."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    dataset: Dataset
    ref: DatasetRef

    @model_validator(mode="after")
    def ref_names_the_dataset(self) -> Self:
        if not self.ref.name == self.dataset.name:
            raise ValueError(Invariant.REF_NAMES_THE_DATASET)
        return self

    @property
    def oracle(self) -> Version:
        return Version(
            name=SystemName("reference"),
            display=Summary(f"the expectation of {self.ref.key.root}"),
            description=Description(
                f"The expectation of every case of {self.ref.key.root}, standing as the "
                f"production: the reference run as a system, so the record and every "
                f"evaluator are proven on it before any system is judged."
            ),
            parts=Parts(
                (
                    Part(
                        name=PartName("expectation"),
                        digest=Digest(self.ref.version.root),
                        summary=Summary(f"the cases of {self.ref.key.root}"),
                    ),
                )
            ),
        )
