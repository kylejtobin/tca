# Journeys

The paths the stranger walks, each tied to the test task it serves. Each step: where they are, what they see, what they learn, where they go next, and the data this package controls that makes the step legible. Example content is the first subject; no step depends on it.

## J1. Phoenix, cold, to one run's story (T2)

| Step | Where | Sees | Learns | Next | Data |
|---|---|---|---|---|---|
| 1 | Projects page | `registrar`, `judge-framing`, each with trace count and last update | A project is a body of work; `judge-` ones are about judges | Click `registrar` | project name = dataset name |
| 2 | Project page | Description: what a trace is here, what the columns are, the three filters, the site URL. Below, rows `run domain-registration` with input, output summary, pass/fail badges per criterion, metadata | Which runs failed which criteria; which version each was | Sort by `check-passes` or filter `annotations["check-passes"].label == "fail"` | project description; annotations on the root; `eval.output`; address in metadata |
| 3 | Trace page | Root row with badges, failures first; four chapters; the long one is the system's | The run's shape; which verdicts failed | Click the root | span names; eval-owned chapters |
| 4 | Root span, Annotations | `check-passes · CODE · fail · 0 · ruff F401 in domain/registration/type.py:3; basedpyright: 2 errors` | Why, in the evaluator's words | Open the system's chapter | annotation name, kind, result, explanation |
| 5 | `invoke_agent tca-agent` | Model calls with messages, tool calls with arguments and results, in order | What the system did, step by step | Find the `execute_tool write_file` the explanation points at | the system's GenAI-convention spans |
| 6 | `capture workspace` | Output: the judged form, its history file by file, the diff | How the type list changed as the run went | Done | derived history on the capture span |

Six steps. The visitor names the criterion, quotes the reason, points at the span.

## J2. The site, cold, to a decision and down to a run (T1, T3)

| Step | Where | Sees | Learns | Next | Data |
|---|---|---|---|---|---|
| 1 | Front door | The question; chapter 1; `Kept · compaction 0.5 · e-2026-10-17-compaction · check-passes 0.60 → 1.00 · 5 reps`; the rejected line beside it with the same fields | What was decided last and why, in one line | Click the experiment's candidate log | front door from decision documents |
| 2 | Log viewer, log header | Description: dataset, version, what a sample and an epoch are; the statement and decision text for this experiment | This log is one version on one dataset version; the decision rested on a rule stated first | Scroll to the samples | log `description`, `metadata` |
| 3 | Samples list | Rows per case and epoch; pass/fail per criterion; filter to failures | Where the pass rate came from | Click a sample | task view columns from the dataset's criteria |
| 4 | Sample, Scoring | Per criterion: what was compared, the explanation. The target is the expected judged form; the output is the produced one; `diff` is beside them | Expectation and production, side by side, with every reason | Copy `trace.url` from Metadata | `Score.explanation`, `Sample.target`, sample metadata |
| 5 | Phoenix | Continues as J1 step 3 | | | `trace.url` |

The visitor states the change, the criterion, the direction and the numbers, and opens the run that carried it.

## J3. A trace to its experiment and back (T5)

| Step | Where | Sees | Learns | Next | Data |
|---|---|---|---|---|---|
| 1 | Any trace, root attributes | `eval.experiment.id`, `eval.system.version` | This run was in a stated experiment | Filter the project by `attributes["eval.experiment.id"]` | address on the root span |
| 2 | Project page, filtered | Two versions × five epochs × one case, badges per criterion | The whole evidence of the experiment | Open the front door's line for it | project description links the site |
| 3 | Front door | The experiment line: the change named as one part with both digests | Exactly what differed | Done | statement document |

## J4. The contributor validates a judge (T4)

| Step | Where | Sees | Learns | Next | Data |
|---|---|---|---|---|---|
| 1 | Front door, "How to read this" | Score: "one evaluator's verdict … an evaluator counts only after it agreed with authored verdicts; first example: judge-framing" | Judges are validated | Click it | first-example links |
| 2 | Log viewer, `judge-framing` log | Description: "Evaluator judge-framing@c2d4… on dataset judge-framing@4b77…: cases are the authored reference and failing examples with their known verdicts" | Where the ground truth came from | Scroll | log description |
| 3 | Samples list | One row per authored example; criteria `agrees-on-pass`, `agrees-on-fail` | Agreement per example | Open a disagreement, if any | scores |
| 4 | Front door, story | The validation experiment's line: `Kept · judge-framing v1 · agrees-on-fail 1.00, agrees-on-pass 1.00` | The judge counted from that decision | Add a failing example as a new case | decision document |

## J5. The operator program

No screens. The calls are in `schema.md` under "Operator calls", in the order J5 runs them: define a version, state an experiment, run, score, read results, decide, publish, repeat for every new version on every dataset. A scheduler runs steps three to seven with no person present; a person audits each by J1 to J4 afterwards.
