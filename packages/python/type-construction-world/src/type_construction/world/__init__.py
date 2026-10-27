"""The world: the reusable vocabulary a business value is built from.

Scalars, values, records and facts are the nouns; comparisons, computations and selections are
the relations declared between them; a refusal is how a relation says it does not hold. All of
it is native Pydantic construction, and none of it knows it will ever be evaluated.
"""

from .base import Fact, Measured, Record, Scalar, Value, measure
from .refusal import REFUTED, refuse
from .relations import (
    AtLeast,
    AtMost,
    Between,
    Beyond,
    Equal,
    Only,
    Sum,
    Times,
    arithmetic,
    comparison,
)

__all__ = [
    "REFUTED",
    "AtLeast",
    "AtMost",
    "Between",
    "Beyond",
    "Equal",
    "Fact",
    "Measured",
    "Only",
    "Record",
    "Scalar",
    "Sum",
    "Times",
    "Value",
    "arithmetic",
    "comparison",
    "measure",
    "refuse",
]
