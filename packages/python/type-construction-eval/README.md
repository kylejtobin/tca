# type-construction-eval

Type Construction Architecture's evaluation: the eval architecture for the TCA agent, built on Inspect AI and DSPy.

The agent gets a problem statement and its own package, and nothing else. What it produces is graded against a reference program, by nouns, layers, fields and edges, with code where the fact is exact and a judge where meaning decides. The registrar package is the first reference.

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
integration/dspy/                        the module GEPA optimizes and its metric
```

A case is a domain to model: its problem statement, with the reference beside it. The reference package itself is a sibling package in the workspace, and the reader walks its `src/`. The first case is `domain-registration`, whose reference is `type-construction-registrar`.

## The task

The agent is told to build. Its answer is read for the program, and its trace is read for the framing and the noun list it worked from. Each is graded against its reference: the framing against `reference/framing.json`, the list against `reference/noun-list.json`, the program against the reference package's `src/`. The reference never enters the agent's context.

## Scores

| Score | By | Reads |
|---|---|---|
| parses, bases, edges, counts | code | the output |
| noun match across names | judge | output and reference |
| framing against reference | judge | output and reference |
| violated sentence of the skill | judge | output and the skill |
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
| `just tune` | one GEPA round over the agent's prompt, scored by the same judge |

| Variable | Holds |
|---|---|
| `EVAL_JUDGE__MODEL` | the judge's model, as pydantic_ai names it; not the agent's |
| `INSPECT_LOG_DIR` | where Inspect writes its logs; Inspect reads it itself |

The skill is frozen; a skill change is a new baseline. The oracle test feeds the reference through the scorer and requires 1.0.
