from enum import StrEnum
from typing import Self

from pydantic import ConfigDict, Field, RootModel, model_validator


class DatasetName(RootModel[str]):
    """The name of a body of work, chosen once and never reused: lower-case words joined by
    hyphens, as a directory, a project and a task are named by it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class CaseId(RootModel[str]):
    """The name of one case within its dataset, in the same form."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class SystemName(RootModel[str]):
    """The name of a system under evaluation, in the same form; its versions are told apart
    by their content, never by this."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class PartName(RootModel[str]):
    """The name of one input that determines a system's behavior: its model, its skills, its
    check, its prompt; in the same form."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


class Digest(RootModel[str]):
    """The identity of some content: its SHA-256, as sixty-four lower-case hex characters."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{64}$")


class DatasetVersion(RootModel[str]):
    """The identity of a dataset at one moment: the digest of its cases in order, so a case
    added later is a new version and a decision taken on this one never moves."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{64}$")


class SystemVersion(RootModel[str]):
    """The identity of a whole system: the digest of its name and every part, so two versions
    can be compared only when each is fixed and whole."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{64}$")


class Repetition(RootModel[int]):
    """Which of a run's repetitions of one case this is, counted from one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=1)


class Repetitions(RootModel[int]):
    """How many times a run repeats each case, at least once."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=1)


class Description(RootModel[str]):
    """What a thing is, written for a stranger who opens it cold; a record with none does not
    render."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Summary(RootModel[str]):
    """One line a stranger can read beside a name: a part's value, a run's result; no line
    break."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[^\r\n]+$")


class InputText(RootModel[str]):
    """What a case hands the system in words: the problem as stated."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class JudgedForm(RootModel[str]):
    """A system's production in the form a person judges it in, as plain text: what an
    expectation states and a capture renders, so the two can be set side by side."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class RelativePath(RootModel[str]):
    """Where a file is within a workspace, a reference or the record: segments joined by
    slashes, none empty, none a step upward and no leading slash, so it names a place inside
    and never outside."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(
        pattern=r"^(?:[^/.][^/]*|\.[^/.][^/]*|\.\.[^/]+)(?:/(?:[^/.][^/]*|\.[^/.][^/]*|\.\.[^/]+))*$"
    )


class FileText(RootModel[str]):
    """The text of one file; nothing is a valid file."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class TraceId(RootModel[str]):
    """The identity of a run's trace, as OpenTelemetry writes it: thirty-two lower-case hex
    characters; what the trace viewer is opened by and what every score points at."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{32}$")


class SpanId(RootModel[str]):
    """The identity of the span the eval opened for a run, as OpenTelemetry writes it: sixteen
    lower-case hex characters; what a verdict is attached to."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{16}$")


class Finished(StrEnum):
    """The ending of a run that finished every sample, in evaluation's one word for it."""

    FINISHED = "finished"


class Shortfall(RootModel[str]):
    """The runner's own word for how a run fell short of finishing every sample, kept as its
    log states it: a reference into the log, which says why; never the finished ending."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)

    @model_validator(mode="after")
    def not_finished(self) -> Self:
        if not all(ending != self.root for ending in Finished):
            raise ValueError(Invariant.SHORTFALL_IS_SHORT)
        return self


class ErrorMessage(RootModel[str]):
    """The runner's own account of why a repetition failed, kept as its log states it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Invariant(StrEnum):
    """A rule of evaluation that construction enforces, in evaluation's words."""

    EACH_PART_ONCE = "a version names each part once"
    EACH_CASE_ONCE = "a dataset holds each case once"
    EACH_FILE_ONCE = "a set of files places each path once"
    EACH_PATH_ONCE_IN_CASE = "a case places each path once across its input and its expectation"
    EVERY_REPETITION_TRACED = (
        "a recorded run holds one trace at each address the run names, and no other"
    )
    VERSION_IS_THE_ORACLE = "a run's version is its dataset's own oracle"
    SHORTFALL_IS_SHORT = "a shortfall is not the finished ending"
    REF_NAMES_THE_DATASET = "an identified dataset's reference names the dataset"
    REF_NAMES_THE_VERSION = "an identified version's reference names the version"
    LEFT_AT_THE_RUN_S_ADDRESSES = (
        "what an unfinished run's repetitions left is at addresses the run names, each once"
    )
