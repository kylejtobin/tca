"""Framework-owned typed diagnostics for failed construction.

The module implements the diagnostics discipline of docs/architecture/DESIGN.md sections 5.2
(execution diagnostics are framework-owned typed facts), 6.1 (invalid required configuration
identifies the setting) and 7 (configuration models hold references to secrets, never their
contents in ordinary values or URLs). A construction failure is explained by the locations,
kinds and messages of its problems. The rejected inputs and the native exception context are
excluded: a rejected deployment value, such as a URL carrying a password, must not reappear in
the explanation. Pydantic's default ``errors()`` includes both, and ``hide_input_in_errors``
governs only the displayed error, so the projection selects Pydantic's safe rendering explicitly.
"""

from pydantic import ValidationError

from type_construction.models import Model

__all__ = ["Problem", "problems"]


class Problem(Model):
    """One construction problem: where it occurred, which native rule failed and its message."""

    location: tuple[int | str, ...]
    kind: str
    message: str


def problems(error: ValidationError) -> tuple[Problem, ...]:
    """Project a validation error to its problems without inputs or exception context."""
    return tuple(
        Problem(location=detail["loc"], kind=detail["type"], message=detail["msg"])
        for detail in error.errors(include_url=False, include_context=False, include_input=False)
    )
