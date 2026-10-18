# Schema

The six kinds as data, the address, and the slot that carries every field in the trace, in the log and in Phoenix's projection, each cited to its owner's contract. A field no screen or operator call demands is not here.

Contracts opened: OpenTelemetry GenAI conventions (`open-telemetry/semantic-conventions-genai`: `docs/gen-ai/gen-ai-events.md`, `docs/gen-ai/gen-ai-agent-spans.md`); OpenTelemetry Collector `transformprocessor/README.md`; OTEP 0258; Inspect docs (`eval-logs`, `datasets`, `tasks`, `sandboxing`, `log-viewer`, `task-views`, `eval-sets`, `extensions-hooks`, `dataframe`, `scoring-policy`, `model-graded`); Phoenix (`schemas/openapi.json`, `src/phoenix/utilities/project.py`, `js/app/src/pages/`); OpenInference `spec/semantic_conventions.md`; Pydantic AI `integrations/logfire` for its GenAI-convention instrumentation.

## Conventions

- Digest: SHA-256 over a canonical serialization, assigned by the record when it writes the entry (D20), stored whole, shown as eight characters.
- Time: RFC 3339 UTC.
- Immutability: written once under a name that includes its digest or address; a correction is a new record naming the one it supersedes.
- Every kind has `description`, markdown, written for the stranger; it is the text the storyboards show.

## Address

```
Address { dataset: {name, version: Digest}, case: CaseId, system: {name, version: Digest}, repetition: int ≥ 1 }
```

| Where | Form | Contract |
|---|---|---|
| eval-owned spans | `eval.dataset.name`, `eval.dataset.version`, `eval.case.id`, `eval.system.name`, `eval.system.version`, `eval.repetition`, `eval.experiment.id` | custom namespace |
| Phoenix | the same keys as attributes of the root span, copied from the run's baggage (D21); Phoenix filters read `attributes["eval.…"]` | Phoenix filter expressions |
| Inspect log | `Task.metadata` = dataset, system, experiment; task args `dataset_version`, `system_version` so eval sets tell runs apart | `tasks`: metadata "recorded in the eval log"; `eval-sets`: task identity from `@task` arguments |
| Inspect sample | `Sample.id = case.id`; `epoch = repetition`; `Sample.input` = the case's input; `Sample.target` = the expected judged form; `Sample.metadata` = dataset ref, version ref; `Sample.output.metadata` = the trace | `datasets`: `id`, `metadata`; `eval-logs`: samples addressed by id and epoch |
| artifacts | `logs/<dataset.name>/artifacts/<dataset.version>/<case.id>/<system.name>@<system.version>/<repetition>/`, holding `workspace/` as the system left it | this package |
| record root | `RecordPath`, a domain scalar: the one directory the deployment names; every system that reaches it is derived from that statement | config |

## Dataset

```
Dataset  { name, description, criteria: list[Criterion], cases: list[Case] }            version: assigned by the record as the digest of its cases
IdentifiedDataset { dataset, ref: DatasetRef }                                       the dataset with the identity the record gave it
Criterion { id, description, kind: verdict | measure, evaluator: VersionRef, failing_example: ExampleRef, passing_example: ExampleRef }
```

| Field | Trace | Log | Phoenix |
|---|---|---|---|
| name, version | `eval.dataset.*` | task name = `name`; `Task.metadata.dataset` | project name |
| description | — | `Task.description` first sentence | project `description` (`PUT /v1/projects/{id}`) |
| criteria[].id | `gen_ai.evaluation.name` | scorer name = criterion id | annotation `name` |
| criteria[].description | — | `Task.description`; `ViewerConfig` score labels | annotation config `description` |
| criteria[].kind | — | verdict: value 1/0 with labels pass/fail; measure: value 0..1 | CATEGORICAL `{pass: 1, fail: 0}` or CONTINUOUS 0..1, `optimization_direction: MAXIMIZE` |

A new case is a new dataset version; an experiment pins the version.

## Case

```
Case { id, description, input: Input, expectation: Expectation, tags }
Input { text, files: dict[path, Digest], prior: TraceRef | None }     prior: a recorded run's prefix the eval replays before the system acts; step cases
Expectation { judged_form: str, reference: dict[path, Digest], extra: dict }   never reaches the system
```

