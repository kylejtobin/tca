from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.type import (
    Arguments, ArtifactContent, ArtifactName, CalibrationError, CheckCode, Choice, Clearance,
    Coverage, Criterion, EvaluatorId, Excerpt, Expectation, GoodOutput, Granularity, ModeName,
    ModeNames, ModelId, OpenCodeNote, OutputText, Precedence, Probability, RunCount, SampleSize, SamplingRule, Share,
    ShareDifference, Sidedness, SystemPrompt, TaskDescription, ToolName, ToolResult, ToolSchema,
    TraceId, TraceIds, TraceSource, Verdict, VersionId,
)


class Tool(BaseModel):
    """A tool an agent may call, by name, with the arguments it accepts."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    name: ToolName
    parameters: ToolSchema


class Tools(RootModel[tuple[Tool, ...]]):
    """Every tool an agent may call."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Agent(BaseModel):
    """The system under evaluation: a model working under a prompt with tools."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    model: ModelId
    prompt: SystemPrompt
    tools: Tools


class Context(BaseModel):
    """The agent under evaluation, the task it performs, and what a good output of it is."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    agent: Agent
    task: TaskDescription
    good_output: GoodOutput


class Artifact(BaseModel):
    """Something the agent produced besides its answer, such as a file it wrote."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    name: ArtifactName
    content: ArtifactContent


class Artifacts(RootModel[tuple[Artifact, ...]]):
    """Every artifact of one output."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Output(BaseModel):
    """What the agent finally answers with: its text and every artifact it produced."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    text: OutputText
    artifacts: Artifacts


class ToolCall(BaseModel):
    """One call the agent made to a tool, with what the tool returned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    tool: ToolName
    arguments: Arguments
    result: ToolResult


class Decision(BaseModel):
    """One typed value the agent decided, with its calibrated confidence."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    choice: Choice
    confidence: Probability


class Step(RootModel[ToolCall | Decision]):
    """One thing the agent did on its way to its output."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Steps(RootModel[tuple[Step, ...]]):
    """Every step of one run, in the order the agent took them."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class TraceSample(BaseModel):
    """Where the traces of an error analysis come from, and the rule that admits them."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    source: TraceSource
    rule: SamplingRule


class OpenCode(BaseModel):
    """The first failure an analyst observes in one trace."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    trace: TraceId
    note: OpenCodeNote


class OpenCodes(RootModel[tuple[OpenCode, ...]]):
    """The first failure observed in each trace of an error analysis."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[OpenCode, ...] = Field(min_length=1)


class Example(BaseModel):
    """The words of one trace that show what a failure mode decides."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    trace: TraceId
    excerpt: Excerpt


class ShippedFailure(BaseModel):
    """A failure in one trace that reached a released version of the system."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    trace: TraceId
    mode: ModeName
    version: VersionId


class ShippedFailures(RootModel[tuple[ShippedFailure, ...]]):
    """Every failure of an error analysis that reached a released version of the system."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class ModePriority(BaseModel):
    """How often a failure mode occurs among the traces, how much of it reached a released version, and the modes it is defined on."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    mode: ModeName
    frequency: Share
    impact: Share
    defined_on: ModeNames

    @property
    def precedence(self) -> Precedence:
        return Precedence(
            2 * len(self.defined_on.root) - self.frequency.root * self.impact.root
        )


class ModePriorities(RootModel[tuple[ModePriority, ...]]):
    """Every failure mode of an error analysis, in the order it is addressed."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ModePriority, ...] = Field(min_length=1)


class ValidationBar(BaseModel):
    """The agreement with reference verdicts an evaluator must reach, on at least so many reference traces, before its ratings count."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    rate: Share
    references: SampleSize


class AcceptanceTest(BaseModel):
    """An executable check, written before the pilot, that a build for a test case must pass."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    source: CheckCode


class AcceptanceTests(RootModel[tuple[AcceptanceTest, ...]]):
    """Every acceptance test of one test case."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class DecisionReference(BaseModel):
    """The decision a correct run of a test case makes."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    expected: Choice

    @property
    def granularity(self) -> Granularity:
        return Granularity.DECISION


class BuildReference(BaseModel):
    """What a correct build for a test case satisfies, and the tests it must pass."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    expectation: Expectation
    tests: AcceptanceTests

    @property
    def granularity(self) -> Granularity:
        return Granularity.BUILD


class Reference(RootModel[DecisionReference | BuildReference]):
    """What decides whether a run of a test case is correct."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def granularity(self) -> Granularity:
        return self.root.granularity


class PowerPlan(BaseModel):
    """How many runs the pilot takes, the power sought at the smallest effect worth detecting, and the cap on runs per case."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    pilot_runs: RunCount
    power: Probability
    effect: ShareDifference
    cap: RunCount


class SignificanceLevel(BaseModel):
    """The probability of a false positive the test accepts, in the direction it can detect."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    alpha: Probability
    sidedness: Sidedness


class ValidityCheck(BaseModel):
    """A test of whether an experiment's result can be trusted."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    criterion: Criterion


class ValidityChecks(RootModel[tuple[ValidityCheck, ...]]):
    """Every validity check of an experiment."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ValidityCheck, ...] = Field(min_length=1)


class Rating(BaseModel):
    """One evaluator's verdict on one trace against one failure mode, with its calibrated confidence."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    trace: TraceId
    mode: ModeName
    evaluator: EvaluatorId
    verdict: Verdict
    confidence: Probability


class Ratings(RootModel[tuple[Rating, ...]]):
    """Verdicts of evaluators on traces."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Rating, ...] = Field(min_length=1)


class ReferenceVerdict(BaseModel):
    """The verdict a trace is established to have against one failure mode, by the error analysis or by a paired incorrect or correct example."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    trace: TraceId
    mode: ModeName
    verdict: Verdict


class ReferenceVerdicts(RootModel[tuple[ReferenceVerdict, ...]]):
    """Every reference verdict evaluators are validated against."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ReferenceVerdict, ...] = Field(min_length=1)


class ReferenceSplit(BaseModel):
    """The reference traces, divided into those an evaluator is written from, tuned on, and measured on."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    train: TraceIds
    dev: TraceIds
    test: TraceIds


class Validation(BaseModel):
    """How often an evaluator agrees with reference verdicts on failing and on passing traces, over so many reference traces, and how well its confidence is calibrated."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    evaluator: EvaluatorId
    true_positive_rate: Share
    true_negative_rate: Share
    references: SampleSize
    calibration: CalibrationError


class Validations(RootModel[tuple[Validation, ...]]):
    """The validation of every evaluator of one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Validation, ...] = Field(min_length=1)


class ValidationCheck(BaseModel):
    """An evaluator's validation, held against the bar its failure mode sets."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    validation: Validation
    bar: ValidationBar

    @property
    def clearance(self) -> Clearance:
        return Clearance(
            min(
                self.validation.true_positive_rate.root,
                self.validation.true_negative_rate.root,
            )
            - self.bar.rate.root
        )

    @property
    def coverage(self) -> Coverage:
        return Coverage(self.validation.references.root - self.bar.references.root)


class ConfidenceInterval(BaseModel):
    """The range the difference between the arms' shares lies in, at the experiment's confidence."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    lower: ShareDifference
    upper: ShareDifference


class PilotEstimate(BaseModel):
    """What the pilot measured: the control share, the runs per case it requires, and the power those runs achieve."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    control: Share
    runs_per_case: RunCount
    power: Probability


class ArmShares(BaseModel):
    """One metric's share in each arm of an experiment."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    treatment: Share
    control: Share
