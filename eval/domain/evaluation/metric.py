from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.failure_mode import FailureMode
from domain.evaluation.type import (
    Probability, Share, ShareDifference, Significance, Tolerance, Verdict, VersionId,
)
from domain.evaluation.value import ConfidenceInterval, SignificanceLevel


class ModeMetric(BaseModel):
    """The share of runs whose traces have one verdict against one failure mode."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    mode: FailureMode
    verdict: Verdict


class AcceptanceMetric(BaseModel):
    """The share of runs with one verdict against their test case's reference."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    acceptance: Verdict


class Metric(RootModel[ModeMetric | AcceptanceMetric]):
    """A share of runs an experiment measures."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )


class SecondaryMetrics(RootModel[tuple[Metric, ...]]):
    """Every metric an experiment reports and does not decide on."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Metric, ...] = Field(min_length=1)


class Ceiling(BaseModel):
    """A metric that must not rise above its reference by more than it allows."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    metric: Metric
    allowed_rise: Tolerance


class Floor(BaseModel):
    """A metric that must not fall below its reference by more than it allows."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    metric: Metric
    allowed_fall: Tolerance


class Bound(RootModel[Ceiling | Floor]):
    """How far a metric may degrade from its reference before it counts as degraded."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def metric(self) -> Metric:
        return self.root.metric


class Guardrails(RootModel[tuple[Bound, ...]]):
    """Every metric that must not degrade under treatment."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Bound, ...] = Field(min_length=1)


class TreatmentEffect(BaseModel):
    """The treatment's effect on one metric: the share in each arm, the interval their difference lies in, and its p-value."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    metric: Metric
    control: Share
    treatment: Share
    interval: ConfidenceInterval
    p: Probability

    @property
    def effect(self) -> ShareDifference:
        return ShareDifference(self.treatment.root - self.control.root)


class TreatmentEffects(RootModel[tuple[TreatmentEffect, ...]]):
    """The treatment's effect on every secondary metric of an experiment."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[TreatmentEffect, ...] = Field(min_length=1)


class SignificanceCheck(BaseModel):
    """A treatment's effect on a metric, held against the experiment's significance level."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    effect: TreatmentEffect
    level: SignificanceLevel

    @property
    def significance(self) -> Significance:
        return Significance(self.level.alpha.root - self.effect.p.root)


class Baseline(BaseModel):
    """A metric's share at the version a change was released in, bounded against degrading from it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    version: VersionId
    bound: Bound
    share: Share


class Baselines(RootModel[tuple[Baseline, ...]]):
    """The baseline of every metric monitored."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Baseline, ...] = Field(min_length=1)
