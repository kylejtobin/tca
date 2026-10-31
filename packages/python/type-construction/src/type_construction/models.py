"""Configuration-only value bases for framework and application models.

The bases implement docs/architecture/DESIGN.md section 5.1. They establish the required
native configuration and nothing else: Pydantic supplies construction, constraints, defaults,
freezing, generics, schemas, errors and serialization.
"""

from pydantic import BaseModel, ConfigDict, RootModel

__all__ = ["Model", "Root"]


class Model(BaseModel):
    """Base for products: a named record whose business-typed fields exist together."""

    model_config = ConfigDict(
        validate_default=True,
        frozen=True,
    )


class Root[T](RootModel[T]):
    """Base for root values: a named scalar, sum, collection or mapping with a native JSON root."""

    model_config = ConfigDict(
        validate_default=True,
        frozen=True,
    )
