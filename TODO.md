# TODO

The remaining work on the eval, grouped by outcome and sequenced B to G; A is built. An outcome is one thing a party outside the system can newly do; each is reached under the loop in `AGENTS.md`, every file checked by `just check`, every decision naming the sentence of the skill it follows. The modeling is A through E, A done; F is environment and verification over what A through E built; G is rendering over all of it. The decisions each item rests on are in `packages/python/type-construction-eval/docs/decisions.md`.

## B. A dataset is authored from a folder, its judged form is derived, and the first dataset exists

- **The judged form is derived, never authored.** `integration/python/` reads a directory's `.py` files through the standard library's `ast` into `Definitions`, one per class as `file: Name`, sorted, rendered as the `JudgedForm`. The same derivation runs on a reference at authoring and on a production at capture, so the diff is between like things. The authored type list stays as content for later criteria on layer and kind.
- **Authoring from a folder.** A folder with `problem.md` and `reference/` is read into a `Dataset` document, its judged form derived as above, and registered. Datasets live in the record root; the package ships the first one as its example.
- **The first dataset.** From `problem.md`, the framing, the type list and the reference program's own sources in this repository, authored by the folder reader.

## C. Every run is scored three ways, and the oracle scores 1.0

- **Score, criterion, evaluator.** `Criterion(id, description, kind)` and `Score(address, trace, criterion, evaluator, label, value, confidence, explanation)` in the domain. Evaluators are versions of system `eval` with role `evaluator`, their parts the package's digest.
- **The first criterion is generic.** `matches-expectation`: the produced judged form equals the expected one. Every dataset has it, so the oracle scores 1.0 before any subject-specific criterion exists.
- **Where a score is written.** An evaluator is an interpreter in `integration/evaluator/`; its span `evaluate <criterion>` is opened as a child of the run's root through a remote context built from the trace's recorded ids, and the evaluation event is written on it. The scorer Inspect calls is a composition-root callback composing the evaluator, the log's `Score` validated from our score's JSON, and the Phoenix annotation on the root span's id through an `integration/phoenix/` provider, with the project's description and one annotation configuration per criterion.
- **Rescoring.** Inspect's own `score` over a log with `action="append"`, written back, every score carrying its evaluator's version.

## D. The agent is evaluated as deployed

- **The agent variant.** With a second system, `Run.version` admits a `Version` or the dataset's `Oracle`, `Version` regains `role`, `entrypoint` and `lineage` as they are read, and `EntrypointInterpreter` is the union construction chooses by entrypoint, `RunAgentInterpreter` behind the action `RunAgent` beside the oracle's. It builds `AgentConfig` from the version's parts, places the workspace in the record, calls the agent's `run` inside the root span so its spans are children through the SDK's own context, takes the transcript from the run's result, captures the workspace and derives its judged form.
- **The boundary.** Bubblewrap in the image's system layer, so the agent's commands and its check run inside its own boundary within the eval's process.
- **In parallel, outside this package.** Run the agent on the case a handful of times in its own environment, read the traces, write the failure modes in observable terms, and derive the criteria with their authored passing and failing examples. The criteria named in the eval README are hypotheses until this is done.

## E. An experiment is stated, run and decided from one document

- **Statement and decision.** Both documents in the domain, each written once: the statement before the run names dataset version, baseline, candidates, the one part that differs, the deciding criterion, the guardrails, the repetitions and the threshold rule; the decision after names the results, kept or rejected or inconclusive, and the reason.
- **The statement is a message.** The process runs baseline and candidates on the dataset version as one Inspect eval set, then `decide` reads each log's per-scorer metrics, applies the rule and writes the decision.
- **Validation is an experiment.** An evaluator counts only after a statement over a `judge-<criterion>` dataset, whose cases are the authored examples, was kept.

## F. A stranger runs it from the README and opens two viewers

- **The process.** `main.py`: settings under `EVAL_` naming the record root, the model binding and one message, `RunMessage(dataset, version, repetitions)` or `ExperimentMessage(statement)`, a union picked by shape; the OpenTelemetry SDK configured from the standard variables with the baggage processor at module level; one callback that performs the message and prints where the record put it.
- **The services.** `eval`, `collector`, `phoenix` and `viewer` in `compose.yaml` with pinned images, under the infrastructure skill; the collector maps `eval.input`, `eval.output` and `eval.span.kind` to OpenInference, sets the project from the root span's dataset, exports to Phoenix and streams the trace into the record root; `just` recipes to start them.
- **Leveled and verified.** `.env.example`, the eval README and its documents say what A through F built; the first run is verified from the README end to end: the oracle's traces in Phoenix under the dataset's project, its log in the viewer, its score of 1.0.

## G. The record reads itself to a person

- **Listing.** `list` folds the datasets' logs, read through Inspect, into datasets, versions and runs, newest first; a version's display name resolves here, from the logs, to the newest version run under it.
- **The table.** A per-dataset table of versions against criteria from the logs' metrics, as text, as soon as scores exist.
- **The front door and the bundle.** One generated page, the story in chapters, the best version per dataset and how to read the rest, over Inspect's static bundle of the viewer and the logs.
