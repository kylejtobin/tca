# type-construction-eval

An evaluation architecture. It exists so that a person or a program can know, with trust, whether a change to a system made that system better at a body of work, and can open the answer down to one run, one criterion and one evaluator's reason. The bar is the best evaluation architecture there is, built from what the field has learned, not from this repository's habits.

This package is built under Type Construction Architecture because everything in this repository is. TCA governs how its code is written. TCA does not define what evaluation is, and the first system evaluated here, the TCA agent, is one subject among many. If a sentence in the generic part of this document needs a TCA word to make sense, the design has been captured by its first subject, and the sentence is wrong.

## Before reading further

You are reading this with no context, as the sessions that wrote it once did. Three of them lost the thread in the same way: they reached for the nearest authoritative text, the skill, the agent, the file in front of them, and restated it with conviction instead of asking what evaluation itself needs. Each time the design shrank to a scoring harness for one agent. So, while you read and after:

- When a question is about what evaluation needs, ask what evaluation is and what the field has learned. Ask what TCA says only when writing code.
- A claim about a standard, a library or a tool is made with its contract open, and the source named. Unread means unclaimed.
- A decision that can be made is made, here, now, with its reason. "Later," "out of scope" and "not eval" are not decisions.
- When an easy true answer and a hard true answer are both available, the hard one is the answer.
- Everything here is best thinking to date, binding until argued down with evidence, and nothing is protected because it exists.

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

No human labels. Every verdict comes from a code evaluator or from a judge that returns a typed verdict with a confidence. This is sound because judging a trace against a stated structural criterion with paired examples is the easy side of the generation-verification gap: a verdict is a decision with a closed outcome space, and that is what a model does reliably, while open-ended generation is where it fails. An evaluator is validated against verdicts fixed by construction, references that are correct because of what they are, before its scores count.

## Two readers

**A person.** The data is the wiki. Every dataset, case, version, trace, score and experiment is a page reachable from every page it relates to, generated from the records, and nobody authors a page by hand. The person must be able to open a dataset and see its versions against its metrics; open a case and see its input, its expectation and every version's scores on it; open an experiment and see the comparison and each case under it; open a run and see what the system produced, shown in the form a person judges it in, diffed against the expectation, with every evaluator's explanation; and from the run, open the trace itself. This view is not reporting. It is how the person verifies the system, the evaluators and the session that built them, without reading transcripts. Where a tool cannot show a required view, this package renders it into the record. Going without the view is never an option.

**A program.** The eval is operated by programs: a standing agent that defines versions, launches runs, reads scores and decides experiments; a scheduler; many agents coordinating through the records. So every operation is a public typed call, every record is readable without a person, records are immutable once issued, and every record carries the same address. Nothing is done by hand that a program will later need to do.

## One address

Every span, record, score and captured artifact carries the same key: dataset version, case, system version, repetition. Every store organizes by it. This is what keeps a thousand runs across many datasets navigable, and what lets two tools never disagree about which run a thing belongs to.

## Standards

Two, each owned by someone else, each a foreign model here, each written from its owner's contract open in the session.

- **The trace is OpenTelemetry.** The system's spans, in the GenAI semantic conventions, exported to the OpenTelemetry Collector. The collector is the one endpoint anything here exports to; every viewer is one of the collector's exporters. A score is also written as the conventions' evaluation event on the root span of the trace it judges, through the collector. The eval starts every run, so it holds the trace it produced; a system's own private record of its runs, if it keeps one, is that system's and is never read here. Evaluators are systems, so their runs are traced the same way, linked to the trace they judged.
- **The record is HELM's data model.** Scenario, instance with references, run spec, request state, per-instance stats and aggregates, written as HELM writes them and rendered by HELM's summarizer and frontend. HELM is the one published, versioned, widely produced model of a complete evaluation record with a site generated from it, and that is the standard this package adopts rather than inventing a record format. Nothing else is a store.

Every score is written twice, as a stat in the record and as an evaluation event on the trace, so the site and the trace viewer agree without either reading the other.

## Tools

Each has one job and owns no meaning.

- **Inspect runs.** A task is one dataset against one version; its solver invokes the system's public surface and stops; its scorers are this package's evaluators. Its own log serves it while it runs and is not the record.
- **Phoenix shows traces.** It receives only what the collector exports. This package has no Phoenix crossing, so nothing in Phoenix has a second owner. The top-level site is HELM's frontend, not Phoenix, because HELM's frontend is the table across versions and metrics and Phoenix is the view inside one trace; each run on the site links to its trace in Phoenix by trace id.
- **HELM's frontend is the site.** Generated from the records.

## Lineage

Two earlier designs, and this one is their synthesis.

The first, in October, modeled evaluation generically as TCA types across the whole practice: error analysis, experiment design, dataset, evaluator specification, result, monitoring. It got the generic ontology, automated judging, agents as versions and immutable records right. It was set aside because it was not buildable then, not because it was wrong.

The second built on Inspect alone, graded one agent's output against one reference program, put a judge first and brought human labels back. It got concreteness right and was captured by its subject.

This design keeps the first one's ontology and reasons, the second one's concreteness and tools, adds the two standards, the two readers and the operator, and places the subject in its own section below.

## The first subject

The TCA agent, modeling domain registration. The dataset is one case: the problem statement as input; as expectation, the reference program `type-construction-registrar`, with its framing and its noun list written beside it. The agent's workspace holds the skills, the check and the problem statement; the expectation lives in this package and never reaches the workspace.

For this subject, what a person judges a run by is the agent's list of nouns, diffed against the reference's, and how that list changed file by file across the run; the program text sits beneath it. Scores begin with code: the program parses and passes the check; nouns are recalled and placed as the reference places them; the program's structure matches the reference's. A judge comes after the code evaluators, as the same kind of thing. When the agent's steps become typed outputs on its spans, a case whose input is the correct prior steps and whose expectation is one step's output is a case like any other.

The order: first the oracle, with no agent, the reference itself written as a dataset, a case, a version, a trace and scores of 1.0, rendered on the site and visible in the trace viewer, because if the reference cannot be written and scored as these records the ontology is wrong and that is learned before any agent runs. Then the agent as it is. Then two versions compared. Then decision cases as the agent decomposes.

In the package today: the case's problem statement, framing and noun list are the first case's content and stay. A judge prompt from the second design remains and is superseded; it goes when the evaluator exists.
