from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

from type_construction.eval.domain.evaluation.run import Failed, OracleProduce, Trace
from type_construction.eval.domain.evaluation.type import (
    CaseId,
    ErrorMessage,
    Finished,
    InputText,
    JudgedForm,
    RelativePath,
    Repetition,
    Shortfall,
)
from type_construction.eval.domain.evaluation.value import Address, DatasetRef, VersionRef


class RecordFolder(StrEnum):
    """Where each kind of record lives under the record root, by the name the map gives it:
    one log directory per dataset, holding every log ever made on it."""

    LOGS = "logs"


class RecordPath(RootModel[str]):
    """The directory the record lives in, as the deployment names it: every log, and later
    every authored dataset and experiment, is under it. The deployment names it once; every
    system that reaches it is derived from this one statement."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ModelBinding(RootModel[str]):
    """The model the runner binds a run to, as Inspect names it, its provider first:
    `anthropic/claude-opus-5-5`, `mockllm/model`. The system under evaluation calls its own
    provider; this is what judges run through and what the log says the run used."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class LogDir(RootModel[str]):
    """The directory the runner writes a dataset's logs in, as Inspect takes it: the record
    root's `logs/<dataset.name>`."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class LogLocation(RootModel[str]):
    """Where Inspect wrote a run's log, as it reports it; its one derivation is the log's
    name, the one part of it this program keeps."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"[^/]+$")

    @property
    def name(self) -> RelativePath:
        return RelativePath(self.root.rsplit("/", 1)[-1])


class FinishedStatus(RootModel[Literal["success"]]):
    """Inspect's word for a run that finished every sample; its derivation is the finished
    ending."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def ending(self) -> Finished:
        return Finished.FINISHED


class UnfinishedStatus(RootModel[Literal["started", "cancelled", "error"]]):
    """Inspect's words for a run that did not finish every sample; its derivation is the
    shortfall the record keeps, the word as the log states it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def ending(self) -> Shortfall:
        return Shortfall(self.root)


class SolverName(StrEnum):
    """The name the eval's solver is registered under in Inspect's registry, which the
    composition root registers it by and the runner names it by."""

    PRODUCING = "producing"


class FinishedHeader(BaseModel):
    """The header of a log Inspect wrote for a run that finished: where it is."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    location: LogLocation
    status: FinishedStatus


class UnfinishedHeader(BaseModel):
    """The header of a log Inspect wrote for a run that fell short: where it is, and how."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    location: LogLocation
    status: UnfinishedStatus


class LogHeader(RootModel[FinishedHeader | UnfinishedHeader]):
    """The header of a log Inspect returned, finished or not, which its status decides."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def header(self) -> FinishedHeader | UnfinishedHeader:
        return self.root


class LogHeaders(RootModel[tuple[FinishedHeader | UnfinishedHeader, ...]]):
    """What the runner returns for the one task it ran: one log header."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[FinishedHeader | UnfinishedHeader, ...] = Field(min_length=1, max_length=1)

    @property
    def header(self) -> FinishedHeader | UnfinishedHeader:
        return self.root[0]


class SampleMetadata(BaseModel):
    """What a sample carries so each repetition can address itself: the dataset and the
    version by reference."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    dataset: DatasetRef
    system: VersionRef


class CaseSample(BaseModel):
    """A case as Inspect's sample: the case's name as the sample's id, its input,
    its expected judged form as the target, and its metadata."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    id: CaseId
    input: InputText
    target: JudgedForm
    metadata: SampleMetadata


class TargetRecord(BaseModel):
    """A sample's target as Inspect hands it to the solver: its text, the judged form the
    expectation states."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    text: JudgedForm


class SampleState(BaseModel):
    """Inspect's state of one sample at the solver, read once: the
    sample's id, which is the case's, its input, its target, its metadata and the epoch; its
    derivations are the repetition's address and its production."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    sample_id: CaseId
    input_text: InputText
    target: TargetRecord
    metadata: SampleMetadata
    epoch: Repetition

    @property
    def address(self) -> Address:
        return Address(
            dataset=self.metadata.dataset,
            case=self.sample_id,
            system=self.metadata.system,
            repetition=self.epoch,
        )

    @property
    def produce(self) -> OracleProduce:
        return OracleProduce(
            address=self.address, input=self.input_text, expectation=self.target.text
        )


class MessageRole(RootModel[Literal["assistant"]]):
    """Inspect's word for the party a sample's output message is from."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class StopReason(RootModel[Literal["stop"]]):
    """Inspect's word for an output that ended because it was complete."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class AssistantMessage(BaseModel):
    """A sample's output message as Inspect accepts it: the judged form as its content."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    role: MessageRole = MessageRole("assistant")
    content: JudgedForm


class Choice(BaseModel):
    """One choice of a sample's output as Inspect accepts it: the message, complete."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    message: AssistantMessage
    stop_reason: StopReason = StopReason("stop")


class Choices(RootModel[tuple[Choice, ...]]):
    """The choices of a sample's output: one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Choice, ...] = Field(min_length=1, max_length=1)


class SampleOutput(BaseModel):
    """A sample's output as Inspect accepts it: the judged form as the completion a person
    reads, and the trace as the output's metadata, which the log keeps and the record reads
    back. It names no model, since no model generated it; the log names the model the run
    was bound to."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    choices: Choices
    metadata: Trace


class NoCompletion(RootModel[str]):
    """Inspect's completion of an output no model produced: the empty text."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(max_length=0)


class UnproducedOutput(BaseModel):
    """A logged sample's output when its repetition produced nothing: an empty completion,
    which refuses every produced output."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    completion: NoCompletion


class OutputRecord(BaseModel):
    """A logged sample's output when its repetition produced: its completion, the judged
    form, and the trace it carries as metadata; it refuses an unproduced output."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    completion: JudgedForm
    metadata: Trace


class TracedSample(BaseModel):
    """A logged sample whose output carries a trace: a repetition that produced."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    output: OutputRecord

    @property
    def left(self) -> Trace:
        return self.output.metadata


class SampleError(BaseModel):
    """What Inspect recorded of a sample's failure: its message."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    message: ErrorMessage


class ErroredSample(BaseModel):
    """A logged sample whose repetition failed before it produced: Inspect recorded its error
    and an unproduced output; known by its sample's id, its epoch and its metadata."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    id: CaseId
    epoch: Repetition
    metadata: SampleMetadata
    output: UnproducedOutput
    error: SampleError

    @property
    def left(self) -> Failed:
        return Failed(
            address=Address(
                dataset=self.metadata.dataset,
                case=self.id,
                system=self.metadata.system,
                repetition=self.epoch,
            ),
            error=self.error.message,
        )


class LoggedSample(RootModel[TracedSample | ErroredSample]):
    """A sample as the log holds it: traced, when its output carries a trace, or errored, when
    Inspect recorded its failure; its own facts decide which."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def sample(self) -> TracedSample | ErroredSample:
        return self.root
