"""The refusal protocol: how a condition that does not hold says so.

A world condition checks its predicate only after Pydantic has validated its operands, and
when the predicate is false it raises a ``PydanticCustomError`` whose type is the reserved
code ``tca_refuted``. Pydantic carries that type, with the location of the refusing
condition, inside the ``ValidationError`` it reports, so whoever constructed the value can tell
a condition that did not hold from input that was the wrong shape without any channel beside
the error itself. Only trusted world conditions emit the code: application validation of
malformed input, missing data or infrastructure failure must not.
"""

from __future__ import annotations

from typing import Final, LiteralString, NoReturn

from pydantic_core import PydanticCustomError

__all__ = ["REFUTED", "refuse"]

REFUTED: Final = "tca_refuted"
"""The reserved error type of a refused condition."""


def refuse(condition: LiteralString, **context: object) -> NoReturn:
    """Refuse: the condition as a literal message template naming its context in braces, and
    the context, rendered as strings, that fills it."""
    raise PydanticCustomError(
        REFUTED, condition, {name: str(value) for name, value in context.items()}
    )
