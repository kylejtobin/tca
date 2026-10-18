# TODO

The outcome: a person or a program can state a change to any system a dataset exercises, run it beside the baseline on the record, and know from validated verdicts on every step whether the change made the system better at the next right thing, with every run and verdict kept where a stranger can read it. The outcomes below achieve it, in this order.

An outcome is one thing a party outside the system can newly do across one crossing, reached by the loop in `AGENTS.md`: what crosses, the contract that owns it, the domain type it is; then its nouns, by name and kind; then the decisions it rests on, in `packages/python/type-construction-eval/docs/decisions.md`. The parties are a person, a program, the runner that calls back, the system under test and the judge model. The machinery is generic: nothing in the domain names a subject, a language or a dataset.

The outcomes cut one graph. The record is one system under one root: 1 runs it and reads its logs, 2 reads its folders, 3 exports traces into it, 4 and 5 write scores into its logs, 6 reads its logs across runs, 7 leaves a workspace under it, 8 reads what a run left, 9 folds and bundles it. The case: 2 decides its shape; 5 judges a step with its prior; 8 derives a step case from a run. The version: 4 adds `role`, 6 `lineage`, 7 `entrypoint`; identity by content (D20) reads the version whole, so each addition changes identity by design. The trace: 1 records it; 4, 5 and 8 hang their spans off its ids. A change to a node is made at the node and walked along every edge before anything else is built.

Rules the record established, binding every outcome (D22): the eval writes no file of its own, so every crossing is a library call whose reply is the fact; a span's attributes are given at its acquisition; a union's variants are each decided by a fact the others refuse.

## 0. Traces are read before any criterion is written

A person's act, outside this package, needing nothing built: the agent runs on the case in its own environment; its traces are read; each failure mode is written in observable terms; each criterion is derived with an authored passing and a failing example. It yields the criteria 4 and 5 construct. The criteria the README names are hypotheses until then.

## 1. A program runs a dataset's oracle and reads the run back

Crossing: a `Run` crosses from a program; the runner's log owns it; the domain type is `RunOutcome`. Built.

Correction, committed as its own fix before 2: the record is one system the deployment states once, `Record(root, model)`, reached as runner and as logs, each a derivation of the one statement. Nouns: the `record` integration, holding what `inspect` and `record/registry` held; the log reader over the root, a dataset's logs its derivation; the `inspect` integration gone. Nothing new is read, so nothing new is added.

Rests on D1, D20, D22.

## 2. A dataset is authored in the record

Crossing: a dataset's name crosses from a program; the record's folders own it; the domain type is `IdentifiedDataset`.

Nouns: `DatasetFolder`, `CaseFolder`, the layout, shaped for every case the graph names, a problem with files and an expectation, a prefix with a next step, a step with a verdict; `AuthorDataset`, `AuthorCase`, `ReadTree`, the actions; `FileEntry | DirectoryEntry`, an entry by its kind; `Folders`, the record's third derivation; in the record integration, the derivation of a judged form from sources, `PythonSource | OtherSource` a file by its place, `ClassDefinition | OtherStatement` a statement by its own fields, what `ast` yields validated by attributes, never a parser, `Definition`, `Sources`, folded to one line per class, `file: Name`, sorted. The domain holds `JudgedForm` and nothing of Python or classes; 8 reuses the derivation. The first dataset, `datasets/registrar`, is content shipped by the package, its reference the registrar's sources, its framing and type list beside it as content.

Rests on D15, D20, D22, and a decision for the folder's shape and the judged form.

## 3. A person runs the eval from the environment and reads the record in its viewers

Crossing: one message crosses from the environment; the process owns it; `RunMessage(dataset, repetitions)` is the domain's `Run`, and what the process prints is where the record put the log.

Nouns: `main.py`, the composition root, the OpenTelemetry SDK and the baggage processor configured at module level; the services `eval`, `collector`, `phoenix`, `viewer`, pinned images under the infrastructure skill; the collector's mapping of `eval.*` to OpenInference and its export into the record root; `just` recipes. Verified from the README end to end, the oracle's traces in Phoenix under the dataset's project, its log in the viewer; every outcome after this is verified the same way.

