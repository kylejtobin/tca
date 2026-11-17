"""Public TCA value foundations and application constructs.

The core exports depend on Pydantic, Pydantic Settings and FastStream's common application
type only. Execution integrations are imported from their own modules: the NATS integration is
``type_construction.nats`` and requires the ``nats`` installation extra.
"""

from type_construction.models import Model, Root
from type_construction.resources import Resource
from type_construction.settings import Settings

__all__ = ["Model", "Resource", "Root", "Settings"]
