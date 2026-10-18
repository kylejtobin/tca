# Map

How one address partitions the corpus into the two tools, what each tool's first screen shows, how every record reaches its neighbours, and where the files live.

## The address

| Part | Field | Example | Identity |
|---|---|---|---|
| dataset | `dataset.name` | `registrar` | a name chosen once, never reused |
| dataset version | `dataset.version` | `d3a1f0c2` | digest of the dataset's cases |
| case | `case.id` | `domain-registration` | unique within the dataset |
| system version | `system.name@system.version` | `tca-agent@7f0c9e41` | digest of the version's parts |
| repetition | `repetition` | `2` | 1-based |

String form: `registrar@d3a1f0c2/domain-registration/tca-agent@7f0c9e41#2`. Digests are stored whole and shown as eight characters.

## How the corpus partitions

| Kind | Inspect (the record and the sample viewer) | Phoenix (the trace viewer) | Front door |
|---|---|---|---|
| Dataset | one log directory `logs/<dataset.name>/`; the task is named by the dataset | one project named `dataset.name` | one row under "The best now" |
| Case | one sample, `id = case.id` | trace metadata `case.id` | — |
| Version | one log per (dataset version, system version); `system.*` in log metadata; the `model` field is the version's model part | trace metadata `system.*` | one line per turning point |
| Trace (one run) | one sample at one epoch: input, target, output, messages, events | one trace; root span `run <case.id>` | — |
| Score | one `Score` per criterion on the sample: value, explanation, metadata | one span annotation on the root per criterion; one evaluation event | a pass rate per criterion |
| Experiment | `experiments/<id>.statement.json`, `.decision.json` beside the logs | trace metadata `experiment.id` | one line in the story |
| Evaluator | a version like any other; its validation logs live under `logs/judge-<criterion>/` | project `judge-<criterion>` | named on the validation line |

One directory holds every log ever made on one dataset; one project holds every trace. A stranger comparing two versions finds both in one table and tells them apart by a column, never by hunting across containers.

## Two vocabularies, taught where they are met

Inspect says task, sample, epoch, model, score. Phoenix says project, trace, span, annotation. The stranger meets those words first. The translation is written into the places they land:

- The log's `description`, shown in the viewer's header: "Dataset registrar@d3a1f0c2 run by version tca-agent@7f0c9e41. Each sample is a case; each epoch is a repetition; scores are criteria."
- The Phoenix project's description: "Each trace is one run of one version on one case. Each annotation is one criterion's verdict with its reason."
- The front door's "How to read this" block, which names the six kinds and gives each tool's word for them.

## Phoenix

**Projects page.** Names, trace counts, median latency, last updated (`js/app/src/pages/projects/ProjectsPage.tsx`). Names are dataset names; `judge-` names sort together.

**Project page.** Description at the top. Traces table with status, kind, name, input, latency and one column per annotation name (`js/app/src/pages/project/TracesTable.tsx`). Name reads `run <case.id>`; input is the case's input; the annotation columns are the criteria; the address is on the root span's attributes. Above, one chart per criterion plotting pass rate over time (release notes 2026-08-04). Filters the description names: `attributes["eval.system.version"] == "…"`, `attributes["eval.experiment.id"] == "…"`, `annotations["check-passes"].label == "fail"`.

**Trace page.** The root row carries the criteria badges, unfavorable first (release notes 2026-10-01). Four chapters:

```
run domain-registration                    [check-passes fail] [structure-matches fail] [types-recalled pass] +2
├── prepare workspace                      parts placed, by digest
├── invoke_agent tca-agent                 the system's own spans: model calls, tool calls, in order
├── capture workspace                      output: the judged form, its history file by file, the diff
└── evaluate <criterion>  × n              output: the verdict; a judge's model call is a child
```

The root span's Info tab shows the input; Attributes holds the address; Events lists the evaluation events; Annotations lists the verdicts with kind CODE or LLM and the explanation (`js/app/src/pages/trace/SpanDetails.tsx`). The judged form and the diff are the output of the `capture workspace` span, opened once the capture exists (D19). The eye lands on the badges, then the long chapter, then the capture's output: the shape, then the verdict, then the evidence.