Rests on D8, D18, D21.

## 4. A run is scored by code, and the oracle scores 1.0

Crossing: a recorded repetition crosses when the runner calls its scorer; the log owns the score; the domain type is `Score`.

Nouns: `Criterion(id, description, kind)`; `Score(address, trace, criterion, evaluator, label, value, confidence, explanation)`; the evaluator as a `Version`, which regains `role`; `matches-expectation`, the code criterion every dataset has; `EvaluateInterpreter`, whose span `evaluate <criterion>` is a child of the run's root through the recorded ids, its verdict among its attributes at acquisition; the scorer as a composition-root callback the runner names by registry, as the solver is; the Phoenix provider, its annotation, project description and annotation configuration, each kept by the reply Phoenix gives; rescoring as the runner's own `score`, which returns the log.

Rests on D5, D6, D7, D17, D22.

## 5. A judge is a system, and it scores a run

Crossing: a step with its prior crosses to a model; the model's reply owns the verdict; the domain type is `Score`.

Nouns: the judge as a `Version` whose parts are a model and a prompt, exercised by a dataset like any system; the step and its prior as the judge's input; the verdict as the domain's own type, the contract the model's structured output meets; the model provider and the judge's interpreter; the step criterion from 0, "was this the next right thing"; the `judge-<criterion>` dataset of authored passing and failing examples, in 2's shape. A judge's verdicts count only after 6 validates it.

Rests on D13, D22.

## 6. An experiment is stated and decided

Crossing: a `Statement` crosses from a person or a program; the logs of the baseline's and the change's runs own the results; the domain type is `Decision`.

Nouns: `Statement`, naming dataset version, baseline, candidates, the one part that differs, the deciding criterion, the guardrails, the repetitions and the threshold rule; `Version` regains `lineage`; `Decision`, kept or rejected or inconclusive with its reason, recorded where a library's reply is the fact, which amends D10. A judge's validation is this outcome over its `judge-<criterion>` dataset, decided by `matches-expectation`. The first experiment, after 7 and 8: the agent under today's single prompt as the baseline beside the agent under the enforced loop, decided by the step criterion.

Rests on D10, D12, D13.

## 7. A system runs as deployed

Crossing: a `Version` with its entrypoint crosses to the system's own public surface; that surface owns the production; the domain type is `Trace`.

Nouns: `Version` regains `entrypoint`; `Run.version` is `Version | Oracle`, and `IdentifiedRun` admits either; `RunAgent`, the action, and `EntrypointInterpreter`, the union construction chooses by entrypoint; `AgentConfig` from the version's parts; the case's input files reach the workspace by the system's or the runner's contract, never by a write of the eval's; bubblewrap in the image; a step judge the system consults in its loop is a part of its version, so 6 can compare with and without it.

Rests on D3, D4, D18, D19.

## 8. A recorded run's capture is read, whole and by step

Crossing: a run's address crosses from a program or the scorer; the record's folders and exported traces own what the run left; the domain type is `Capture`, its history one judged form per step.

Nouns: the workspace left under the artifact's address, read through `Folders` into the judged form by 2's derivation; the exported trace stream under `traces/`, a foreign model of the export, read into the run's steps; `Capture` whole and `History`, the judged form after each step; the `capture` span, a child of the root through the recorded ids; `StepCase`, a derivation of a recorded run, its input the prefix as `Input.prior`, its expectation the next step, so a program states a `Run` of step cases without a folder.

Rests on D14, D15, D19.

## 9. The record reads itself to a person

Crossing: a listing, a table and a page cross to a person; the logs own what they show.

Nouns: `list`, the datasets, versions and runs folded from the logs, newest first, where a display name resolves to the newest version run under it; the per-dataset table of versions against criteria from the logs' metrics; the front door over the runner's bundle, served or written through a library whose reply is the fact, which amends D11.

Rests on D9, D11, D16.
