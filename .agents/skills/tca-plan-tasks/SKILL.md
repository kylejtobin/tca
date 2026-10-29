---
name: tca-plan-tasks
description: Maintain a minimal, token-efficient, Markdown-based Kanban for AI agent task execution using docs/plan/TASKS.md. Use when an agent needs to create or update the task board, capture newly discovered work, claim tasks, change task states, resolve dependencies, or remove completed and obsolete tasks. Also use when resuming execution from an existing TASKS.md. This skill governs lightweight task coordination and continuous pruning, not project planning, architecture design, or detailed task specifications.
---

## Overview

`docs/plan/TASKS.md` is a minimal, token-efficient Kanban system for coordinating agent work. It tracks only outstanding, actionable tasks—not designs, detailed plans, discussions, or history. Tasks are continuously added, advanced, and removed, keeping the file small, current, and focused on execution.

## Rules

1. One file. `docs/plan/TASKS.md` is the single source of truth for outstanding tasks.
2. Four states. `Todo`, `Doing`, `Review`, and `Blocked`, represented by Markdown headings. Omit empty sections.
3. One line per task. Use `- [ ] ID | Action | optional:metadata`.
4. Actionable outcomes. Tasks describe specific, verifiable work, not vague intentions or planning activities.
5. Execute, don't elaborate. Keep design, detailed plans, reasoning, and discussions outside `docs/plan/TASKS.md`. Reference authoritative sources when necessary.
6. Move to change state. Each task exists in exactly one section. Claim ownership when starting work.
7. Minimal dependencies. Record blockers, prerequisites, or ownership only when necessary, using compact metadata.
8. Delete aggressively. Remove completed, canceled, obsolete, or unnecessary tasks immediately. Git preserves history.
9. Continuously prune. Consolidate duplicates, eliminate stale dependencies, and simplify tasks as work progresses.
10. Keep it lean. No progress narratives, completion archives, speculative tasks, redundant metadata, or additional infrastructure.

## Example

`docs/plan/TASKS.md`

```

# TASKS.md

## Todo
- [ ] T12 | Remove obsolete event adapters
- [ ] T13 | Implement typed event dispatch | after:T12
- [ ] T14 | Add event validation tests

## Doing
- [ ] T11 | Refactor event contracts | agent:claude

## Review
- [ ] T10 | Validate declarative construction

## Blocked
- [ ] T09 | Resolve schema incompatibility | needs:decision

```

## Gotchas

- **Task accumulation:** Agents readily add tasks but rarely remove them. Every board update should also eliminate completed, obsolete, duplicate, and unnecessary work.
- **Planning instead of execution:** Agents expand simple tasks into subtasks, investigations, and elaborate plans. Keep the board focused on executable work and perform the work.
- **Premature decomposition:** A task doesn't need to become five tasks just because it has five implementation steps. Split only when the resulting work genuinely needs independent tracking.
- **Completion avoidance:** Agents leave finished work in Review, add follow-up validation tasks, or preserve completed checkboxes. Verify the outcome and delete the task.
- **Documentation creep:** Task descriptions gradually accumulate reasoning, implementation instructions, and progress reports. Keep each task to one line and reference authoritative sources.
- **Stale state:** Agents complete work without updating the board. Update task state as part of the work itself.
- **Artificial blockers:** Agents invent dependencies, approvals, or investigations that aren't actually necessary. Block only when execution genuinely cannot proceed.
- **Board maintenance as work:** Agents spend time reorganizing, categorizing, and discussing the Kanban instead of executing tasks. Maintenance should be a trivial side effect of execution.