**To the log viewer.** Root attribute `eval.sample.url` is the sample in the bundled viewer. Phoenix renders it as text; the stranger copies it.

## The log viewer

Inspect's viewer, bundled with the logs as a static directory (`inspect view bundle`; log viewer docs). It lists the logs; a log shows its samples with the columns, score labels and colour scales the task declared (task views, `ViewerConfig`); a sample shows its Transcript, Messages, Scoring and Metadata tabs; samples filter by score and sort by score or across epochs.

**Logs list.** One log per (dataset version, system version), each headed by its description.

**Samples list.** One row per case and epoch: id, epoch, the input's first line, the target's summary, one column per criterion with pass or fail. Filter to failures; sort across epochs.

**Sample.** Scoring: for each criterion, what was compared and the explanation. Metadata: the address, the trace id and Phoenix URL, the artifact path, the judged form and its diff. Transcript: every model call and tool call the system made, in order, written in from the exported trace. Messages: the raw history, last.

**To Phoenix.** Sample metadata `trace.url`. Text; copied.

## The front door

`site/index.html`, one static file generated from the logs and the experiment documents. Three blocks:

1. **The story.** Title, the one-line question, then chapters in order, each a paragraph and its experiments as one line each: kept or rejected, the change, the deciding criterion's numbers, links to the log and the Phoenix filter. Kept and rejected have the same fields.
2. **The best now.** One row per dataset: the current best version, pass rate per criterion, link to its log and its Phoenix project. The criteria it fails are in the same row as the ones it passes.
3. **How to read this.** The six kinds, two sentences each, each with a link to its first live example, and each tool's word for it.

A chapter renders only when it holds at least one decided experiment.

## Cross-links

| From | To | How | Limit |
|---|---|---|---|
| front door | a log, a Phoenix project, an experiment's runs | links | none |
| samples list | a sample | click | none |
| sample | every verdict, reason, the expectation, the output, the diff | on the page | none |
| sample | its trace | `trace.url` in metadata | copied |
| trace root | its sample | `eval.sample.url` attribute | copied |
| trace | its experiment's other runs | project filter by `experiment.id` | typed |
| experiment | its runs | the two logs it names | links from the front door |
| criterion | its meaning, evaluator, validation | the log description names the criteria; the evaluator's validation log is under `judge-<criterion>` | one hop |

## The record on disk

One directory, the record root. Everything the eval knows is a file in it, written once by Inspect, by the collector or by a system in its workspace; the eval writes no file of its own (D22). The whole directory is what is published and what a program reads. No database: a derived index may be rebuilt from it when reading gets slow, and thrown away without loss.

```
logs/
  registrar/
    2026-10-17T10-12-03_registrar_<id>.eval       dataset d3a1f0c2 × tca-agent@7f0c9e41, all cases, all epochs; each sample carries its case and its trace
    2026-10-17T11-02-41_registrar_<id>.eval       dataset d3a1f0c2 × reference@a91b2c3d, the oracle
    artifacts/d3a1f0c2/domain-registration/tca-agent@7f0c9e41/2/   workspace/ as the system left it
    traces/                                        the trace stream as the collector's file exporter writes it
    experiments/
      e-2026-10-17-compaction.statement.json
      e-2026-10-17-compaction.decision.json
  judge-framing/                                   an evaluator's validation dataset
site/
  index.html                                       the front door, generated
  view/                                            inspect view bundle: viewer + logs
```

Inspect names its log files; the address lives in each sample's metadata and in the trace its output carries, and the dataframe API finds a run by it. Artifacts, exported traces and experiment documents sit beside the logs, under the same address.

## Naming rules

- Span names are low in cardinality: `run <case.id>`, `prepare workspace`, `capture workspace`, `evaluate <criterion>`. Versions, repetitions and experiments are attributes.
- A project and a log directory are named by the dataset. A validation dataset is `judge-<criterion>`.
- A criterion id reads as a pass condition: `check-passes`, `types-recalled`. Its description is the sentence a stranger tests a run against.
- A version is `system.name@digest`; its display name adds the phrase that says what differs from its parent.
- An experiment id is `e-<date>-<slug>`; its title is the change in five words.
- The oracle version of a dataset is `reference@<digest>`.
