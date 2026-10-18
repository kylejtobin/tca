# Storyboards

Every screen the journeys touch, with the text that renders and the field that carries it. Text in `«»` is carried by a field named in `schema.md`; text outside it is the tool's chrome. Phoenix renders from spans and annotations; Inspect's viewer renders from the log and the task's view configuration; the front door is the one screen this package draws.

## Phoenix

### P1. Projects page

```
Projects                                              [search projects by name]
┌───────────────────────────┐ ┌───────────────────────────┐
│ registrar                 │ │ judge-framing             │
│ 212 traces · p50 4m 12s   │ │ 28 traces · p50 9s        │
│ Last updated 2 hours ago  │ │ Last updated 3 days ago   │
└───────────────────────────┘ └───────────────────────────┘
```

Carried by: resource attribute `openinference.project.name` ← `eval.dataset.name` (collector, `decisions.md` D8); Phoenix reads it in `src/phoenix/utilities/project.py`.

### P2. Project page

```
registrar
«Each trace is one run of one system version on one case of this dataset. Each column is a criterion;
each badge is one evaluator's verdict with its reason. Filter by version: attributes["eval.system.version"] == "…";
by experiment: attributes["eval.experiment.id"] == "…"; failures: annotations["check-passes"].label == "fail".
Samples and scores: https://…/site/view/  Story: https://…/site/»

[check-passes ▁▃▅▇] [types-recalled ▇▇▇▇] [types-placed ▅▆▇▇]            pass rate over time

 status  kind   name                      input                      check-passes  types-recalled  …  metadata
 ok      CHAIN  run domain-registration   Model domain name regis…   fail          pass               {system.version: 7f0c9e41, experiment.id: e-2026-10-17-…, repetition: 2}
 ok      CHAIN  run domain-registration   Model domain name regis…   pass          pass               {system.version: 3b2a77d0, …}
```

Carried by: project `description` (`PUT /v1/projects/{id}`, D7); columns `name`, `input` and dynamic annotation columns (`TracesTable.tsx`); `input.value` ← `eval.input` (D8); the address as the root span's own attributes (D21); charts from annotation configs with `optimization_direction: MAXIMIZE` (release notes 2026-08-04).

### P3. Trace page

```
run domain-registration   4m 12s   $0.41   12,480 tokens
├ ▣ run domain-registration                4m 12s   [check-passes fail] [structure-matches fail] [types-recalled pass] +2
│  ├ ▣ prepare workspace                      1s
│  ├ ◆ invoke_agent tca-agent              3m 58s
│  │  ├ ● chat claude-opus-5-5               22s
│  │  ├ ▲ execute_tool write_file             0s
│  │  ├ ▲ execute_tool check                  6s
│  │  └ …
│  ├ ▣ capture workspace                      2s
│  ├ ◇ evaluate check-passes                  5s
│  ├ ◇ evaluate types-recalled                1s
│  ├ ◇ evaluate structure-matches             1s
│  └ ◇ evaluate judge-framing                 9s
│       └ ● chat claude-sonnet-5-5            8s
```

Carried by: span names; `openinference.span.kind` ← `eval.span.kind` (CHAIN, EVALUATOR); the system's AGENT, LLM and TOOL kinds from Phoenix's conversion of its GenAI-convention spans (release notes 2026-05-15); badges from span annotations on the root (release notes 2026-10-01).

### P4. Root span tabs

