---
name: tca-plan-tasks
description: Derive actionable tasks from TCA's intended outcomes, product requirements, architecture, decisions, and current implementation, and maintain them in docs/plan/TASKS.md. Use when identifying outstanding work, updating or claiming tasks, resolving blockers, or resuming execution. Keep detailed designs and strategic roadmapping outside the task board.
---

# TCA Tasks

`docs/plan/TASKS.md` coordinates outstanding work toward the intended outcome.
Understand the work first; compress its description afterward.

## Derive the work

1. Read the relevant roadmap outcome, product requirements, architecture,
   established decisions and corrections, and actual implementation.
   Establish what is required and what already works.
2. Identify the remaining gaps. For each task, determine the concrete change
   required and the observable result that establishes completion.
   Split work only when it needs independent execution or review.
3. Write a compact action using the established concepts and relationships.
   Reference the relevant document section for supporting detail.
   Check whether literal completion could still miss the intended result;
   revise the task if it could.

## Board format

- Use one file: `docs/plan/TASKS.md`.
- Use headings `Todo`, `Doing`, `Review`, and `Blocked`; omit empty sections.
- Write one line per task:
  `- [ ] ID | Title | Action | optional:metadata`.
- Use a short, specific title, usually 2–5 words.
- Make the action specific and verifiable. Preserve the meaning needed to
  perform the work correctly; keep detailed reasoning and designs elsewhere.
- Add references, dependencies, ownership, or blockers only when useful.

## Maintain during execution

Move each task between sections as its state changes; keep it in exactly
one section. Claim ownership when starting work. Block only when execution
genuinely cannot proceed.

Verify completed work against its intended result, then delete the task.
Remove canceled, superseded, and duplicate work; Git preserves history.
Keep maintenance a small part of execution, without progress narratives
or completion archives.

## Example

```markdown
# Tasks

## Todo
- [ ] T12 | Typed configuration | Construct declared application settings through Pydantic Settings before dependent resources open; invalid required values prevent startup. | ref:docs/architecture/DESIGN.md§6.1
- [ ] T13 | Evidence continuation | Resume an activated Activity when later events supply its missing operands through declared supply and selection relationships. | ref:docs/architecture/DESIGN.md§6.3

## Doing
- [ ] T11 | Public value exports | Export the existing Model and Root bases from type_construction and verify imports from the installed wheel. | agent:claude
```

## Gotchas

- **Compression before understanding:** A concise task can still assign
  the wrong work. Derive it from the outcome, relevant documents, and code
  before shortening it.
- **Implementation mistaken for intent:** Existing machinery and passing
  tests do not determine what is required. Establish the expected result
  independently.
- **Steps mistaken for tasks:** Reading, implementation, and verification
  usually belong to the same task. Track them separately only when they
  need independent coordination.
- **Detail replacing clarity:** Preserve the essential change and result
  in the action; reference supporting specifications rather than copying
  them into the board.
