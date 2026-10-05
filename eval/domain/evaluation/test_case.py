from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.type import CaseId, CaseIds, Exposure, InputText, TraceIds
from domain.evaluation.value import Reference


class CountedCase(BaseModel):
    """A test case whose runs count toward whether the change under test ships."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: CaseId
    input: InputText
    reference: Reference
    exposure: Exposure


class CountedCases(RootModel[tuple[CountedCase, ...]]):
    """Every test case of an evaluation dataset whose runs count toward the decision."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[CountedCase, ...] = Field(min_length=1)

    @property
    def ids(self) -> CaseIds:
        return CaseIds(tuple(case.id for case in self.root))


class ReportedCase(BaseModel):
    """A test case derived from the traces that informed the change under test; reported, and outside the decision."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: CaseId
    input: InputText
    reference: Reference
    traces: TraceIds


class ReportedCases(RootModel[tuple[ReportedCase, ...]]):
    """Every test case of an evaluation dataset that is reported and outside the decision."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[ReportedCase, ...] = Field(min_length=1)

    @property
    def ids(self) -> CaseIds:
        return CaseIds(tuple(case.id for case in self.root))
