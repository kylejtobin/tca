from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.type import (
    AllCleared, AllCovered, AllWithin, Balanced, Below, Beyond, Cleared, Covered,
    NotSignificant, Significant, Unbalanced, Uncovered, Within,
)


class Shipped(BaseModel):
    """An experiment whose evaluators all cleared and covered their bars, whose arms balanced, whose treatment's effect was significant, and whose guardrails all held: the change ships."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    clearances: AllCleared
    coverages: AllCovered
    balance: Balanced
    significance: Significant
    standings: AllWithin


class NotShipped(BaseModel):
    """An experiment whose evaluators all cleared and covered their bars and whose arms balanced, but whose treatment's effect was not significant or broke a guardrail: the change does not ship."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    clearances: AllCleared
    coverages: AllCovered
    balance: Balanced
    significance: Significant | NotSignificant
    standings: tuple[Within | Beyond, ...]


class Rerun(BaseModel):
    """An experiment whose result cannot be trusted, because an evaluator fell short of its bar or the arms did not balance: it runs again."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    clearances: tuple[Cleared | Below, ...]
    coverages: tuple[Covered | Uncovered, ...]
    balance: Balanced | Unbalanced
    significance: Significant | NotSignificant
    standings: tuple[Within | Beyond, ...]


class Outcome(
    RootModel[Annotated[Shipped | NotShipped | Rerun, Field(union_mode="left_to_right")]]
):
    """What an experiment's result decides for the change it tests."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )


class Assessment(BaseModel):
    """Everything an experiment's decision rests on: each evaluator's clearance and coverage, the arms' balance, the significance of the treatment's effect, and each guardrail's standing."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    clearances: tuple[Cleared | Below, ...]
    coverages: tuple[Covered | Uncovered, ...]
    balance: Balanced | Unbalanced
    significance: Significant | NotSignificant
    standings: tuple[Within | Beyond, ...]

    @property
    def outcome(self) -> Outcome:
        return Outcome.model_validate(self)


class Steady(BaseModel):
    """A monitored version whose every baseline holds within its tolerance."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    standings: AllWithin


class Regressing(BaseModel):
    """A monitored version that degraded beyond the tolerance of at least one baseline."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    standings: tuple[Within | Beyond, ...]


class Health(RootModel[Annotated[Steady | Regressing, Field(union_mode="left_to_right")]]):
    """What a monitoring check finds of a later version against its baselines."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