| Field | Trace | Log | Phoenix |
|---|---|---|---|
| input.text | root `eval.input` | `Sample.input` | `input.value` |
| input.files | `prepare workspace` attributes | placed in the workspace by the record (D18) | — |
| input.prior | `prepare workspace` attribute `eval.prior.trace_id` | `Sample.metadata.prior` | metadata |
| expectation.judged_form | evaluator span input digest only | `Sample.target` | — |
| expectation.reference, extra | evaluator span input digest | `Sample.metadata.expectation` | — |

For the first subject: `input.text` is the problem statement; `expectation.judged_form` is the reference program's type list by layer and file; `reference` is its files by digest; `extra` holds the framing and the list as JSON.

## Version

```
Version { name, display, description, role, entrypoint: Entrypoint, parts: Parts, lineage: Lineage }    identity: assigned by the record as the digest of name, entrypoint and parts
Part    { name, digest, summary }
Lineage: the version this one derives from, at most one; the first of its name has none
Entrypoint: a closed vocabulary naming how the eval invokes the system; the integration answering to a name is the composition root's to choose
IdentifiedVersion { version, ref: VersionRef }
```

A version is the whole system; an experiment varies exactly one part. For an agent the parts are at least model, skills, check, prompt, tools, image, compaction, entrypoint. For the oracle, the reference's files. For a judge, model and prompt.

| Field | Trace | Log | Phoenix |
|---|---|---|---|
| name, version | `eval.system.*` | `Task.metadata.system`; task arg `system_version` | metadata |
| model part | the system's own `gen_ai.request.model` | `eval(model=…)` names it; the system calls its provider itself (D4) | converted by Phoenix |
| parts, parent, description | `prepare workspace` `eval.part.<name>` | `Task.metadata.parts`, `Task.description` | — |

## Trace

```
Run        { dataset: IdentifiedDataset, version: IdentifiedVersion, repetitions }
Assignment { dataset: DatasetRef, system: VersionRef, case: CaseId }   what a sample carries, by name; the repetition is the epoch; the record reads the case by this address
LoggedRun     { run, log: RelativePath }                             the runner is done; traces not yet read back
Produce    { address, case }                                      one repetition's production
Trace      { address, trace: TraceId, span: SpanId, capture }     times live on the span and in the log, not here
Capture    { artifact, output, judged_form, diff }                history is listed above, for the capture crossing of a real subject
RecordedRun   { run, traces, log }
```

| Span | Name | kind | Attributes |
|---|---|---|---|
| root | `run {case.id}` | CHAIN | address, `eval.input`; attributes are given at acquisition, so the output is not here (D19) |
| 1 | `prepare workspace` | CHAIN | `eval.part.*`, files placed |
| 2 | the system's root, e.g. `invoke_agent tca-agent` | the system's | GenAI conventions (`gen-ai-agent-spans.md`); Pydantic AI emits them under conventions 1.37.0 |
| 3 | `capture workspace` | CHAIN | zero-length, opened once the capture exists: `eval.output` = the judged form and diff, `eval.artifact.path` |
| 4..n | `evaluate {criterion}` | EVALUATOR | `eval.evaluator.name`, `.version`, `.validated_by`, `eval.judged.trace_id` |

The solver opens the root span under a context carrying the address as baggage (D21) and invokes the system's public surface inside it, in the same process, so the system's spans are its children (D3). A process-shaped subject would instead be handed `TRACEPARENT` by its own integration.

| Capture field | Log | Phoenix |
|---|---|---|
| artifact | `Sample.metadata.artifact` path; archive beside the logs (D15) | root `eval.artifact.path` |
| judged_form, diff, history | `Sample.metadata`; `Score.answer` carries the summary | root and capture `eval.output` |
| final_output | `Sample.output` | — |
| transcript | written into the sample by the capture step from the exported trace (D4) | the system's spans |
| trace_id | `Sample.metadata.trace` {id, url, export path} | — |
| export | the collector's file exporter writes the trace stream under `traces/` in the record root; the sample's output metadata holds the ids and the capture (D15, D22) | — |

## Score

```
Score { address, trace_id, criterion, evaluator: VersionRef, kind, label: pass | fail | None, value: float, confidence: float | None, explanation, scored_at }
```

Written three times from one value (D5):

