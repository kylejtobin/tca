import asyncio

from inspect_ai.model import ModelOutput
from inspect_ai.solver import Generate, Solver, TaskState, solver

from type_construction.eval.config import EvalConfig
from type_construction.eval.domain.evaluation.dataset import (
    Case,
    Cases,
    Dataset,
    IdentifiedDataset,
)
from type_construction.eval.domain.evaluation.record import DatasetLogs
from type_construction.eval.domain.evaluation.run import (
    Execute,
    Failed,
    FinishedLog,
    IdentifiedRun,
    OracleProduce,
    ReadLog,
    RecordedRun,
    Residue,
    Run,
    RunLog,
    RunOutcome,
    ShortLog,
    Trace,
    Traces,
    UnfinishedRun,
)
from type_construction.eval.domain.evaluation.type import (
    CaseId,
    DatasetName,
    DatasetVersion,
    Description,
    Digest,
    ErrorMessage,
    FileText,
    Finished,
    InputText,
    Invariant,
    JudgedForm,
    PartName,
    RecordFolder,
    RelativePath,
    Repetition,
    Repetitions,
    Shortfall,
    SpanId,
    Summary,
    SystemName,
    SystemVersion,
    TraceId,
)
from type_construction.eval.domain.evaluation.value import (
    Address,
    Capture,
    DatasetRef,
    Expectation,
    File,
    Files,
    Input,
    Part,
    Parts,
    VersionRef,
)
from type_construction.eval.domain.evaluation.version import IdentifiedVersion, Version
from type_construction.eval.integration.inspect.interpreter import (
    ExecuteInterpreter,
    ReadLogInterpreter,
)
from type_construction.eval.integration.inspect.model import Arrival, ModelBinding, RecordPath
from type_construction.eval.integration.inspect.provider import LogReader, Record
from type_construction.eval.integration.inspect.task import TracedOutput
from type_construction.eval.integration.record.registry import Identification
from type_construction.eval.integration.subject.interpreter import OracleProduceInterpreter
from type_construction.eval.integration.subject.provider import Tracing

__all__ = (
    "Address",
    "Capture",
    "Case",
    "CaseId",
    "Cases",
    "Dataset",
    "DatasetLogs",
    "DatasetName",
    "DatasetRef",
    "DatasetVersion",
    "Description",
    "Digest",
    "ErrorMessage",
    "EvalConfig",
    "Execute",
    "Expectation",
    "Failed",
    "File",
    "FileText",
    "Files",
    "Finished",
    "FinishedLog",
    "IdentifiedDataset",
    "IdentifiedRun",
    "IdentifiedVersion",
    "Input",
    "InputText",
    "Invariant",
    "JudgedForm",
    "LogReader",
    "ModelBinding",
    "OracleProduce",
    "Part",
    "PartName",
    "Parts",
    "ReadLog",
    "Record",
    "RecordFolder",
    "RecordPath",
    "RecordedRun",
    "RelativePath",
    "Repetition",
    "Repetitions",
    "Residue",
    "Run",
    "RunLog",
    "RunOutcome",
    "ShortLog",
    "Shortfall",
    "SpanId",
    "Summary",
    "SystemName",
    "SystemVersion",
    "Trace",
    "TraceId",
    "Traces",
    "Tracing",
    "UnfinishedRun",
    "Version",
    "VersionRef",
    "produce",
    "producing",
    "run",
    "run_sync",
)


async def produce(state: TaskState, generate: Generate) -> TaskState:  # noqa: ARG001
    return TaskState(
        model=state.model,
        sample_id=state.sample_id,
        epoch=state.epoch,
        input=state.input,
        messages=state.messages,
        target=state.target,
        output=ModelOutput.model_validate_json(
            TracedOutput(
                trace=await OracleProduceInterpreter(
                    action=Arrival.model_validate(state, from_attributes=True).produce,
                    provider=Tracing(),
                ).interpret()
            ).output.model_dump_json()
        ),
        message_limit=state.message_limit,
        token_limit=state.token_limit,
        completed=state.completed,
        metadata=state.metadata,
        scores=state.scores,
        sample_uuid=state.uuid,
    )


@solver
def producing() -> Solver:
    return produce


async def run(config: EvalConfig, action: Run) -> RunOutcome:
    return await ReadLogInterpreter(
        action=ReadLog(
            log=await ExecuteInterpreter(
                action=Execute(run=Identification(run=action).identified),
                provider=config.record,
            ).interpret()
        ),
        provider=config.record.logs,
    ).interpret()


def run_sync(config: EvalConfig, action: Run) -> RunOutcome:
    return asyncio.run(run(config, action))
