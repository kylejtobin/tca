# Decisions

The hard calls, each with its reason and evidence. Binding until argued down with evidence; none protected because it is written here.

## D1. Inspect is the runner, the record and the sample viewer

Inspect's eval log holds a task with metadata, samples by id and epoch with input, target, output, messages and event transcript, and scores with value, explanation and metadata (`eval-logs`). That is five of the six kinds. Its eval sets retry, resume and reuse completed samples (`eval-sets`); its viewer shows a sample's transcript and scoring and bundles statically (`log-viewer`); task views declare how samples list (`task-views`); its dataframe API reads many logs at once (`dataframe`); its hooks fire on every sample and model event (`extensions-hooks`). Each of those is something this package would otherwise write.

## D2. HELM is set aside

Its run page and group tables carried their weight. Its home page is hardwired to its own hero and to Stanford's project index (`SimpleHero.tsx`, `CardGrid.tsx`); its vocabulary reaches the stranger before ours; its annotation values render as plain text that does not link (`AnnotationsDisplay.tsx`, `Preview.tsx`); its summarizer needs model registries faked for versions (`config_registry.py`); and its five files were a second record of facts Inspect's log already held. A tool earns its place by what it replaces; this one was being fought.

## D3. The solver owns the root span, and the system's spans are its children

