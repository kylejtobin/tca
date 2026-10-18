# Product

Who this instrument serves, what it promises them, and the test that says it kept the promise. Every other document in this directory is checked against this one.

## The stranger

The customer has never seen this project, opens one of its two tools cold with many datasets, versions, experiments and runs already in them, and has nobody to ask.

1. **The visitor.** An engineer who heard a claim, "this change made the agent better" or "TCA development can be automated", and will give the instrument ten minutes to decide whether to believe it. They also come for the arc: which experiments moved the agent from one agent to many, what each changed, and what the current version does and does not yet do.
2. **The contributor.** Someone who wants to add a case, write an evaluator or submit a version. They learn the method from the records, because the records are what they will add to.
3. **The operator program.** An agent or scheduler that defines versions, runs, scores, states and decides experiments. It has no memory between invocations and no screen.

The author is not a customer. A screen that needs the author to explain it is a defect.

## The promise

Open any record, in either tool, and it tells you what it is, how it got here, and where to go next. From a claim you reach the decision; from the decision, the experiment stated before it ran; from the experiment, the runs it compared; from a run, what the system produced in the form a person judges it in, beside what was expected; from the judgment, each evaluator's verdict and its reason; and from there the trace of what the system did, step by step. Every hop is a click or a copied identifier in the tool you are already in. Nothing on the path was written by hand.

## The ten-minute test

Kept when a stranger, given the two URLs and nothing else, does each of these in ten minutes or less and gives the right answer.

| # | Task | Right answer |
|---|---|---|
| T1 | Open the site. Find the most recent decision. Say what changed, which criterion decided it, and which way it went. | "Experiment E changed part P of system S; decided on criterion C; kept or rejected; pass rate moved from a to b over n repetitions." |
| T2 | Open the trace viewer. Find the worst recent run on any dataset. Say which criterion it failed, why, and point at the step where it went wrong. | A criterion, the evaluator's explanation in its words, and a span. |
| T3 | From that run, reach its sample in the log viewer and say what the expectation was. | The case's expectation beside the produced output, with the diff. |
| T4 | From the site, find how the judge for criterion C was validated before its scores counted. | The validation experiment, its dataset of authored verdicts, its agreement rates. |
| T5 | Say exactly what differs between two versions that were compared. | One part, by name, with both digests. |

The contributor passes when, after T1 to T5, they can name the six kinds and what each is for without having read a README. The operator program passes when every step is a typed call or a file read.

A failed task is a defect in one of these documents, at the step where the stranger stalled.

## What the instrument refuses to be

- **Not a dashboard.** No number is shown without a path down to a run, a criterion and a reason.
- **Not a transcript dump.** Raw messages are the last thing reached, never the first.
- **Not a leaderboard of models in general.** Rows are versions of systems on this project's datasets; columns are this project's criteria.
- **Not a grading tool.** People author cases, references, criteria and the paired examples that validate evaluators. Nobody grades a run.
- **Not a harness for one agent.** The first system evaluated is one agent. Nothing generic names it. The front door speaks in the project's voice, as TCA evaluation; that voice is content the generic machinery renders.
- **Not a catalogue.** The front door carries one version per dataset, the current best, with the criteria it still fails beside the ones it passes, and the experiments that turned the story, rejected beside kept with the same fields. Every other run is one click deeper.
