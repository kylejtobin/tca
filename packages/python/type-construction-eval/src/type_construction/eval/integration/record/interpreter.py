from inspect_ai.solver import SolverSpec
from pydantic import BaseModel, ConfigDict

from type_construction.eval.domain.evaluation.run import Execute, ReadLog, RunLog, RunOutcome
from type_construction.eval.integration.record.model import (
    LoggedSample,
    LogHeader,
    LogHeaders,
    SolverName,
)
from type_construction.eval.integration.record.provider import Logs, Record
from type_construction.eval.integration.record.task import (
    HeadedLog,
    Log,
    LogContents,
    LogDirectory,
    LogFile,
    RunHeader,
    RunTask,
)


class ExecuteInterpreter(BaseModel):
    """The one place a run is executed: the run in Inspect's terms, under the dataset's log
    directory, each repetition solved by the eval's one solver, which the composition root
    registers with Inspect under its name and the runner names back to Inspect by that
    name, since Inspect calls a solver with positional arguments no `interpret` takes; what
    comes back is the run's log, finished or short."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Execute
    provider: Record

    async def interpret(self) -> RunLog:
        return HeadedLog.model_validate(
            RunHeader(
                run=self.action.run,
                header=LogHeaders(
                    tuple(
                        LogHeader.model_validate(log, from_attributes=True).header
                        for log in await self.provider.client(
                            RunTask(action=self.action.run).task,
                            log_dir=LogDirectory(
                                root=self.provider.root,
                                dataset=self.action.run.dataset.dataset.name,
                            ).path.root,
                            solver=SolverSpec(solver=SolverName.PRODUCING),
                        )
                    )
                ).header,
            )
        ).log


class ReadLogInterpreter(BaseModel):
    """The one place a run's log is read back: every sample, each carrying the trace its
    repetition produced or not; what comes back is what became of the run, recorded whole
    or unfinished, which the log decides."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: ReadLog
    provider: Logs

    async def interpret(self) -> RunOutcome:
        return Log.model_validate(
            LogContents(
                log=self.action.log.entry,
                samples=tuple(
                    LoggedSample.model_validate(sample, from_attributes=True).sample
                    for sample in self.provider.client(
                        LogFile(root=self.provider.root, log=self.action.log.log).location.root
                    )
                ),
            )
        ).outcome