```
Info ────────────────────────────────────────────────────────────────────
Input (text/plain)   «Model domain name registration as a program. A registrant asks …»

Attributes ──────────────────────────────────────────────────────────────
eval.dataset.name  registrar        eval.dataset.version  d3a1f0c2…    eval.case.id       domain-registration
eval.system.name   tca-agent        eval.system.version   7f0c9e41…    eval.repetition    2
eval.experiment.id e-2026-10-17-compaction
eval.sample.url    https://…/site/view/?log_file=logs/registrar/2026-10-17T11-02-41_registrar_….eval
eval.artifact.path logs/registrar/artifacts/d3a1f0c2/domain-registration/tca-agent@7f0c9e41/2/

Events (5) ──────────────────────────────────────────────────────────────
gen_ai.evaluation.result   gen_ai.evaluation.name=check-passes   gen_ai.evaluation.score.value=0   gen_ai.evaluation.score.label=fail
                           gen_ai.evaluation.explanation=«ruff: F401 in domain/registration/type.py:3; basedpyright: 2 errors»
…

Annotations ─────────────────────────────────────────────────────────────
name               kind   label  score  explanation
check-passes       CODE   fail   0      «ruff: F401 in domain/registration/type.py:3; basedpyright: 2 errors. The workspace's check exited 1.»
types-recalled     CODE   pass   1      «31 of 31 reference types found by meaning: 29 by name, 2 by fields (Offer≈Quote, …).»
structure-matches  CODE   fail   0      «AvailabilityReply is one model with optional fields; the reference has a union of four replies.»
judge-framing      LLM    pass   1      «Outcome sentence matches; both boundaries name the reference's action, provider, one message out, one reply in.»
```

Carried by: `eval.input`, `eval.output`; `eval.*`; evaluation events (`gen-ai-events.md`, written as span events, D6); span annotations (`POST /v1/span_annotations`: `name`, `annotator_kind`, `result{label,score,explanation}`, `metadata`, `identifier`).

### P5. `capture workspace` and `evaluate <criterion>` spans

```
capture workspace                                   (zero-length, opened once the capture exists)
Output  «31 types · 29 recalled · 2 misplaced · 1 missing · 1 extra
         layer  kind              name              file                           ref
         Scalar semantic scalar   Fqdn              domain/registration/type.py    =
         …
       - Value  foreign model     AvailabilityReply integration/registrar/model.py missing
       + Thing  entity            Registrant        domain/registration/type.py    extra
         diff: --- reference +++ produced @@ …»
Attributes  eval.artifact.path  logs/registrar/artifacts/d3a1f0c2/domain-registration/tca-agent@7f0c9e41/2/

evaluate judge-framing
Input   «case registrar@d3a1f0c2/domain-registration · judged trace 7a1c… · expectation framing.json 90e1…»
Output  «{"criterion":"judge-framing","label":"pass","value":1.0,"confidence":0.92,"explanation":"…"}»
Attributes  eval.evaluator.name judge-framing   eval.evaluator.version c2d4e8a0…   eval.evaluator.validated_by e-2026-10-20-judge-framing-v1
```

Carried by: the history derived from the system's tool events (D14); `eval.evaluator.*`; the event's instrumentation scope is the evaluator (D5).

## The log viewer

Inspect's viewer, from its docs: a logs list, a samples list with task-declared columns, and per-sample Transcript, Messages, Scoring and Metadata tabs; filter by score; sort by score or across epochs; bundled statically with `inspect view bundle`.

### V1. Logs list and log header

```
registrar · 2026-10-17T11-02-41
«Dataset registrar@d3a1f0c2 run by version tca-agent@7f0c9e41 · compaction at 0.5. Each sample is a case;
each epoch is a repetition; each score is a criterion. Experiment e-2026-10-17-compaction: candidate.
Statement: changed compaction 0.7 → 0.5; decides check-passes; must not drop types-recalled, types-placed;
5 repetitions; rule: gain ≥ 0.20, no guardrail loss. Decision: KEPT, check-passes 0.60 → 1.00.»
model anthropic/claude-opus-5-5   epochs 5   samples 1   check-passes 1.00   types-recalled 1.00   types-placed 0.80 …
```

Carried by: `Task.description`, `Task.metadata` (address, experiment), `eval()` `model` = the version's model part, `epochs`; metrics per scorer.

### V2. Samples list (task view)

```
id                    epoch  input                         target                     check-passes  types-recalled  types-placed  structure-matches  judge-framing
domain-registration   1      Model domain name registrat…  31 types by layer and file  pass          pass            pass          fail               pass
domain-registration   2      Model domain name registrat…  31 types by layer and file  fail          pass            pass          fail               pass
                                                                                         [filter: failures]  [sort: across epochs]
```

