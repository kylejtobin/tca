"""The shared resource contract that execution integrations specialize.

The module implements the ``Resource`` construct of docs/architecture/DESIGN.md sections 5.2,
5.4 and 7. ``Resource[Native]`` is the immutable configuration of an integration resource that an
application declares as a field of its ``Settings`` and that deployment supplies values for. The
type parameter names the native object a realization yields. The supplied integration
specializes the model with its typed configuration and implements ``bind``, the binding that
realizes one resource placement in one FastStream runtime and returns the actual native object.
The core contract carries no provider configuration, client type or dependency: it imports
FastStream's common application type only, and the NATS specialization lives in
``type_construction.nats`` behind the ``nats`` installation extra.
"""

from abc import abstractmethod

from faststream import FastStream

from type_construction.models import Model

__all__ = ["Resource"]


class Resource[Native](Model):
    """Configuration of an integration resource whose realization yields a ``Native`` object.

    A binding realizes one placement: each call to ``bind`` constructs a new native object from
    this configuration and registers it with ``owner``. Uses of that placement share the returned
    object through the association the caller establishes; equal configuration realized again,
    or realized in another runtime, yields a distinct object. The live object stays outside the
    model: it is never a field, never serialized and owned by the runtime's native lifecycle.
    Declaring or constructing a resource opens no connection and reads no credential.
    """

    @abstractmethod
    def bind(self, owner: FastStream) -> Native:
        """Realize this resource placement in ``owner`` and return its native object."""