| Slot | Fields | Contract |
|---|---|---|
| Log | scorer named by criterion: `Score(value, answer = judged form summary, explanation, metadata = {evaluator, evaluator_version, kind, label, confidence, validated_by, trace_id, scored_at})` | `eval-logs`: Score `value`, `explanation`, `metadata`; one scorer per criterion |
| Trace | span event `gen_ai.evaluation.result` on the root: `gen_ai.evaluation.name`, `.score.value`, `.score.label`, `.explanation`; instrumentation scope = evaluator name and version | `gen-ai-events.md`; written as a span event, see D6 |
| Phoenix | `POST /v1/span_annotations`: `name` = criterion, `annotator_kind` = CODE or LLM, `result{label, score, explanation}`, `metadata` as the log's, `identifier = "{address}/{criterion}/{evaluator_version}"`, `span_id` = root | `openapi.json` `SpanAnnotationData` |

`HUMAN` is never written.

## Experiment

```
Statement { id, title, description, dataset: DatasetRef, baseline: VersionRef, candidates: list[VersionRef], change: {part, from, to}, decides: CriterionId, guardrails: list[CriterionId], repetitions: int, rule: {min_gain, max_guardrail_loss}, stated_at, stated_by }
Decision  { statement: Digest, results: dict[VersionRef, dict[CriterionId, {passes, n, mean}]], decision: kept | rejected | inconclusive, reason, decided_at, decided_by }
```

The rule is a pre-stated threshold on pass rates over the stated repetitions, not a test of significance; `inconclusive` is the decision when the repetitions stated were not all completed or the rule's inputs are missing.

| Slot | Contract |
|---|---|
| `logs/<dataset.name>/experiments/<id>.statement.json`, `<id>.decision.json` | this package (D10) |
| `Task.metadata.experiment` = id and role (baseline, candidate) on each log it compares; the statement and decision text in `Task.description` | `tasks` |
| front door story line | generated from the decision |
| Phoenix | `eval.experiment.id` on every span of the runs |

## Evaluator

A `Version` with `role: evaluator`, validated by an `Experiment` on dataset `judge-<criterion>` whose cases are the authored reference and the authored failing examples with their verdicts as targets; criteria `agrees-on-pass` and `agrees-on-fail`; the statement decides on `agrees-on-fail` with no loss on `agrees-on-pass`. A criterion's `evaluator` may name only a version whose validation decision is `kept`. Judges use Inspect's model-graded scoring with a grader role and may use a panel (`model-graded`); the grader's votes stay in score metadata.

## Site narrative

One content file in this package, rendered by the front door and never a kind: `title`, `question`, `chapters: list[{id, title, description, experiments: list[ExperimentId]}]`. An experiment belongs to a chapter by being listed, not by a field on its immutable statement.

## Operator calls

| Call | Takes | Returns | Writes |
|---|---|---|---|
| `state_experiment` | Statement fields | id | statement document |
| `run` | Dataset content, repetitions (a Version or the Oracle once a second system exists), experiment id | RunOutcome: recorded with its run, log and traces, or unfinished with its shortfall | the log (Inspect `eval()`), with each sample's input, target and trace; artifacts by the system; traces via the collector; annotations |
| `score` | log path or address, criteria | scores | scores appended to the log with their evaluator version, events, annotations; rescoring reads the record only and never overwrites a score (D17) |
| `read_results` | experiment id | results | — |
| `decide` | experiment id | Decision | decision document |
| `publish` | — | site path | `inspect view bundle`, `site/index.html` |

`run` is an Inspect eval set over one task: a sample per case carrying its input, its target and its assignment; `epochs` = repetitions; the solver, a callback of the composition root, opens the root span under the address's baggage, invokes the production, and returns the trace as the sample's output metadata; scorers are this package's evaluators; limits per sample; hooks carry the annotations and events out; retries and resumption from the log directory (`eval-sets`, `extensions-hooks`).

## Storyboard to field

| Screen | Fields |
|---|---|
| P1 | dataset.name |
| P2 | dataset.description, case.input.text, capture.judged_form summary, scores, address, experiment id, criterion kind |
| P3 | span names and kinds, score labels |
| P4 | input, judged form, address, sample url, artifact path, every Score field, evaluator version |
| P5 | capture.history, evaluator name, version, validated_by, judged trace id |
| V1 | Task.description, Task.metadata, model part, epochs, per-criterion metrics |
| V2 | sample id, epoch, input, target, scores, ViewerConfig |
| V3 | Score fields, target, answer |
| V4 | sample metadata: address, trace, artifact, judged form, diff, history; transcript |
| S0 | decisions, best version per dataset with pass rates, six kinds' first examples, site narrative |
