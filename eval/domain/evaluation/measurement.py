from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.failure_mode import DependentMode, FailureMode, IndependentMode
from domain.evaluation.metric import (
    AcceptanceMetric, Baseline, Bound, Ceiling, Floor, ModeMetric,
)
from domain.evaluation.run import Arms, Runs
from domain.evaluation.type import Flagged, Flagging, Share, Standing, TraceId, Unflagged, Verdict
from domain.evaluation.value import Ratings


class IndependentFailing(BaseModel):
    """A trace an evaluator of an independent failure mode failed."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    own: Flagged

    @property
    def verdict(self) -> Verdict:
        return Verdict.FAIL


class IndependentPassing(BaseModel):
    """A trace no evaluator of an independent failure mode failed."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    own: Unflagged

    @property
    def verdict(self) -> Verdict:
        return Verdict.PASS


class IndependentJudgment(RootModel[IndependentFailing | IndependentPassing]):
    """Whether a trace fails an independent failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def verdict(self) -> Verdict:
        return self.root.verdict


class DependentFailing(BaseModel):
    """A trace an evaluator of a dependent failure mode failed, which also fails the mode it is defined on."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    own: Flagged
    basis: Flagged

    @property
    def verdict(self) -> Verdict:
        return Verdict.FAIL


class DependentPassing(BaseModel):
    """A trace that does not fail a dependent failure mode: no evaluator of it failed the trace, or the trace passes the mode it is defined on."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    own: Unflagged | Flagged
    basis: Unflagged | Flagged

    @property
    def verdict(self) -> Verdict:
        return Verdict.PASS


class DependentJudgment(
    RootModel[Annotated[DependentFailing | DependentPassing, Field(union_mode="left_to_right")]]
):
    """Whether a trace fails a dependent failure mode."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def verdict(self) -> Verdict:
        return self.root.verdict


class IndependentReading(BaseModel):
    """One trace read against an independent failure mode through that mode's ratings."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    mode: IndependentMode
    trace: TraceId
    ratings: Ratings

    @property
    def own(self) -> Unflagged | Flagged:
        return Flagging(
            sum(
                rating.trace == self.trace
                and rating.mode == self.mode.name
                and rating.verdict == Verdict.FAIL
                for rating in self.ratings.root
            )
        ).root

    @property
    def verdict(self) -> Verdict:
        return IndependentJudgment.model_validate(self).verdict


class DependentReading(BaseModel):
    """One trace read against a dependent failure mode and the mode it is defined on, through their ratings."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    mode: DependentMode
    trace: TraceId
    ratings: Ratings

    @property
    def own(self) -> Unflagged | Flagged:
        return Flagging(
            sum(
                rating.trace == self.trace
                and rating.mode == self.mode.name
                and rating.verdict == Verdict.FAIL
                for rating in self.ratings.root
            )
        ).root

    @property
    def basis(self) -> Unflagged | Flagged:
        return Flagging(
            sum(
                rating.trace == self.trace
                and rating.mode == self.mode.depends_on
                and rating.verdict == Verdict.FAIL
                for rating in self.ratings.root
            )
        ).root

    @property
    def verdict(self) -> Verdict:
        return DependentJudgment.model_validate(self).verdict


class ModeReading(RootModel[IndependentReading | DependentReading]):
    """One trace read against one failure mode through its ratings."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def verdict(self) -> Verdict:
        return self.root.verdict


class TraceRatings(BaseModel):
    """The ratings of one trace under one failure mode."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    failure_mode: FailureMode
    trace: TraceId
    ratings: Ratings

    @property
    def mode(self) -> IndependentMode | DependentMode:
        return self.failure_mode.root

    @property
    def reading(self) -> ModeReading:
        return ModeReading.model_validate(self)


class ModeMeasurement(BaseModel):
    """A failure mode metric measured over runs through their ratings."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    metric: ModeMetric
    runs: Runs
    ratings: Ratings

    @property
    def share(self) -> Share:
        return Share(
            sum(
                TraceRatings(
                    failure_mode=self.metric.mode, trace=run.trace.id, ratings=self.ratings,
                ).reading.verdict
                == self.metric.verdict
                for run in self.runs.root
            )
            / len(self.runs.root)
        )


class AcceptanceMeasurement(BaseModel):
    """An acceptance metric measured over runs."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    metric: AcceptanceMetric
    runs: Runs

    @property
    def share(self) -> Share:
        return Share(
            sum(run.acceptance == self.metric.acceptance for run in self.runs.root)
            / len(self.runs.root)
        )


class Measurement(RootModel[ModeMeasurement | AcceptanceMeasurement]):
    """A metric measured over runs."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def share(self) -> Share:
        return self.root.share


class MetricReading(BaseModel):
    """A metric, the runs it is measured over, and the ratings of their traces."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    metric: ModeMetric | AcceptanceMetric
    runs: Runs
    ratings: Ratings

    @property
    def measurement(self) -> Measurement:
        return Measurement.model_validate(self)


class CeilingComparison(BaseModel):
    """An observed share held against its reference under a ceiling."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    bound: Ceiling
    reference: Share
    observed: Share

    @property
    def standing(self) -> Standing:
        return Standing(
            self.bound.allowed_rise.root - (self.observed.root - self.reference.root)
        )


class FloorComparison(BaseModel):
    """An observed share held against its reference under a floor."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    bound: Floor
    reference: Share
    observed: Share

    @property
    def standing(self) -> Standing:
        return Standing(
            self.bound.allowed_fall.root - (self.reference.root - self.observed.root)
        )


class Comparison(RootModel[CeilingComparison | FloorComparison]):
    """An observed share held against its reference under its bound."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def standing(self) -> Standing:
        return self.root.standing


class BoundReading(BaseModel):
    """A bound, the share it is held against, and the share observed."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bound: Ceiling | Floor
    reference: Share
    observed: Share

    @property
    def comparison(self) -> Comparison:
        return Comparison.model_validate(self)


class GuardrailCheck(BaseModel):
    """A guardrail held against an experiment's arms: the treatment's share against the control's."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bound: Bound
    arms: Arms
    ratings: Ratings

    @property
    def standing(self) -> Standing:
        return BoundReading(
            bound=self.bound.root,
            reference=MetricReading(
                metric=self.bound.metric.root, runs=self.arms.control.runs, ratings=self.ratings,
            ).measurement.share,
            observed=MetricReading(
                metric=self.bound.metric.root, runs=self.arms.treatment.runs, ratings=self.ratings,
            ).measurement.share,
        ).comparison.standing


class BaselineCheck(BaseModel):
    """A baseline held against the runs of a later version: the current share against the baseline's."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    baseline: Baseline
    runs: Runs
    ratings: Ratings

    @property
    def standing(self) -> Standing:
        return BoundReading(
            bound=self.baseline.bound.root,
            reference=self.baseline.share,
            observed=MetricReading(
                metric=self.baseline.bound.metric.root, runs=self.runs, ratings=self.ratings,
            ).measurement.share,
        ).comparison.standing
