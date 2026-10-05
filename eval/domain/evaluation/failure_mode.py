from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.type import Criterion, Definition, EvaluatorKinds, ModeName, ModeNames
from domain.evaluation.value import Example, ValidationBar


class IndependentMode(BaseModel):
    """A way the agent fails, defined on its own."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    name: ModeName
    definition: Definition
    criterion: Criterion
    fail_example: Example
    pass_example: Example
    evaluators: EvaluatorKinds
    bar: ValidationBar

    @property
    def defined_on(self) -> ModeNames:
        return ModeNames(())


class DependentMode(BaseModel):
    """A way the agent fails, defined on another failure mode."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    name: ModeName
    definition: Definition
    criterion: Criterion
    fail_example: Example
    pass_example: Example
    evaluators: EvaluatorKinds
    bar: ValidationBar
    depends_on: ModeName

    @property
    def defined_on(self) -> ModeNames:
        return ModeNames((self.depends_on,))


class FailureMode(RootModel[IndependentMode | DependentMode]):
    """A way the agent fails, with how it is decided."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def defined_on(self) -> ModeNames:
        return self.root.defined_on

    @property
    def bar(self) -> ValidationBar:
        return self.root.bar


class FailureModes(RootModel[tuple[FailureMode, ...]]):
    """Every failure mode of an error analysis."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[FailureMode, ...] = Field(min_length=1)
