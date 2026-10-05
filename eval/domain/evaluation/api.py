from operator import attrgetter

from pydantic import BaseModel, ConfigDict

from domain.evaluation.evaluator import ModeEvaluations
from domain.evaluation.failure_mode import FailureModes
from domain.evaluation.measurement import BaselineCheck, GuardrailCheck, MetricReading
from domain.evaluation.metric import (
    Baselines, Guardrails, Metric, SecondaryMetrics, SignificanceCheck, TreatmentEffect,
    TreatmentEffects,
)
from domain.evaluation.outcome import Assessment, Health, Outcome
from domain.evaluation.run import Arms, BalanceCheck, ExperimentRuns, Runs
from domain.evaluation.test_case import CountedCases, ReportedCases
from domain.evaluation.trace import Traces
from domain.evaluation.type import (
    AnalysisMethod, Balance, Beyond, ChangeText, Correction, Criterion, DatasetVersion,
    HypothesisStatement, RandomizationUnit, Share, Significance, Verdict, VersionId, Within,
)
from domain.evaluation.value import (
    Agent, ArmShares, Context, ModePriorities, ModePriority, OpenCodes, PilotEstimate,
    PowerPlan, Ratings, ReferenceSplit, ReferenceVerdicts, ShippedFailures, SignificanceLevel,
    TraceSample, ValidityChecks,
)


class ErrorAnalysis(BaseModel):
    """What an error analysis publishes: the system and its task, the traces read, the failure each first showed, the failure modes found, each trace's verdict against each mode, and the failures that reached a release."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    context: Context
    sample: TraceSample
    traces: Traces
    open_codes: OpenCodes
    failure_modes: FailureModes
    verdicts: ReferenceVerdicts
    shipped: ShippedFailures

    @property
    def priorities(self) -> ModePriorities:
        return ModePriorities(
            tuple(
                sorted(
                    (
                        ModePriority(
                            mode=mode.root.name,
                            frequency=Share(
                                sum(
                                    verdict.mode == mode.root.name and verdict.verdict == Verdict.FAIL
                                    for verdict in self.verdicts.root
                                )
                                / len(self.traces.root)
                            ),
                            impact=Share(
                                sum(failure.mode == mode.root.name for failure in self.shipped.root)
                                / max(
                                    1,
                                    sum(
                                        verdict.mode == mode.root.name
                                        and verdict.verdict == Verdict.FAIL
                                        for verdict in self.verdicts.root
                                    ),
                                )
                            ),
                            defined_on=mode.defined_on,
                        )
                        for mode in self.failure_modes.root
                    ),
                    key=attrgetter("precedence.root"),
                )
            )
        )


class ExperimentDesign(BaseModel):
    """What an experiment pre-registers: the hypothesis, the agent under control and under treatment with the change between them, the metrics, the guardrails, the power, the significance level, the analysis, the validity checks, and the dataset it runs."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    hypothesis: HypothesisStatement
    control: Agent
    treatment: Agent
    change: ChangeText
    randomization: RandomizationUnit
    trigger: Criterion
    primary: Metric
    secondary: SecondaryMetrics
    correction: Correction
    guardrails: Guardrails
    power: PowerPlan
    significance: SignificanceLevel
    analysis: AnalysisMethod
    validity: ValidityChecks
    dataset: DatasetVersion


class EvaluationDataset(BaseModel):
    """What an evaluation dataset publishes: its version, the test cases that count toward the decision, and those reported outside it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    version: DatasetVersion
    counted: CountedCases
    reported: ReportedCases


class EvaluatorSpecification(BaseModel):
    """What an evaluator specification publishes: each failure mode with its evaluators and their validations, the reference verdicts they were measured against, and how those references were split."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    evaluations: ModeEvaluations
    references: ReferenceVerdicts
    split: ReferenceSplit


class ExperimentResult(BaseModel):
    """What an experiment's result publishes: the design, dataset and evaluators it ran under, its runs and their ratings, what the pilot measured, the treatment's effects, and the decision they lead to."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    design: ExperimentDesign
    dataset: EvaluationDataset
    specification: EvaluatorSpecification
    pilot_runs: ExperimentRuns
    counted: Arms
    reported: Arms
    ratings: Ratings
    pilot: PilotEstimate
    primary: TreatmentEffect
    secondary: TreatmentEffects

    @property
    def balance(self) -> Balance:
        return BalanceCheck(arms=self.counted, cases=self.dataset.counted.ids).balance

    @property
    def significance(self) -> Significance:
        return SignificanceCheck(effect=self.primary, level=self.design.significance).significance

    @property
    def standings(self) -> tuple[Within | Beyond, ...]:
        return tuple(
            GuardrailCheck(bound=bound, arms=self.counted, ratings=self.ratings).standing.root
            for bound in self.design.guardrails.root
        )

    @property
    def assessment(self) -> Assessment:
        return Assessment(
            clearances=self.specification.evaluations.clearances,
            coverages=self.specification.evaluations.coverages,
            balance=self.balance.root,
            significance=self.significance.root,
            standings=self.standings,
        )

    @property
    def outcome(self) -> Outcome:
        return self.assessment.outcome

    @property
    def reported_shares(self) -> ArmShares:
        return ArmShares(
            treatment=MetricReading(
                metric=self.design.primary.root, runs=self.reported.treatment.runs, ratings=self.ratings,
            ).measurement.share,
            control=MetricReading(
                metric=self.design.primary.root, runs=self.reported.control.runs, ratings=self.ratings,
            ).measurement.share,
        )


class Monitoring(BaseModel):
    """What a monitoring check publishes: the version checked, the baselines it is held against, its runs and their ratings, the evaluators that rated them, and the health they show."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    version: VersionId
    baselines: Baselines
    runs: Runs
    ratings: Ratings
    specification: EvaluatorSpecification

    @property
    def standings(self) -> tuple[Within | Beyond, ...]:
        return tuple(
            BaselineCheck(baseline=baseline, runs=self.runs, ratings=self.ratings).standing.root
            for baseline in self.baselines.root
        )

    @property
    def health(self) -> Health:
        return Health.model_validate(self)
