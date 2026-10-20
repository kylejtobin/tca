# type-construction-eval

An evaluation architecture. It exists so that a person or a program can know, with trust, whether a change to a system made that system better at a body of work, and can open the answer down to one run, one criterion and one evaluator's reason. The bar is the best evaluation architecture there is, built from what the field has learned, not from this repository's habits.

This package is built under Type Construction Architecture because everything in this repository is. TCA governs how its code is written. TCA does not define what evaluation is, and the first system evaluated here, the TCA agent, is one subject among many. If a sentence in the generic part of this document needs a TCA word to make sense, the design has been captured by its first subject, and the sentence is wrong.

## Before reading further

You are reading this with no context, as the sessions that wrote it once did. Three of them lost the thread in the same way: they reached for the nearest authoritative text, the skill, the agent, the file in front of them, and restated it with conviction instead of asking what evaluation itself needs. Each time the design shrank to a scoring harness for one agent. A fourth kept the thread and overbuilt: four tools where two carry the work. So, while you read and after:

- When a question is about what evaluation needs, ask what evaluation is and what the field has learned. Ask what TCA says only when writing code.
- A claim about a standard, a library or a tool is made with its contract open, and the source named. Unread means unclaimed.
- A decision that can be made is made, here, now, with its reason. "Later," "out of scope" and "not eval" are not decisions.
- When an easy true answer and a hard true answer are both available, the hard one is the answer.
- Everything here is best thinking to date, binding until argued down with evidence, and nothing is protected because it exists.
- A tool earns its place by what it replaces. One that must be fought on its home page, its vocabulary or its record is not earning it.

## What gets evaluated

Any system whose behavior a dataset can exercise: an agent; one step of an agent, given the correct prior steps; a skill or prompt the agent runs under; a model behind the same agent; a judge, whose dataset is traces with known verdicts; a reviewer such as the commit gate's; an arrangement of several agents under an operator. Each is a version of a system. The architecture never knows what kind.

## The method the architecture serves

The nouns below are the data of a practice, and a session that knows the nouns without the practice will build a scoring script and call it an eval. The practice:

1. Look at traces of the system working, and write down what went wrong in each, in observable terms.
2. Name failure modes from those notes, each with a binary criterion, a failing example and a passing example.
3. Build an evaluator for each criterion, code where the fact is exact, a judge where meaning decides, and validate it against verdicts already known before it counts.
4. Assemble a dataset of cases, each an input and an expectation, kept apart from the system that will be run on it.
5. State an experiment before it runs: what changed, which metric decides, what must not get worse. Run it, record it, decide, and never alter the record.
6. Keep running the same datasets against each new version, so regressions are seen when they happen.

Every artifact of this practice is one of the six nouns. A failure mode is the criterion a score names. A validated evaluator is a version that was itself evaluated on a dataset of traces. Monitoring is experiments over time. Nothing in the practice needs a seventh noun, and that is the test that the six are complete.

Step 1 comes first in time as well as in the list. No criterion in this package is written before traces of the system have been read.

## The nouns

Six. Everything specific to any subject is their content, never a type.

| Noun | Is | Why it is its own thing |
|---|---|---|
| Dataset | a versioned set of cases | an experiment must pin exactly which cases it ran, and a case added later must not change a decision already taken |
| Case | one input and the expectation a correct output meets | the expectation lives with the case and never with the system, or the system can see its own answer key |
| Version | the complete definition of a system under evaluation, identified by its content | two versions can be compared only if each is fixed and whole; a name typed by a person identifies nothing |
| Trace | what one version did on one case, once, with everything it produced | the one durable thing between generating and judging; every score points at one |
| Score | one evaluator's verdict on one trace: criterion, value, explanation, evaluator | a verdict without its reason and its author cannot be trusted or re-examined |
| Experiment | versions compared on one dataset version, stated before it ran, with its decision | the decision rests on what was pre-stated, so the record is a document, fixed when issued |

