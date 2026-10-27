"""The value vocabulary: what a business value is, before anything is done with it.

Every world type is constructed natively by Pydantic at its complete declared boundary and is
immutable afterwards. Configuration is the contract: frozen, strict, no extra fields, and
instances revalidated wherever they are supplied, so a value crossing into a holder is checked
as the holder declares it and never trusted for having been valid elsewhere. Nothing here
knows about invocations, occurrences, attempts or provenance; a value cannot say where it came
from, and does not try to.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, RootModel

__all__ = ["Fact", "Measured", "Record", "Scalar", "Value", "measure"]


class Scalar[T](RootModel[T]):
    """One measured or named thing: a quantity, an identifier, a moment. Its ``root`` is the
    native value, validated strictly in the declared type, with the metadata the subclass puts
    on ``root``. A subclass may give ``root`` a default. A root model admits no extra fields
    by its nature, so that part of the contract needs no configuration."""

    model_config = ConfigDict(frozen=True, strict=True, revalidate_instances="always")


class Value(BaseModel):
    """A composite business value: fields, each a world value or a native immutable, and
    nothing the declaration did not name."""

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", revalidate_instances="always"
    )


class Record(Value):
    """A composite that holds other values together with what follows from them: a relation
    that must hold, a computation over its operands, a selection among members. Constructing a
    record is the proof that its conclusions hold for its contents."""


class Fact(Record):
    """A record as a source reports it: what the world outside said, under the names it uses.
    A fact does not establish its own origin; whoever admits it does."""


@runtime_checkable
class Measured(Protocol):
    """Anything that carries a measure: a scalar through its root, a computation through its
    derived root. Relations and computations work on measures, so a comparison over a computed
    total reads the same as one over a scalar."""

    @property
    def root(self) -> Any: ...


def measure(operand: object) -> Any:
    """The measure an operand carries. An operand that carries none is a declaration error,
    raised as such rather than compared."""
    if not isinstance(operand, Measured):
        msg = f"{type(operand).__name__} carries no measure: it has no root"
        raise TypeError(msg)
    return operand.root
