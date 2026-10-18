from typing import Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from type_construction.eval.domain.evaluation.type import (
    CaseId,
    DatasetName,
    DatasetVersion,
    Digest,
    FileText,
    InputText,
    Invariant,
    JudgedForm,
    PartName,
    RelativePath,
    Repetition,
    Summary,
    SystemName,
    SystemVersion,
)


class DatasetRef(BaseModel):
    """A dataset at one version, named: enough to pin exactly which cases a run ran."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    name: DatasetName
    version: DatasetVersion

    @property
    def key(self) -> Summary:
        return Summary(f"{self.name.root}@{self.version.root[:8]}")


class VersionRef(BaseModel):
    """A system at one version, named: enough to tell two runs' systems apart by content."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    name: SystemName
    version: SystemVersion

    @property
    def key(self) -> Summary:
        return Summary(f"{self.name.root}@{self.version.root[:8]}")


class Address(BaseModel):
    """Where one run of one version on one case sits in the whole corpus: the key every span,
    record, score and artifact carries, so no tool mints an identity of its own."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    dataset: DatasetRef
    case: CaseId
    system: VersionRef
    repetition: Repetition

    @property
    def key(self) -> Summary:
        return Summary(
            f"{self.dataset.key.root}/{self.case.root}/{self.system.key.root}"
            f"#{self.repetition.root}"
        )


class Part(BaseModel):
    """One input that determines a system's behavior, by the digest of its content and one
    line a stranger can read; an experiment varies exactly one."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    name: PartName
    digest: Digest
    summary: Summary


class Parts(RootModel[tuple[Part, ...]]):
    """Every part of a version, at least one, each named once; together they are what the
    version is."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Part, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def each_part_once(self) -> Self:
        if not len({member.name for member in self.root}) == len(self.root):  # pyright: ignore[reportUnhashable]
            raise ValueError(Invariant.EACH_PART_ONCE)
        return self


class File(BaseModel):
    """One file by its place and its text."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    path: RelativePath
    text: FileText


class Files(RootModel[tuple[File, ...]]):
    """A set of files, each path once; none is a valid set."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @model_validator(mode="after")
    def each_file_once(self) -> Self:
        if not len({member.path for member in self.root}) == len(self.root):  # pyright: ignore[reportUnhashable]
            raise ValueError(Invariant.EACH_FILE_ONCE)
        return self


class Input(BaseModel):
    """What a case hands the system: the problem in words, and the files placed in its
    workspace before it begins."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: InputText
    files: Files = Files(())


class Expectation(BaseModel):
    """What a correct production meets: the judged form a person compares against, and the
    reference files it was drawn from. It lives with the case and never reaches the system."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    judged_form: JudgedForm
    files: Files


class Capture(BaseModel):
    """Everything an evaluator may ever need of one run, taken when it ended: its production
    in the judged form, set beside what the expectation states."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    judged_form: JudgedForm
