"""A program crosses the eval as its operator would: it hands `run` a dataset's content and
gets back what became of the run of the dataset's own oracle; the record then holds one
Inspect log a person can open, each sample carrying its case in and its trace out, and one
span per repetition on the collector."""

import asyncio
from pathlib import Path

import pytest
from inspect_ai.log import read_eval_log
from inspect_ai.solver import Generate, TaskState
from opentelemetry import trace
from opentelemetry.processor.baggage import (  # pyright: ignore[reportMissingTypeStubs]
    ALLOW_ALL_BAGGAGE_KEYS,
    BaggageSpanProcessor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import ValidationError

import type_construction.eval
from type_construction.eval import (
    Capture,
    Case,
    CaseId,
    Cases,
    Dataset,
    DatasetName,
    Description,
    Digest,
    ErrorMessage,
    EvalConfig,
    Execute,
    Expectation,
    Failed,
    File,
    Files,
    FileText,
    Finished,
    FinishedLog,
    IdentifiedRun,
    Input,
    InputText,
    JudgedForm,
    Part,
    PartName,
    Parts,
    ReadLog,
    RecordedRun,
    RelativePath,
    Repetition,
    Repetitions,
    Residue,
    Run,
    Shortfall,
    ShortLog,
    SpanId,
    Summary,
    SystemName,
    Trace,
    TraceId,
    Traces,
    UnfinishedRun,
    run_sync,
)
from type_construction.eval.integration.record.identity import RunIdentity, VersionIdentity
from type_construction.eval.integration.record.interpreter import (
    ExecuteInterpreter,
    ReadLogInterpreter,
)
from type_construction.eval.integration.record.model import (
    ErroredSample,
    NoCompletion,
    SampleError,
    SampleMetadata,
    UnproducedOutput,
)
from type_construction.eval.integration.record.task import Log, LogContents

EXPORTED = InMemorySpanExporter()
PROVIDER = TracerProvider()
PROVIDER.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
PROVIDER.add_span_processor(SimpleSpanProcessor(EXPORTED))
trace.set_tracer_provider(PROVIDER)

JUDGED = JudgedForm(
    "layer  kind             name   file\nScalar semantic scalar Toss   domain/coin/type.py\n"
)
REFERENCE = Files(
    (
        File(path=RelativePath("domain/coin/type.py"), text=FileText("class Toss: ...\n")),
        File(path=RelativePath("README.md"), text=FileText("# coin\n")),
    )
)
DATASET = Dataset(
    name=DatasetName("coin"),
    description=Description("A coin toss modeled as a program."),
    cases=Cases(
        (
            Case(
                id=CaseId("coin-toss"),
                description=Description("Model a coin toss."),
                input=Input(text=InputText("Model a coin toss as a program.")),
                expectation=Expectation(judged_form=JUDGED, files=REFERENCE),
            ),
        )
    ),
)


@pytest.fixture
def config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> EvalConfig:
    monkeypatch.setenv("EVAL_RECORD__ROOT", str(tmp_path))
    monkeypatch.setenv("EVAL_RECORD__MODEL", "mockllm/model")
    return EvalConfig()  # pyright: ignore[reportCallIssue]


def test_one_call_runs_the_oracle_and_the_log_is_the_record(
    config: EvalConfig, tmp_path: Path
) -> None:
    outcome = run_sync(config, Run(dataset=DATASET, repetitions=Repetitions(2)))

    recorded = outcome.root
    assert isinstance(recorded, RecordedRun)
    assert recorded.run.dataset.dataset == DATASET
    oracle = recorded.run.version.version
    assert oracle.parts.root[0].digest.root == recorded.run.dataset.ref.version.root
    assert recorded.log.root.startswith("logs/coin/")
    assert len(recorded.traces.root) == 2
    assert {t.address.repetition.root for t in recorded.traces.root} == {1, 2}
    for recorded_trace in recorded.traces.root:
        assert recorded_trace.address.dataset == recorded.run.dataset.ref
        assert recorded_trace.address.system == recorded.run.version.ref
        assert recorded_trace.capture.judged_form == JUDGED

    log = read_eval_log(str(tmp_path / recorded.log.root))
    assert log.status == "success"
    assert log.eval.task == "coin"
    assert log.samples is not None
    assert len(log.samples) == 2
    for sample in log.samples:
        assert sample.id == "coin-toss"
        assert sample.input == "Model a coin toss as a program."
        assert sample.target == JUDGED.root
        assert sample.output.completion == JUDGED.root
        assert sample.metadata["system"]["name"] == "reference"
        assert sample.output.metadata is not None
        assert Trace.model_validate(sample.output.metadata) in recorded.traces.root

    again = run_sync(config, Run(dataset=DATASET, repetitions=Repetitions(1)))
    assert isinstance(again.root, RecordedRun)
    assert again.root.log != recorded.log
    assert again.root.run.version == recorded.run.version
    assert len(list((tmp_path / "logs" / "coin").glob("*.eval"))) == 2


def test_each_repetition_is_one_root_span_carrying_the_address_input_and_output(
    config: EvalConfig,
) -> None:
    EXPORTED.clear()
    outcome = run_sync(config, Run(dataset=DATASET, repetitions=Repetitions(2)))
    assert isinstance(outcome.root, RecordedRun)

    spans = EXPORTED.get_finished_spans()
    roots = [s for s in spans if s.name == "run coin-toss"]
    assert len(roots) == len(spans) == 2
    for root in roots:
        assert root.parent is None
        assert root.attributes is not None
        assert root.attributes["eval.dataset.name"] == "coin"
        assert root.attributes["eval.system.name"] == "reference"
        assert root.attributes["eval.span.kind"] == "CHAIN"
        assert root.attributes["eval.input"] == "Model a coin toss as a program."
        assert root.attributes["eval.output"] == JUDGED.root
        assert root.instrumentation_scope is not None
        assert root.instrumentation_scope.name == "type-construction-eval"
    assert {
        (format(r.context.trace_id, "032x"), format(r.context.span_id, "016x"))
        for r in roots
        if r.context
    } == {(t.trace.root, t.span.root) for t in outcome.root.traces.root}


async def fall_over(state: TaskState, generate: Generate) -> TaskState:
    message = "the system fell over"
    raise RuntimeError(message)


def test_a_run_whose_system_fails_is_logged_short_and_read_as_unfinished(
    config: EvalConfig, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(type_construction.eval, "produce", fall_over)
    registered = RunIdentity(run=Run(dataset=DATASET, repetitions=Repetitions(1))).identified
    log = asyncio.run(
        ExecuteInterpreter(action=Execute(run=registered), provider=config.record).interpret()
    )
    assert isinstance(log.entry, ShortLog)
    assert log.run == registered
    assert log.entry.ending == Shortfall("error")
    assert read_eval_log(str(tmp_path / log.log.root)).status == "error"

    outcome = asyncio.run(
        ReadLogInterpreter(action=ReadLog(log=log), provider=config.record.logs).interpret()
    )
    assert isinstance(outcome.root, UnfinishedRun)
    assert outcome.root.run == registered
    assert outcome.root.log == log.log
    assert outcome.root.ending == Shortfall("error")
    assert outcome.root.left == (
        Residue(
            Failed(
                address=registered.addresses[0],
                error=ErrorMessage("RuntimeError('the system fell over')"),
            )
        ),
    )


def test_a_finished_log_with_a_repetition_that_did_not_produce_is_refused() -> None:
    registered = RunIdentity(run=Run(dataset=DATASET, repetitions=Repetitions(1))).identified
    with pytest.raises(ValidationError):
        Log.model_validate(
            LogContents(
                log=FinishedLog(
                    run=registered, log=RelativePath("logs/coin/x.eval"), ending=Finished.FINISHED
                ),
                samples=(
                    ErroredSample(
                        id=CaseId("coin-toss"),
                        epoch=Repetition(1),
                        metadata=SampleMetadata(
                            dataset=registered.dataset.ref, system=registered.version.ref
                        ),
                        output=UnproducedOutput(completion=NoCompletion("")),
                        error=SampleError(message=ErrorMessage("x")),
                    ),
                ),
            )
        )


def test_a_run_is_of_its_dataset_s_own_oracle_and_no_other_version() -> None:
    registered = RunIdentity(run=Run(dataset=DATASET, repetitions=Repetitions(1))).identified
    other = VersionIdentity(
        version=registered.version.version.model_copy(update={"name": SystemName("other")})
    ).identified
    with pytest.raises(ValidationError):
        IdentifiedRun(dataset=registered.dataset, version=other, repetitions=Repetitions(1))


def test_a_recorded_run_holds_a_trace_at_each_address_the_run_names_and_no_other() -> None:
    registered = RunIdentity(run=Run(dataset=DATASET, repetitions=Repetitions(1))).identified
    elsewhere = Trace(
        address=registered.addresses[0].model_copy(update={"repetition": Repetition(2)}),
        trace=TraceId("a" * 32),
        span=SpanId("b" * 16),
        capture=Capture(judged_form=JUDGED),
    )
    with pytest.raises(ValidationError):
        RecordedRun(
            run=registered, log=RelativePath("logs/coin/x.eval"), traces=Traces((elsewhere,))
        )


def test_the_record_refuses_what_its_types_refuse() -> None:
    with pytest.raises(ValidationError):
        RelativePath("../escape")
    with pytest.raises(ValidationError):
        Parts(
            (
                Part(name=PartName("model"), digest=Digest("0" * 64), summary=Summary("a")),
                Part(name=PartName("model"), digest=Digest("1" * 64), summary=Summary("b")),
            )
        )
    with pytest.raises(ValidationError):
        Files(
            (
                File(path=RelativePath("a.py"), text=FileText("")),
                File(path=RelativePath("a.py"), text=FileText("x")),
            )
        )
    with pytest.raises(ValidationError):
        Case(
            id=CaseId("coin-toss"),
            description=Description("A case placing one path twice."),
            input=Input(
                text=InputText("x"),
                files=Files((File(path=RelativePath("README.md"), text=FileText("")),)),
            ),
            expectation=Expectation(judged_form=JUDGED, files=REFERENCE),
        )
