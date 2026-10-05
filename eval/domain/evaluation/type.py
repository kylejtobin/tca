from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel


class TraceId(RootModel[str]):
    """The identity of a trace."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9-]+$")


class CaseId(RootModel[str]):
    """The identity of a test case."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9-]+$")


class RunId(RootModel[str]):
    """The identity of a run: one test case attempted once under one condition."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9-]+$")


class EvaluatorId(RootModel[str]):
    """The identity of an evaluator."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9-]+$")


class VersionId(RootModel[str]):
    """The identity of a version of the system under evaluation."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[A-Za-z0-9._-]+$")


class ModelId(RootModel[str]):
    """The provider's identity for a language model."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9.-]+$")


class DatasetVersion(RootModel[str]):
    """The version of an evaluation dataset; a dataset never changes within one version."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(pattern=r"^v[1-9][0-9]*$")


class TaskDescription(RootModel[str]):
    """The task the system under evaluation performs."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class GoodOutput(RootModel[str]):
    """What an output of the system under evaluation must be to be good."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class TraceSource(RootModel[str]):
    """Where the traces of an error analysis were recorded."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SamplingRule(RootModel[str]):
    """The rule that decides which recorded runs enter an error analysis as traces."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class InputText(RootModel[str]):
    """What the system under evaluation receives at the start of a run."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class OutputText(RootModel[str]):
    """The text the system under evaluation answers with."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ArtifactName(RootModel[str]):
    """The name of an artifact within the output it belongs to."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ArtifactContent(RootModel[str]):
    """The content of an artifact."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str


class SystemPrompt(RootModel[str]):
    """The instructions an agent works under."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ToolName(RootModel[str]):
    """The name by which an agent calls a tool."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")


class ToolSchema(RootModel[str]):
    """The JSON schema of the arguments a tool accepts."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Arguments(RootModel[str]):
    """The JSON arguments an agent passes to a tool."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ToolResult(RootModel[str]):
    """What a tool returns to the agent that called it."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str


class Choice(RootModel[str]):
    """The JSON value an agent decides, as the decision's schema types it."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Expectation(RootModel[str]):
    """What a correct output of a build satisfies."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Excerpt(RootModel[str]):
    """The words of a trace that show what a failure mode decides."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class OpenCodeNote(RootModel[str]):
    """The first failure an analyst observes in one trace, in the analyst's words."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ModeName(RootModel[str]):
    """The name of a failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Definition(RootModel[str]):
    """What a failure or a metric is, in observable terms."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Criterion(RootModel[str]):
    """A binary test that a trace, a run or an experiment either meets or does not."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class HypothesisStatement(RootModel[str]):
    """A change and its predicted effect on the primary metric."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ChangeText(RootModel[str]):
    """The exact change the treatment applies to the agent."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class RandomizationUnit(RootModel[str]):
    """The unit assigned to treatment or control."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class AnalysisMethod(RootModel[str]):
    """The statistical model the primary metric is tested with."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class JudgePrompt(RootModel[str]):
    """The prompt by which a language model judges a trace against one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CheckCode(RootModel[str]):
    """The source of a program that judges a trace against one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SampleSize(RootModel[int]):
    """The number of items in a sample, above zero."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(gt=0)


class RunCount(RootModel[int]):
    """A number of runs, above zero."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(gt=0)


class RunPosition(RootModel[int]):
    """Where a run falls in the order its test case's runs were attempted, from the first."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=1)


class Unflagged(RootModel[int]):
    """No evaluator of a failure mode failed a trace."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=0, le=0)


class Flagged(RootModel[int]):
    """How many evaluators of a failure mode failed a trace, at least one."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Flagging(RootModel[Unflagged | Flagged]):
    """How many evaluators of a failure mode failed a trace."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Share(RootModel[float]):
    """The proportion of a set of items that meets a criterion, from none to all."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=1)


class ShareDifference(RootModel[float]):
    """The difference between two shares."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=-1, le=1)


class Probability(RootModel[float]):
    """The probability of an event, from impossible to certain."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=1)


class CalibrationError(RootModel[float]):
    """How far an evaluator's stated confidence lies from how often its verdicts are right."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=1)


class Precedence(RootModel[float]):
    """Where a failure mode falls in the order it is addressed: after every mode it is defined on, then by frequency times impact, lowest first."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=-1)