A Version is always the whole system. When a system is composed of parts, a step of an agent, a prompt inside it, a model behind it, each part is a value inside the version, and an experiment varies one part by issuing a new whole version that differs in that value. The thing compared never changes shape; what changed is read from the difference between two versions.

A Score attaches to a Trace, never to a run or a version. Generating and judging are two phases with the trace between them. An evaluator runs from the record, so a changed judge rescores every trace ever recorded, and no agent is rerun to re-judge it.

No human labels. Every verdict comes from a code evaluator or from a judge that returns a typed verdict with a confidence. This is sound because judging a trace against a stated structural criterion with paired examples is the easy side of the generation-verification gap: a verdict is a decision with a closed outcome space, and that is what a model does reliably, while open-ended generation is where it fails. An evaluator is validated against verdicts fixed by construction, references that are correct because of what they are, before its scores count. People author those references and the paired examples; people never grade runs.

## Two readers

**A person.** A stranger: someone who has never seen this project, opens either tool cold with many datasets, versions, experiments and runs in it, and has nobody to ask. The author is not the reader. The data is the wiki. Every dataset, case, version, trace, score and experiment is a page reachable from every page it relates to, generated from the records, and nobody authors a page by hand. The person must be able to open a dataset and see its versions against its metrics; open a case and see its input, its expectation and every version's scores on it; open an experiment and see the comparison and each case under it; open a run and see what the system produced, shown in the form a person judges it in, diffed against the expectation, with every evaluator's explanation; and from the run, open the trace itself. This view is not reporting. It is how the person verifies the system, the evaluators and the session that built them, without reading transcripts. Where a tool cannot show a required view, this package renders it into the record. Going without the view is never an option.

**A program.** The eval is operated by programs: a standing agent that defines versions, launches runs, reads scores and decides experiments; a scheduler; many agents coordinating through the records. So every operation is a public typed call, every record is readable without a person, records are append-only with every addition carrying its author's version, and every record carries the same address. Nothing is done by hand that a program will later need to do.

## One address

Every span, record, score and captured artifact carries the same key: dataset version, case, system version, repetition. Every store organizes by it. This is what keeps a thousand runs across many datasets navigable, and what lets two tools never disagree about which run a thing belongs to.

## Standards

Two, each owned by someone else, each a foreign model here, each written from its owner's contract open in the session.

- **The trace is OpenTelemetry.** The system's spans, in the GenAI semantic conventions, exported to the OpenTelemetry Collector. The collector is the one endpoint anything here exports to; every viewer is one of the collector's exporters. A score is also written as the conventions' evaluation event on the root span of the trace it judges. The eval opens that root span itself, and the collector exports every trace to a file beside the logs as well as to the viewer, so the record holds the trace it produced and a lost viewer loses nothing; a system's own private record of its runs, if it keeps one, is that system's and is never read here. Evaluators are systems, so their runs are traced the same way, linked to the trace they judged.
- **The record is Inspect's eval log.** One log per dataset version and system version; one sample per case; one epoch per repetition; a sample's input, target, output, and the transcript of what the system did, written in from its exported trace; a score per evaluator with value, explanation and metadata; identifying metadata on the log. It is a published, versioned format with a Python API, a dataframe API across many logs, a viewer that shows a sample's transcript and scoring, and a static bundle of viewer and logs for any static host. Nothing else is a store: the registry of datasets and versions, the captured artifacts, the exported traces and the experiment documents live beside the logs in one record root, every file named by digest or address and written once, so many programs write without a lock and the directory is published as it is. A log is appended to and never overwritten: a rescoring adds scores that carry their evaluator's version, and the first score stays.

HELM's data model was the record in the previous design and is set aside with evidence (`docs/decisions.md`, D2): its run page and tables worked, and its home page, its vocabulary, its text-only annotations and its model registries had to be fought, while Inspect's log already held five of the six nouns.

