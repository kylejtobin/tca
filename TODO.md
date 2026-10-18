# TODO

The outcome: a stranger or a program can state a change to any system a dataset can exercise, run it step by step against the record, and know from validated verdicts, in two viewers and one call, whether the change made that system better at the next right step. The outcomes below achieve it, in this order.

Each outcome is one thing a party outside the system can newly do across one crossing, reached under the loop in `AGENTS.md`: the crossing stated first, what crosses, the contract that owns it, the domain type it is; then its nouns, by name and kind. An item names the decision it rests on, in `packages/python/type-construction-eval/docs/decisions.md`, and says no more. A is built, with one placement to remodel first.

The outcomes are cuts through one graph, and four nodes carry its edges. The record, one system under one root: A runs it and reads its logs, B reads its folders, F exports traces into it, C writes scores into its logs, D reads the workspace left under it, H reads its traces as the transcript, E reads its logs across runs, G folds and bundles them. The case: B decides its shape, H's step case has a prior and a next step, E's judge case has a step and a verdict. The version: C adds `role`, D `entrypoint`, E `lineage`, and identity by content (D20) reads the version whole, so each addition changes what identity is, by design. The trace: A records it, and C's evaluate span, D's capture span and H's step history hang off its ids. A change to a node is made at the node and walked along every edge before anything else is built.

Rules A established, binding every item (D22): the eval writes no file of its own, so every crossing is a library call whose reply is the fact; a span's attributes are given at its acquisition; a union's variants are each decided by a fact the others refuse. The loop's own rule, skipped twice and never again: each file's types, fields and valid states are stated before it is written, one file per step, the check between.

## 0. Traces are read before any criterion is written

A person's act, outside this package, needing nothing built: the agent runs on the case in its own environment; its traces are read; each failure mode is written in observable terms; each criterion is derived with an authored passing and a failing example. It yields the criteria C and H construct. The criteria the README names are hypotheses until then.

## A'. The record is one system

Crossing: none new; a placement of A remodeled. The record is one system the deployment states once, `Record(root, model)`, reached as runner and as logs, each a derivation of the one statement; a `Run` crosses as before and the same `RunOutcome` returns.

Nouns: the `record` integration, holding what `inspect` and `record/registry` held; the log reader over the root, the dataset's logs a derivation; the `inspect` integration gone. Nothing new is read, so nothing new is added; D's and B's folders arrive when something reads them.

Rests on D20, D22.

## B. A dataset is authored from a folder, and the first dataset exists

Crossing: a dataset's name crosses from a program; the record owns the folder under its root; the domain type is `IdentifiedDataset`.

Nouns: `DatasetFolder`, `CaseFolder`, the layout, shaped for every case the graph names, a problem with files and an expectation, a prefix with a next step, a step with a verdict; `AuthorDataset`, `AuthorCase`, `ReadTree`, the actions; `FileEntry | DirectoryEntry`, an entry by its kind; `Folders`, the record's third derivation from its one statement; in the record integration, the derivation of a judged form from what folders yield, `PythonSource | OtherSource` a file by its place, `ClassDefinition | OtherStatement` a statement by its own fields, what `ast` yields validated by attributes, never a parser, `Definition`, `Sources`, folded to one line per class, `file: Name`, sorted. The domain holds `JudgedForm` and nothing of Python, classes or any one subject; D reuses the derivation at capture.

The judged form is the subject's own noun list, so it is the step unit H judges. The first dataset is `datasets/registrar`, content shipped by the package; its reference is the registrar's own sources; the framing and the type list stay beside it as content.

Rests on D15, D20, D22, and a decision for the folder's shape and the judged form.

## F. A stranger runs the oracle from the README and opens two viewers

Crossing: one message crosses from the environment; the process owns it; `RunMessage(dataset, repetitions)` is the domain's `Run`, and what the process prints is where the record put the log.

Nouns: `main.py`, the composition root, the OpenTelemetry SDK and the baggage processor configured at module level; the services `eval`, `collector`, `phoenix`, `viewer`, pinned images under the infrastructure skill; the collector's mapping of `eval.*` to OpenInference and its export into the record root; `just` recipes.

Verified from the README end to end: the oracle's traces in Phoenix under the dataset's project, its log in the viewer. Every outcome after this is verified the same way.

Rests on D8, D18, D21.

## C. Every run is scored, by code and by a judge, three ways, and the oracle scores 1.0

Crossing: a run's log crosses to the scorer Inspect calls; the log owns the score; the domain type is `Score`.

Nouns: `Criterion(id, description, kind)`; `Score(address, trace, criterion, evaluator, label, value, confidence, explanation)`; the evaluator as a `Version`, which regains `role`; `matches-expectation`, the code criterion every dataset has; the first judge criterion from item 0, a version of a model and a prompt through Inspect's model-graded scoring, counted only after E validates it; `EvaluateInterpreter`, whose span `evaluate <criterion>` is a child of the run's root through the recorded ids, its verdict among its attributes at acquisition; the scorer as a composition-root callback Inspect names by registry, as the solver is; the Phoenix provider, its annotation, project description and annotation configuration, each kept by the reply Phoenix gives; rescoring as Inspect's own `score`, which returns the log.

Rests on D5, D6, D7, D13, D17, D22.

## D. The agent runs as deployed

Crossing: a version a program defines crosses in `Run`; the agent's own public surface owns the production; the domain type is `Trace`.

Nouns: `Version` regains `entrypoint`; `Run.version` is `Version | Oracle`, and `IdentifiedRun` admits either; `RunAgent`, the action, and `EntrypointInterpreter`, the union construction chooses by entrypoint; `AgentConfig` from the version's parts; the workspace the agent leaves under the artifact's address, which the record reads back as the capture, its judged form derived as in B, announced on the `capture workspace` span, a child of the root through the recorded ids; the case's input files reach the workspace by the agent's or Inspect's contract, never by a write of the eval's; bubblewrap in the image; the step judge the agent consults as a part of its version, so E can compare.

Rests on D3, D4, D15, D18, D19.

## H. Each step of a run is judged as the next right thing

Crossing one: a recorded run's transcript crosses to the capture; the trace owns it; the domain type is the judged form's history, file by file, each step scored by the step criterion.

Crossing two: a step case crosses as a `Case` whose input is a recorded run's prefix and whose expectation is the next step, cut from the traces; `Input.prior` as the schema has it.

Rests on D14.

## E. An experiment is stated by a person, run and decided in one message

Crossing: a `Statement` crosses as the process's message; the eval set's logs own the results; the domain types are `Statement` and `Decision`.

Nouns: `Statement`, naming dataset version, baseline, candidates, the one part that differs, the deciding criterion, the guardrails, the repetitions and the threshold rule; `Version` regains `lineage`; `Decision`, kept or rejected or inconclusive with its reason, recorded where a library's reply is the fact, which amends D10; validation as an experiment over a `judge-<criterion>` dataset of the authored examples; the first experiment, the agent with the step judge against the agent without it, decided by the step criterion.

Rests on D10, D12, D13.

## G. The record reads itself to a person

Crossing: a listing, a table and a page cross to a person; the logs own what they show.

Nouns: `list`, the datasets, versions and runs folded from the logs, newest first, where a display name resolves to the newest version run under it; the per-dataset table of versions against criteria from the logs' metrics; the front door over Inspect's bundle, served or written through a library whose reply is the fact, which amends D11.

Rests on D9, D11, D16.
