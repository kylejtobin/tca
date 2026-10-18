from typing import Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from type_construction.eval.domain.evaluation.dataset import Dataset, IdentifiedDataset
from type_construction.eval.domain.evaluation.type import (
    ErrorMessage,
    Finished,
    InputText,
    Invariant,
    JudgedForm,
    RelativePath,
    Repetition,
    Repetitions,
    Shortfall,
    SpanId,
    TraceId,
)
from type_construction.eval.domain.evaluation.value import Address, Capture
from type_construction.eval.domain.evaluation.version import IdentifiedVersion


class Run(BaseModel):
    """The intended running of the dataset's own oracle on every case of one dataset, each
    case this many times, as a program states it: the dataset's content, which the record
    identifies before anything runs, so a program that holds the content makes one call.
    What an experiment is made of."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    dataset: Dataset
    repetitions: Repetitions


class IdentifiedRun(BaseModel):
    """A run the record can address: the dataset and the version with the identities the
    record gave them, the version being the dataset's own oracle until a system is added,
    and the repetitions. Its addresses are every case at every repetition, which is what a
    log and the traces in it are keyed by."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    dataset: IdentifiedDataset
    version: IdentifiedVersion
    repetitions: Repetitions

    @model_validator(mode="after")
    def version_is_the_oracle(self) -> Self:
        if not self.version.version == self.dataset.oracle:
            raise ValueError(Invariant.VERSION_IS_THE_ORACLE)
        return self

    @property
    def addresses(self) -> tuple[Address, ...]:
        return tuple(
            Address(
                dataset=self.dataset.ref,
                case=case.id,
                system=self.version.ref,
                repetition=Repetition(repetition),
            )
            for case in self.dataset.dataset.cases.root
            for repetition in range(1, self.repetitions.root + 1)
        )


class Execute(BaseModel):
    """The intended execution of an identified run by the runner, every case as many times
    as it says; what comes back is the run's log."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    run: IdentifiedRun


class OracleProduce(BaseModel):
    """The intended production of one case by the oracle, once, at one address: the case's
    input, which the trace shows, and the judged form the expectation states, which the
    oracle stands as. The one production the eval performs until a system is added."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    address: Address
    input: InputText
    expectation: JudgedForm


class Trace(BaseModel):
    """What one version did on one case, once: its address, the trace the eval opened for it
    and the span at its root, and what was captured when it ended. The one durable thing
    between generating and judging; every score points at one."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    address: Address
    trace: TraceId
    span: SpanId
    capture: Capture


class Traces(RootModel[tuple[Trace, ...]]):
    """Every trace one run produced: one per case per repetition, at least one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Trace, ...] = Field(min_length=1)


class FinishedLog(BaseModel):
    """The log of a run that finished every sample: the run, where the runner wrote the log
    within the record root, and the ending that says so."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    log: RelativePath
    ending: Finished


class ShortLog(BaseModel):
    """The log of a run that fell short: the run, where the runner wrote the log, and the
    runner's word for how it fell short."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    log: RelativePath
    ending: Shortfall


class RunLog(RootModel[FinishedLog | ShortLog]):
    """A run's log, of a run that finished or one that fell short, which its ending decides.
    What a program holds to read the run back, now or later."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def entry(self) -> FinishedLog | ShortLog:
        return self.root

    @property
    def run(self) -> IdentifiedRun:
        return self.root.run

    @property
    def log(self) -> RelativePath:
        return self.root.log


class ReadLog(BaseModel):
    """The intended reading of a run's log back from the record: every sample, with the trace
    its repetition produced or not; what comes back is what became of the run."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    log: RunLog


class RecordedRun(BaseModel):
    """A run the record holds whole: the run, where its log is, and one trace at each address
    the run names, and no other."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    log: RelativePath
    traces: Traces

    @model_validator(mode="after")
    def every_repetition_traced(self) -> Self:
        if not (
            len(self.traces.root) == len(self.run.addresses)
            and {trace.address for trace in self.traces.root} == set(self.run.addresses)  # pyright: ignore[reportUnhashable]
        ):
            raise ValueError(Invariant.EVERY_REPETITION_TRACED)
        return self


class Failed(BaseModel):
    """What a repetition that failed left: the runner's account of why, at its address."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    address: Address
    error: ErrorMessage


class Residue(RootModel[Trace | Failed]):
    """What one repetition the runner reached left behind: its trace, or its failure, at its
    address."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def address(self) -> Address:
        return self.root.address


class UnfinishedRun(BaseModel):
    """A run that fell short: the run, where its log is, which says why, the runner's word
    for how, and what each repetition the runner reached left behind."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    log: RelativePath
    ending: Shortfall
    left: tuple[Residue, ...]

    @model_validator(mode="after")
    def left_at_the_run_s_addresses(self) -> Self:
        if not (
            len({residue.address for residue in self.left}) == len(self.left)  # pyright: ignore[reportUnhashable]
            and {residue.address for residue in self.left} <= set(self.run.addresses)  # pyright: ignore[reportUnhashable]
        ):
            raise ValueError(Invariant.LEFT_AT_THE_RUN_S_ADDRESSES)
        return self


class RunOutcome(RootModel[RecordedRun | UnfinishedRun]):
    """What became of a run: recorded whole, or unfinished with its log saying why."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
