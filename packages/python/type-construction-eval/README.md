# type-construction-eval

Type Construction Architecture's evaluation: the eval architecture for the TCA agent, built on Inspect AI.

This package is that architecture as planned: this README, the judge's prompt and the first case's reference. The code and the recipes named below, `just eval`, `just calibrate` and `just baseline`, are not yet built; building them is the next outcome.

The agent gets a problem statement and a fresh workspace holding the skills, and nothing else. It works there as it works anywhere, reading and writing files, and the program it leaves in the workspace's `src/` is graded against a reference program, by nouns, layers, fields and edges, with code where the fact is exact and a judge where meaning decides. The registrar package is the first reference.

## Layout

```text
cases/<domain>/problem.md                the problem statement, prose in the domain's words
cases/<domain>/reference/framing.json    the reference's outcome, tactics and crossings
cases/<domain>/reference/noun-list.json  the reference's list: name, layer, kind, file
cases/<domain>/labels/<trace>.json       a hand-labeled trace the judge is calibrated against
prompts/agents/judge.md                  the judge's prompt
domain/evaluation/                       case, structure, comparison, verdict, calibration
integration/judge/                       the judge: a provider and its interpreter
integration/inspect/                     the task, solver and scorers
```

A case is a domain to model: its problem statement, with the reference beside it. The reference package itself is a sibling package in the workspace, and the reader walks its `src/`. The first case is `domain-registration`, whose reference is `type-construction-registrar`.

The reference's noun list is the modeling judgment, what each thing is and where it lives, written to the schema the plan states for the work's one list; the code reader checks its names and files against the reference package, and the oracle test holds them together. Its framing is the outcome, the tactics and the crossings, prose nothing derives.

## The task

The agent is told to build, in a workspace made for the run. The program it leaves there is read for its structure, and its trace is read for the framing and the noun list it worked from. Each is graded against its reference: the program against the reference package's `src/`, the list against `reference/noun-list.json`, the framing against `reference/framing.json`. The reference never enters the agent's context.

## Scores

The program scores are the headline: they say whether what the agent built is the reference's domain. The framing score says whether it saw the same crossings. The trace scores are diagnostics of how it worked, and where a run's steps have typed outputs, they read those outputs, not prose.

| Score | By | Reads |
|---|---|---|
| parses, bases, edges, counts | code | the program |
| noun match across names | judge | the program and the reference |
| framing against reference | judge | the trace and the reference |
| violated sentence of the skill | judge | the program and the skill |
| outcome before any noun | judge | the trace |
| crossings before any file | judge | the trace |
| whole list questioned after each file | judge | the trace |
| list reprinted whole whenever it changed | judge | the trace |

Recall, precision and agreement are computed from the noun matches. Each sample runs five epochs. The judge's scores count once its agreement with the labels reaches 0.9.

## Runs

| Recipe | Does |
|---|---|
| `just eval` | runs the task over every case and writes an Inspect log |
| `just calibrate` | scores the labeled traces and reports the judge's agreement |
| `just baseline` | runs the eval at the current commit and keeps its log as the baseline |

| Variable | Holds |
|---|---|
| `EVAL_JUDGE__MODEL` | the judge's model, as pydantic_ai names it; not the agent's |
| `INSPECT_LOG_DIR` | where Inspect writes its logs; Inspect reads it itself |

The skill is frozen; a skill change is a new baseline. The oracle test feeds the reference through the scorer and requires 1.0. Tuning a prompt against the judge is a later outcome, one per step of the agent once it has steps.

## Sequence

1. Build the eval: the reader, the scorers, the judge and the three recipes, with the oracle test first.
2. Baseline the agent as it is, one agent following the loop in its prompt, on `domain-registration`.
3. Decompose the agent into one provider per step of the loop, each step's output the domain type it produces: the outcome, the crossings, the noun list, a file.
4. Baseline again. The comparison that counts is the program score.