Carried by: `Sample.id`, `epoch`, `Sample.input`, `Sample.target`; `ViewerConfig.task_samples_view` columns, score labels pass/fail, colour scale by direction.

### V3. Sample, Scoring tab

```
check-passes      fail   «ruff: F401 in domain/registration/type.py:3; basedpyright: 2 errors. The workspace's check exited 1.»
                         evaluator check-passes@1a2b…  kind CODE
types-recalled    pass   «31 of 31 reference types found by meaning …»          evaluator types-recalled@88c0…  kind CODE
structure-matches fail   «AvailabilityReply is one model with optional fields …»  evaluator structure-matches@…  kind CODE
judge-framing     pass   «Outcome sentence matches …»  confidence 0.92          evaluator judge-framing@c2d4…  kind LLM  validated_by e-2026-10-20-judge-framing-v1
Target   «31 types by layer and file: … (the reference's judged form)»
Answer   «31 types · 29 recalled · 2 misplaced · 1 missing · 1 extra (the produced judged form)»
```

Carried by: `Score.value`, `Score.answer`, `Score.explanation`, `Score.metadata` (`evaluator`, `evaluator_version`, `kind`, `confidence`, `validated_by`); `Sample.target`.

### V4. Sample, Metadata and Transcript tabs

```
Metadata
address        registrar@d3a1f0c2/domain-registration/tca-agent@7f0c9e41#2
trace.id       7a1c…      trace.url   https://…phoenix…/projects/registrar/traces/7a1c…
artifact       logs/registrar/artifacts/d3a1f0c2/domain-registration/tca-agent@7f0c9e41/2/
judged_form    «…»        diff   «--- reference +++ produced @@ …»        history   «…»

Transcript
model  chat claude-opus-5-5        22s   …
tool   write_file                  domain/registration/type.py …
tool   check                       exit 1 …
```

Carried by: `Sample.metadata`; the transcript written by the capture step from the exported trace (D4).

## The front door

### S0. `site/index.html`

```
TCA evaluation
How well can Type Construction Architecture development be automated, and is it getting better?

Chapter 1 · One agent, one loop
«The reference agent runs the loop under the skill, with the check as its only tool beyond files and shell.»
  Kept      the oracle          e-2026-10-15-oracle        reference 1.00 on every criterion                   [log] [Phoenix]
  Kept      compaction 0.5      e-2026-10-17-compaction    check-passes 0.60 → 1.00 · 5 reps · compaction 0.7→0.5   [log] [Phoenix]
  Rejected  skill rewrite v3    e-2026-10-12-skill-v3      types-placed 0.80 → 0.40 · 5 reps · skills 9c1e→4d07     [log] [Phoenix]

The best now
  registrar   tca-agent@7f0c9e41   check-passes 1.00 · types-recalled 1.00 · types-placed 0.80 · structure-matches 0.60 · judge-framing 1.00   [log] [Phoenix]

How to read this
  Dataset     a versioned set of cases, pinned by digest so a decision never moves.                 Inspect: task · Phoenix: project       first: registrar@d3a1f0c2
  Case        one input and the expectation a correct output meets; lives with the dataset.         Inspect: sample                         first: domain-registration
  Version     the whole system by the digest of its parts; experiments vary one part.               Inspect: model + metadata               first: tca-agent@7f0c9e41
  Trace       what one version did on one case, once; every score points at one.                   Inspect: sample at an epoch · Phoenix: trace   first: 7a1c…
  Score       one evaluator's verdict with its reason; counts only after the evaluator was validated. Inspect: score · Phoenix: annotation  first: check-passes on 7a1c…
  Experiment  versions compared on one dataset version by a rule stated before it ran.             documents beside the logs               first: e-2026-10-17-compaction
```

One file, inline CSS, no script, no build, regenerated at publish. Prose is the site narrative content; lines are records. Every number is read from a log or a decision document; every link goes to the bundled viewer or to Phoenix. A chapter renders only when it holds a decided experiment.
