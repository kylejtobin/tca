from inspect_ai import Task
from inspect_ai.dataset import Sample
from pydantic import BaseModel, ConfigDict, RootModel

from type_construction.eval.domain.evaluation.record import DatasetLogs
from type_construction.eval.domain.evaluation.run import (
    FinishedLog,
    IdentifiedRun,
    RecordedRun,
    Residue,
    RunLog,
    RunOutcome,
    ShortLog,
    Trace,
    Traces,
    UnfinishedRun,
)
from type_construction.eval.domain.evaluation.type import DatasetName, Description, RelativePath
from type_construction.eval.integration.inspect.model import (
    AssistantMessage,
    Choice,
    Choices,
    ErroredSample,
    FinishedHeader,
    LogDir,
    LogLocation,
    RecordPath,
    SampleMetadata,
    SampleOutput,
    SampleSpec,
    TracedSample,
    UnfinishedHeader,
)


class TaskSpec(BaseModel):
    """A run in Inspect's terms: one task named by the dataset, one sample per case carrying
    its input, its expected judged form and its references, as many epochs as repetitions,
    and a description that tells a stranger what a sample, an epoch and a score are here."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: IdentifiedRun

    @property
    def samples(self) -> tuple[Sample, ...]:
        return tuple(
            Sample.model_validate_json(
                SampleSpec(
                    id=case.id,
                    input=case.input.text,
                    target=case.expectation.judged_form,
                    metadata=SampleMetadata(
                        dataset=self.action.dataset.ref, system=self.action.version.ref
                    ),
                ).model_dump_json()
            )
            for case in self.action.dataset.dataset.cases.root
        )

    @property
    def description(self) -> Description:
        return Description(
            f"Dataset {self.action.dataset.ref.key.root} run by version "
            f"{self.action.version.ref.key.root}, {self.action.version.version.display.root}: "
            f"{self.action.version.version.description.root} "
            f"Each sample is a case; each epoch is a repetition; each score is a criterion."
        )

    @property
    def task(self) -> Task:
        return Task(
            dataset=self.samples,
            name=self.action.dataset.dataset.name.root,
            description=self.description.root,
            epochs=self.action.repetitions.root,
        )


class LogDirectory(BaseModel):
    """Where a dataset's logs live, as Inspect takes it: under the record root."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: RecordPath
    dataset: DatasetName

    @property
    def path(self) -> LogDir:
        return LogDir(f"{self.root.root}/{DatasetLogs(dataset=self.dataset).path.root}")


class FinishedHead(BaseModel):
    """A run beside the header of a log whose run finished; its derivation is the finished
    log, placed within the record root by the dataset's log directory and the log's name."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    header: FinishedHeader

    @property
    def log(self) -> FinishedLog:
        return FinishedLog(
            run=self.run,
            log=RelativePath(
                f"{DatasetLogs(dataset=self.run.dataset.dataset.name).path.root}"
                f"/{self.header.location.name.root}"
            ),
            ending=self.header.status.ending,
        )


class ShortHead(BaseModel):
    """A run beside the header of a log whose run fell short; its derivation is the short
    log, placed the same way, with the runner's word for the shortfall."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    run: IdentifiedRun
    header: UnfinishedHeader

    @property
    def log(self) -> ShortLog:
        return ShortLog(
            run=self.run,
            log=RelativePath(
                f"{DatasetLogs(dataset=self.run.dataset.dataset.name).path.root}"
                f"/{self.header.location.name.root}"
            ),
            ending=self.header.status.ending,
        )


class HeadedLog(RootModel[FinishedHead | ShortHead]):
    """A log as its header describes it, finished or short, which the header decides; its
    derivation is the run's log."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def log(self) -> RunLog:
        return RunLog(self.root.log)


class RunHeader(BaseModel):
    """A run beside the header Inspect returned for it: what the log as its header describes
    it is constructed from."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    run: IdentifiedRun
    header: FinishedHeader | UnfinishedHeader


class LogFile(BaseModel):
    """A log's place within the record root beside the root itself; its derivation is where
    the log is, as Inspect reads it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: RecordPath
    log: RelativePath

    @property
    def location(self) -> LogLocation:
        return LogLocation(f"{self.root.root}/{self.log.root}")


class TracedOutput(BaseModel):
    """A repetition's trace in the sample's terms; its derivation is the sample's output as
    Inspect accepts it: the judged form as the completion, the trace as the output's
    metadata."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    trace: Trace

    @property
    def output(self) -> SampleOutput:
        return SampleOutput(
            choices=Choices(
                (Choice(message=AssistantMessage(content=self.trace.capture.judged_form)),)
            ),
            metadata=self.trace,
        )


class FinishedLogRead(BaseModel):
    """A finished run's log as read: every sample carries a trace; its derivation is the
    recorded run."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    log: FinishedLog
    samples: tuple[TracedSample, ...]

    @property
    def outcome(self) -> RecordedRun:
        return RecordedRun(
            run=self.log.run,
            log=self.log.log,
            traces=Traces(tuple(sample.left for sample in self.samples)),
        )


class ShortLogRead(BaseModel):
    """A short run's log as read, whatever its samples carry; its derivation is the
    unfinished run, with what each repetition the runner reached left."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    log: ShortLog
    samples: tuple[TracedSample | ErroredSample, ...]

    @property
    def outcome(self) -> UnfinishedRun:
        return UnfinishedRun(
            run=self.log.run,
            log=self.log.log,
            ending=self.log.ending,
            left=tuple(Residue(sample.left) for sample in self.samples),
        )


class Log(RootModel[FinishedLogRead | ShortLogRead]):
    """A log as read, finished or short, which the log decides; its derivation is what
    became of the run."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def outcome(self) -> RunOutcome:
        return RunOutcome(self.root.outcome)


class LogContents(BaseModel):
    """A run's log beside the samples read from it: what the log as read is constructed
    from."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    log: FinishedLog | ShortLog
    samples: tuple[TracedSample | ErroredSample, ...]
