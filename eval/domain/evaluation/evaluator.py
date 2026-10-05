from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.failure_mode import FailureMode
from domain.evaluation.type import (
    Below, CheckCode, Cleared, Covered, EvaluatorId, EvaluatorKind, JudgePrompt, ModelId,
    Uncovered,
)
from domain.evaluation.value import ValidationCheck, Validations


class Judge(BaseModel):
    """A model that rates traces against one failure mode, returning a verdict with its calibrated confidence."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: EvaluatorId
    model: ModelId
    prompt: JudgePrompt

    @property
    def kind(self) -> EvaluatorKind:
        return EvaluatorKind.JUDGE


class CodeCheck(BaseModel):
    """A program that rates traces against one failure mode."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: EvaluatorId
    code: CheckCode

    @property
    def kind(self) -> EvaluatorKind:
        return EvaluatorKind.CODE_CHECK


class Evaluator(RootModel[Judge | CodeCheck]):
    """What rates traces against one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def id(self) -> EvaluatorId:
        return self.root.id

    @property
    def kind(self) -> EvaluatorKind:
        return self.root.kind


class Evaluators(RootModel[tuple[Evaluator, ...]]):
    """Every evaluator of one failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Evaluator, ...] = Field(min_length=1)


class ModeEvaluation(BaseModel):
    """One failure mode, the evaluators that decide it, and how each measured against reference verdicts."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    mode: FailureMode
    evaluators: Evaluators
    validations: Validations

    @property
    def clearances(self) -> tuple[Cleared | Below, ...]:
        return tuple(
            ValidationCheck(validation=validation, bar=self.mode.bar).clearance.root
            for validation in self.validations.root
        )

    @property
    def coverages(self) -> tuple[Covered | Uncovered, ...]:
        return tuple(
            ValidationCheck(validation=validation, bar=self.mode.bar).coverage.root
            for validation in self.validations.root
        )


class ModeEvaluations(RootModel[tuple[ModeEvaluation, ...]]):
    """The evaluation of every failure mode of an evaluator specification."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ModeEvaluation, ...] = Field(min_length=1)

    @property
    def clearances(self) -> tuple[Cleared | Below, ...]:
        return tuple(
            clearance for evaluation in self.root for clearance in evaluation.clearances
        )

    @property
    def coverages(self) -> tuple[Covered | Uncovered, ...]:
        return tuple(
            coverage for evaluation in self.root for coverage in evaluation.coverages
        )
