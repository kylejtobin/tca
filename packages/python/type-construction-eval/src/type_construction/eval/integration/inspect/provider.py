from collections.abc import Awaitable, Callable, Iterator, Sequence
from functools import partial

from inspect_ai import eval_async  # pyright: ignore[reportUnknownVariableType]
from inspect_ai.log import EvalLog, EvalSample, read_eval_log_samples
from pydantic import BaseModel, ConfigDict

from type_construction.eval.integration.inspect.model import ModelBinding, RecordPath


class LogReader(BaseModel):
    """The record read back: Inspect's logs under the record root. Constructed from the one
    statement the deployment made of the record; its one derivation is the library's reader
    of a log's samples, which yields them one by one and keeps nothing."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: RecordPath

    @property
    def client(self) -> partial[Iterator[EvalSample]]:
        return partial(read_eval_log_samples, all_samples_required=False)


class Record(BaseModel):
    """The record as the deployment names it: the root its logs go under, and the model
    Inspect binds a run to. Inspect is the record and the runner, so its one derivation is
    the library's `eval_async`, bound to that model and returning log headers, since the log
    holds everything else; the record read back is a second provider from this statement."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: RecordPath
    model: ModelBinding

    @property
    def client(self) -> Callable[..., Awaitable[Sequence[EvalLog]]]:
        return partial(eval_async, model=self.model.root, log_header_only=True)

    @property
    def logs(self) -> LogReader:
        return LogReader(root=self.root)