Every score is written three times from one value: as a Score in the log, as the evaluation event on the trace, and as a span annotation in Phoenix, because Phoenix's tree, table and charts read annotations and not events. The log is the owner; the other two are projections, regenerable from it.

## Tools

Each has one job and owns no meaning.

- **Inspect runs, records and shows samples.** A task is one dataset version against one system version; a sample is a case; an epoch is a repetition; the workspace is the record's, constructed from the version's parts, and the system's own boundary is the sandbox; the solver opens the run's root span and invokes the system's public surface inside it, in the same process, and captures; the scorers are this package's evaluators. Eval sets give retries and resumption; limits bound a run; hooks carry events out. Its viewer, bundled statically, is where a person reads a sample.
- **Phoenix shows traces.** It receives spans only from the collector, whose Phoenix pipeline maps this package's standard attributes to the ones Phoenix reads. This package writes to Phoenix one thing, the projection of verdicts: a project's description, one annotation configuration per criterion, and one span annotation per score on a run's root span, each regenerable from the log, so meaning keeps one owner.
- **One generated page is the site's front door.** Static, one file, from the logs and the experiment documents: the story of the experiments, the best version per dataset, and how to read the rest. It links into the bundled viewer and into Phoenix. It is the only page this package draws.

## Running it

A program hands `run` a dataset's content and a repetition count, in one call. The record identifies the dataset by its content and derives its oracle, the expectation itself as a version whose one part is the dataset's digest, so no one authors it and it cannot drift from its dataset; runs the oracle on every case that many times through Inspect; and reads the log back. What comes back is what became of the run: recorded, with the run, where its log is and one trace per case per repetition, each with its address, the ids of the span the eval opened and its capture; or unfinished, with the run, the log that says why and how it fell short. The eval writes no file of its own: the log Inspect writes is the record, each sample carrying its input and expected judged form in and its trace out as its output's metadata, and a version carries a display name beside its identity, the line a person reads in the log's description. The oracle is the one system built; a version a program defines, and the entrypoint by which construction chooses the integration that runs it, come with the first system.

```python
from type_construction.eval import EvalConfig, RecordedRun, Repetitions, Run, run_sync

config = (
    EvalConfig()
)  # EVAL_RECORD__ROOT names the record root; EVAL_RECORD__MODEL the model the runner binds to
outcome = run_sync(config, Run(dataset=my_dataset, repetitions=Repetitions(2)))
if isinstance(outcome.root, RecordedRun):
    print(outcome.root.log, [trace.address.key for trace in outcome.root.traces.root])
```

The process that runs it configures the OpenTelemetry SDK from the standard `OTEL_*` variables and adds the baggage span processor, so the address the eval sets as the run's baggage lands on the root span of every trace.

## Design

The concrete form is written as a product before any code, in `docs/`, in this order: `product.md`, the stranger it serves and the ten-minute test; `schema.md`, the six nouns as data with every field mapped to its slot under the owner's contract; `decisions.md`, the hard calls with their reasons and evidence.

## Lineage

Three earlier designs, and this one is their reduction.

The first, in October, modeled evaluation generically as TCA types across the whole practice. It got the generic ontology, automated judging, agents as versions and immutable records right. It was set aside because it was not buildable then, not because it was wrong.

The second built on Inspect alone, graded one agent's output against one reference program, put a judge first and brought human labels back. It got concreteness right and was captured by its subject.

The third kept the first one's ontology, the second one's tools, and added OpenTelemetry for the trace and HELM for the record and site. It got the two readers, the one address, the stranger and the trace-then-judge separation right. It was set aside because HELM's site had to be fought and Inspect's log already was the record.

This design keeps the ontology, the two readers, the address, OpenTelemetry and Phoenix, makes Inspect the runner, the record and the sample viewer, and keeps the one document and the one page that no tool provides.