The evaluation event "SHOULD be parented to GenAI operation span being evaluated" (`gen-ai-events.md`) and Inspect emits no OpenTelemetry (PR #2755, draft). So the solver opens `run {case.id}`, and the system's public surface is invoked inside it, in the same process, so the system's spans join through the SDK's own context and no carrier is handed across a boundary. A system under evaluation emits spans in the GenAI conventions with their content, model calls with messages and tool calls with arguments and results; the exported trace is the record's transcript (D4). A subject that exists only as a command line is a process-shaped integration: it is handed `TRACEPARENT` (OTEP 0258 names the carrier) and must parent to it, and that requirement belongs to that integration when it exists, not to the first subject.

## D4. The system runs as deployed, through its public surface; the exported trace is the transcript

The system runs natively against its own provider, exactly as it ships, invoked the way its own contract says a program invokes it: for the first subject, the agent's `run` on a config the eval constructs from the version's parts, in the eval's process, with the agent's own boundary around its commands and its check. A separate process and a sandbox image would wrap a second boundary around a system that carries one, cost the eval service the Docker socket, and need a driver inside the sandbox that is a script with a name. Inspect's sandbox agent bridge would put every model call into the log, but it does so by making the system speak to a proxy in the OpenAI format, which is not the system as deployed; an evaluation of a different system measures the wrong thing. The record is complete without it: the system's public surface returns every message of the run, so the capture writes the transcript into the sample from the run's own result, in the process, at capture time; the system's GenAI-convention spans carry the same messages and tool calls to the viewer, and the collector's export in the record root is their durable copy (D15), not the source. Inspect's `model` is still bound to the version's model part, because judges run through it and the log should say which model the run used.

## D5. Every score is written three times from one value; the log owns it

As a Score in the log, as the evaluation event on the trace, as a span annotation in Phoenix. The event's attributes name no author, so the evaluator is the event's instrumentation scope name and version, OpenTelemetry's own slot for who emitted a thing. One call writes all three; divergence is a bug in that call.

## D6. The evaluation event is written as a span event

The conventions define `gen_ai.evaluation.result` as an event, which in OpenTelemetry today is a log record carrying span context. Phoenix stores and shows span events in a span's Events tab (`SpanDetails.tsx`) and has no log ingestion endpoint (`openapi.json`). Written as a log record alone the event would be invisible in Phoenix; written as a span event it keeps the convention's name and attributes on the span it judges and is shown. The better form is both: the standard log record into the collector, so the record holds the convention's own transport, and the span event for the viewer. The span event is written first; the log record is listed, not abandoned.

## D7. One write path into Phoenix: the projection of verdicts and descriptions

Phoenix's tree badges, table columns, charts and filters read annotations, not events (release notes 2026-10-01, 2026-08-04; `TracesTable.tsx`). Without annotations the stranger sees no verdict in a trace. So the eval writes, and only writes: a project's description, one annotation configuration per criterion with its direction, and one span annotation per score with an identifier so a rescore upserts. Phoenix's own datasets and experiments features are not used; they would be a second record.

## D8. The collector maps to OpenInference; the package emits standard attributes only

Phoenix reads the project from `openinference.project.name` (`project.py`) and its views read `input.value`, `output.value`, `openinference.span.kind` (OpenInference spec); its filters read any attribute. The Phoenix pipeline's transform processor sets those three from `eval.*` on the spans that carry them (`transformprocessor/README.md`: `resource`, `span`, `spanevent` contexts), and the address stays under its own keys. The project name is a resource attribute, shared by every span a process exports in a batch, so setting it from the root span's dataset is right only while one process runs one dataset at a time; that is a constraint on the operator, stated here, until the project is set another way. The system's own spans need nothing: Phoenix converts `gen_ai.*` at ingest (release notes 2026-05-15).

## D9. One project and one log directory per dataset

The stranger comparing two versions finds both in one table and tells them apart by a column. Phoenix's project is its unit of tables, charts and annotation configs; Inspect's log directory is the scope of an eval set's progress (`eval-sets`). Versions, experiments and dataset versions are metadata inside.

## D10. The experiment is two documents beside the logs

Inspect has no pre-stated experiment with a decision; neither did HELM. `experiments/<id>.statement.json` is immutable at statement, `<id>.decision.json` at decision. Each log the experiment compares carries the id and its role in task metadata, and the statement and decision text in its description, so the viewer shows them without reading the documents.

## D11. One generated front door; the bundled viewer is the body

Inspect's bundle gives a static site over the logs but no story and no cross-version table. One static HTML file, inline CSS, no script, generated at publish from the logs and the decision documents: the story in chapters, the best version per dataset, how to read this. Every number is read from a log or a decision; every link goes to the bundle or Phoenix; a chapter renders only when it holds a decided experiment. A fourth block would make it a dashboard.

## D12. Verdicts decide; measures inform; the rule is a threshold

Binary criteria are what the method asks and what people label consistently. A one-case dataset judged all-or-nothing gives a person no gradient, so recall ratios and the like are measures, shown and never deciding. An experiment's rule is a pre-stated threshold on pass rates over stated repetitions; with five repetitions it is not a significance test and is not called one. `inconclusive` exists for when the rule cannot be applied.

## D13. An evaluator counts only after an experiment on authored verdicts kept it

For each criterion a dataset `judge-<criterion>` holds the authored reference and the authored failing examples with their verdicts. The evaluator version runs on it as a subject; the statement decides on `agrees-on-fail` with no loss on `agrees-on-pass`, because a missed failure is the costly error. A criterion may name only a kept evaluator. People author references, criteria and examples; nobody grades a run; Phoenix's `HUMAN` kind is never written. A person who disagrees with a verdict adds an authored example, which may re-validate and replace the evaluator.

## D14. The judged form's history is derived from the transcript

The README asks how the type list changed file by file across the run. The exported trace holds every tool call with its arguments; the capture step derives, after each write, the type list's change, and writes the history on the capture span and in sample metadata. The system is not asked to report it.

## D15. Artifacts and exported traces live beside the logs; the trace itself lives in the sample

The captured workspace is what evaluators read later and what a person opens when the judged form is not enough. It is kept as the directory the system left, under `logs/<dataset.name>/artifacts/<address>/workspace/`, not inside the log, because the log is Inspect's format and a workspace is not a sample field, and under the dataset's name so a stranger browsing the record can tell whose it is; the oracle leaves none. The collector's file exporter writes the trace stream it receives under `traces/` in the record root, because Phoenix is a viewer and the record must not depend on it. The eval's own record of a repetition, its address, the ids of the span it opened and the capture, is the sample's output metadata in the log, written by Inspect when the solver returns and read back from there; a trace is found in the exported stream by the ids the sample holds (D22).

## D16. Vocabulary is taught where the stranger meets it

Inspect says task, sample, epoch, model; Phoenix says project, trace, annotation. The translation is written into the log's description, the project's description and the front door's "How to read this", and nowhere that the stranger has to find first.

## D17. The log is append-only, not immutable

Inspect's log takes added scores with their history and provenance (`eval-logs`: score edits, `log_updates`). A rescoring appends a score carrying its evaluator version and never overwrites one. Statements, decisions, artifacts and traces are written once. "Immutable" in this package means that: nothing issued is ever changed or lost, and additions say who added them.

## D18. The eval's environment is its own; the agent's is not touched

The eval runs as its own service from the workspace image, with the record root mounted and bubblewrap present for the subject's boundary, beside its own collector and Phoenix. The system under evaluation runs inside the eval's process through its public surface, in a workspace the eval constructed in the record root, and sees the eval's collector through the process's own SDK. The repository's `dev` service and Jaeger are the agent's development environment: the README's rule that the collector is the one endpoint governs what the eval runs, not how the agent is developed, and the rule that a system's own record is never read here cuts the other way too. Nothing of the eval reaches into them.

## D19. The run's root span is acquired under the interpreter's one `async with`

The skill: "An `interpret`'s expression may stand within the one `async with` that acquires the capability it uses, which is then released on every path." The span is such a capability: acquired by the interpreter of the production, current for the production's whole lifetime so every span the system emits is its child, released when the production ends, whether it succeeded or raised. OpenTelemetry's span is a synchronous context manager and offers no asynchronous one, and the smell check admits no `with` inside an `interpret`, so the standard library's `AsyncExitStack` is the `async with` that enters the span and closes it on every path: the one place the library's form and the skill's differ, held by a standard-library shim rather than by a rule changed or a library entered. For a system that produces before its capture exists, the judged form cannot be an attribute of the root span, because attributes are given at acquisition, so it will be carried by a zero-length child span, `capture workspace`, opened with the capture's attributes once the capture exists; the oracle's capture is known from the expectation before the span opens, so its root span carries the address, the input and the output, and it is the one span of its repetition.

## D20. Identity by content is the record integration's derivation

A digest is computed by a library the domain does not import, and identity by content is the record's act: a dataset's version is the digest of its cases, a version's identity the digest of its name, its entrypoint and its parts, so the same parts invoked two ways are two systems. Both are derived by the record integration from the content alone, with nothing written: the registry that once filed them was a second record of what every log already holds (D2, D22). The domain holds `IdentifiedDataset` and `IdentifiedVersion`, the thing with the identity the record gave it, and a `IdentifiedRun` is made of those, because an address needs identities the record issued; a program states a `Run` of content, naming a version or the dataset's own `Oracle`, and the record derives the rest.

## D21. The address is the run's baggage, and only the root span carries it

A span's attributes are a mapping, and the skill admits no dict as an argument, so the eval cannot hand attributes at a span's start. Asked what the address is to a trace, it is context of the run. The OpenTelemetry baggage API sets it one key at a time and returns a context; the root span is opened under that context, and the deployment's baggage span processor copies the context's baggage onto the span it starts. Because the context is given to the span's start and not attached as current, the system's child spans do not inherit it and nothing of the eval rides out in the system's requests to its provider; Phoenix's trace table and trace filters read the root span's attributes, which is all the product needs. The capture span carries the judged form the same way, under a context built from the current one. The processor is `opentelemetry-processor-baggage`, declared by the eval because its runtime needs it; it ships no type stubs, which costs one marked import where a process configures it, and it pins the eval to the SDK's release line.

## D22. The eval writes no file of its own

Every write the eval once made for itself, the registry's pages, the oracle's placed workspace and a `trace.json` beside it, was an effect with no reply, and an effect with no reply has no fact to construct: the skill admits `None` only where a value is handed to a library, never held, and holding a write's nothing to sequence it inside one expression evades the one-expression rule's purpose. Asked what the record's reply is, the answer was already D1: the log Inspect writes and returns is the record. So the sample carries its case in, as text in its metadata, and its trace out, as its output's metadata; the oracle's production is its expectation standing as the production, with no archive; identity is derived (D20); and a version's display name is read in the log's description, where a stranger meets the version, until the listing (G) reads every log. The one write the eval composes is Inspect's, in the interpreter that acquires it, whose reply is the log's header, read into the run's log, finished or short with the runner's word for the shortfall kept by reference, which decides whether the run is recorded whole or unfinished with what each repetition left. Inspect calls its solver with positional arguments, which an `interpret` cannot take, so the solver is a callback of the composition root, registered with Inspect under its name as Inspect's own decorator registers solvers, and the acquiring interpreter names it back to Inspect by that name through `SolverSpec`, the library's own reference to a registered solver; the log records which solver ran. The solver reads no configuration: the tracer is the eval's own scope, which nothing deploys, and the output of a production no model generated names no model, the log naming the model the run was bound to. The sample needs no document of its case: Inspect carries the case's input and target natively, and the oracle's production needs nothing else; the solver hands the state back with its output set and every other field as Inspect gave it. A repetition that produced nothing is read back at its address, so an unfinished run says what each repetition the runner reached left. The deployment names the record once, as one provider holding the root and the model, from which the runner and the reader of logs derive.
