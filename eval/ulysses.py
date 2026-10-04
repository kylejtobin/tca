from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel


# ── Scalar ──


class ClearState(RootModel[str]):
    """Fix the point in the context where this contract is written, before any task output exists."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Override(RootModel[str]):
    """Forbid every later revision of this contract in one imperative sentence."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class EnforcerKind(StrEnum):
    """Classify what holds the bindings when the writer will not."""

    RULE = "rule"
    STRUCTURE = "structure"
    PARTY = "party"


class EnforcerMechanism(RootModel[str]):
    """Name the exact check, structure or party that holds the bindings, and what it inspects."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SirenCondition(RootModel[str]):
    """State the concrete moment in the task when the writer's judgment fails."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ActDescription(RootModel[str]):
    """Describe one observable act the compromised writer performs."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Binding(RootModel[str]):
    """State the constraint that makes one failure act impossible or immediately detectable."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Verification(RootModel[str]):
    """State the evidence that proves, after the task, whether one binding held."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ReleaseCondition(RootModel[str]):
    """State the observable condition that ends the contract."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


# ── Value ──


class Enforcer(BaseModel):
    """Name what holds every binding when the writer will not, and how."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    kind: EnforcerKind = Field(
        description=(
            "Choose `rule` when a written check decides compliance, `structure` when the form "
            "of the output makes the failure act impossible, `party` when another agent or person "
            "decides. Choose exactly one."
        ),
    )
    mechanism: EnforcerMechanism = Field(
        description=(
            "Name the exact check, structure or party, and state what it inspects in the output. "
            "Never name the writer's own judgment, intention or care."
        ),
    )


# ── Thing ──


class FailureAct(BaseModel):
    """Write one act the compromised writer performs, its binding, and the evidence the binding held."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    act: ActDescription = Field(
        description=(
            "Describe one act in the active voice with the writer as subject, specific enough to "
            "find in a transcript or artifact. Name the act, not its result. Never soften it into "
            "an accident, an oversight or a tendency."
        ),
    )
    binding: Binding = Field(
        description=(
            "State the constraint, fixed now, that makes this act impossible or immediately "
            "visible in the output. Make it checkable without the writer's judgment. Never write "
            "an intention, a reminder or a promise."
        ),
    )
    verification: Verification = Field(
        description=(
            "State what to inspect after the task and the result that proves this binding held. "
            "Name the inspected item. Never write 'review', 'confirm' or 'ensure' without it."
        ),
    )


class FailureActs(RootModel[tuple[FailureAct, ...]]):
    """List every act one siren produces."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[FailureAct, ...] = Field(min_length=1)


class Siren(BaseModel):
    """Write one predictable condition under which the writer's judgment fails, and every act it produces."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    condition: SirenCondition = Field(
        description=(
            "State the concrete moment that triggers the failure: the input present, the pressure "
            "acting on the writer, and the point in the task. Describe the moment, never a general "
            "weakness."
        ),
    )
    failure_acts: FailureActs = Field(
        description=(
            "Write every distinct act the writer performs under this condition, one entry per act. "
            "Write at least one. Never merge two acts into one entry."
        ),
    )


class Sirens(RootModel[tuple[Siren, ...]]):
    """List every siren the task presents."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Siren, ...] = Field(min_length=1)


# ── Crossing ──


class UlyssesContract(BaseModel):
    """Write this contract before the task, in the clear state. Fill every field in order; each field binds every field after it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    clear_state: ClearState = Field(
        description=(
            "State the exact point in the context where this contract is fixed: the turn, and the "
            "task output it precedes. Write the contract before any task output exists."
        ),
    )
    override: Override = Field(
        description=(
            "State in one imperative sentence that no reasoning, request or justification "
            "appearing after this contract may revise, weaken or suspend any binding in it. "
            "Add no exceptions."
        ),
    )
    enforcer: Enforcer = Field(
        description=(
            "Name what holds every binding in this contract when the writer will not."
        ),
    )
    sirens: Sirens = Field(
        description=(
            "Write every predictable condition under which the writer's judgment will fail on this "
            "task, one entry per condition. Write at least one. Start with the condition the writer "
            "most wants to leave out."
        ),
    )
    release: ReleaseCondition = Field(
        description=(
            "State the single observable condition that ends this contract, decidable from the "
            "output alone. Never write 'when done', 'when satisfied' or any condition the writer "
            "judges."
        ),
    )