class Tolerance(RootModel[float]):
    """How far a share may degrade before it counts as degraded, from none to all."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=1)


class Significant(RootModel[float]):
    """How far a p-value falls below the significance level, where the effect counts as real."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(gt=0, le=1)


class NotSignificant(RootModel[float]):
    """How far a p-value falls short of the significance level, where the effect does not count as real."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=-1, le=0)


class Significance(RootModel[Significant | NotSignificant]):
    """Whether a treatment's effect clears the significance level, and by how much."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Cleared(RootModel[float]):
    """How far an evaluator's weaker agreement rate rises above its validation bar."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=1)


class Below(RootModel[float]):
    """How far an evaluator's weaker agreement rate falls below its validation bar."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=-1, lt=0)


class Clearance(RootModel[Cleared | Below]):
    """Whether an evaluator clears its validation bar, and by how much."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Within(RootModel[float]):
    """How far a share's degradation from its reference stays inside its tolerance."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=0, le=2)


class Beyond(RootModel[float]):
    """How far a share's degradation from its reference exceeds its tolerance."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: float = Field(ge=-2, lt=0)


class Standing(RootModel[Within | Beyond]):
    """Whether a share holds against its reference within its tolerance, and by how much."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Covered(RootModel[int]):
    """How many reference traces an evaluator was measured on beyond those its validation bar requires."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=0)


class Uncovered(RootModel[int]):
    """How many reference traces an evaluator was measured on short of those its validation bar requires."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(lt=0)


class Coverage(RootModel[Covered | Uncovered]):
    """Whether an evaluator was measured on as many reference traces as its validation bar requires."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Balanced(RootModel[int]):
    """Every test case was run as many times under treatment as under control."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=0, le=0)


class Unbalanced(RootModel[int]):
    """How many runs the arms differ by, summed over the test cases where they differ."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Balance(RootModel[Balanced | Unbalanced]):
    """Whether the arms of an experiment ran each test case equally often."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class Verdict(StrEnum):
    """Whether a trace or a run meets a criterion."""

    PASS = "pass"
    FAIL = "fail"


class Sidedness(StrEnum):
    """The direction of difference a test can detect."""

    ONE_SIDED = "one_sided"
    TWO_SIDED = "two_sided"


class Correction(StrEnum):
    """How the error rate is held across the secondary tests."""

    HOLM = "holm"
    BONFERRONI = "bonferroni"
    BENJAMINI_HOCHBERG = "benjamini_hochberg"


class EvaluatorKind(StrEnum):
    """The kind of evaluator that decides a failure mode."""

    JUDGE = "judge"
    CODE_CHECK = "code_check"


class Exposure(StrEnum):
    """Whether the author of the treatment saw a test case before the experiment."""

    SEEN = "seen"
    HELD_OUT = "held_out"


class Granularity(StrEnum):
    """Whether a test case asks for one decision or a complete build."""

    DECISION = "decision"
    BUILD = "build"


class TraceIds(RootModel[tuple[TraceId, ...]]):
    """Some traces, by identity."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[TraceId, ...] = Field(min_length=1)


class CaseIds(RootModel[tuple[CaseId, ...]]):
    """Some test cases, by identity."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[CaseId, ...] = Field(min_length=1)


class EvaluatorKinds(RootModel[tuple[EvaluatorKind, ...]]):
    """Every kind of evaluator that decides one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[EvaluatorKind, ...] = Field(min_length=1)


class ModeNames(RootModel[tuple[ModeName, ...]]):
    """Some failure modes, by name."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class AllCleared(RootModel[tuple[Cleared, ...]]):
    """Every evaluator of an experiment, clearing its validation bar."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Cleared, ...] = Field(min_length=1)


class AllCovered(RootModel[tuple[Covered, ...]]):
    """Every evaluator of an experiment, measured on as many reference traces as its validation bar requires."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Covered, ...] = Field(min_length=1)


class AllWithin(RootModel[tuple[Within, ...]]):
    """Every bound of an experiment or a monitoring check, holding within its tolerance."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Within, ...] = Field(min_length=1)
