from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.trace import Trace
from domain.evaluation.type import Balance, CaseId, CaseIds, RunId, RunPosition, Verdict, VersionId


class Run(BaseModel):
    """One test case attempted once by one version of the system, its trace, and its verdict against the case's reference."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: RunId
    case: CaseId
    version: VersionId
    trace: Trace
    acceptance: Verdict


class Runs(RootModel[tuple[Run, ...]]):
    """Runs measured together."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Run, ...] = Field(min_length=1)


class ExperimentRun(BaseModel):
    """A run of an experiment, at its place in the randomized order of its test case's runs."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    run: Run
    position: RunPosition


class ExperimentRuns(RootModel[tuple[ExperimentRun, ...]]):
    """The runs of one arm or one phase of an experiment."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ExperimentRun, ...] = Field(min_length=1)

    @property
    def runs(self) -> Runs:
        return Runs(tuple(experiment_run.run for experiment_run in self.root))


class Arms(BaseModel):
    """The runs of an experiment under treatment and under control."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    treatment: ExperimentRuns
    control: ExperimentRuns


class BalanceCheck(BaseModel):
    """An experiment's arms, held against the test cases each must run equally often."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    arms: Arms
    cases: CaseIds

    @property
    def balance(self) -> Balance:
        return Balance(
            sum(
                abs(
                    sum(run.case == case for run in self.arms.treatment.runs.root)
                    - sum(run.case == case for run in self.arms.control.runs.root)
                )
                for case in self.cases.root
            )
        )
