---
name: tca-plan-roadmap
description: Maintain a minimal, token-efficient, outcome-driven roadmap using docs/plan/ROADMAP.md and rolling Now, Next, and Later horizons. Use when creating or updating an outcome roadmap, establishing strategic priorities, progressively refining outcomes, incorporating new evidence, moving outcomes between horizons, or removing achieved, obsolete, or superseded outcomes. Also use when reviewing or revising strategic direction during ongoing project execution. This skill governs desired outcomes and their evolution, not implementation planning, task management, or execution tracking.
---
# Outcome-Driven Roadmap

## Overview

`docs/plan/ROADMAP.md` is a minimal, token-efficient, outcome-driven roadmap that organizes desired results across three rolling horizons: Now, Next, and Later. Outcomes are progressively refined as evidence accumulates and they approach execution, while priorities continuously evolve as new information emerges. The roadmap tracks what the organization intends to achieve, not how it will be implemented, and stays focused through continuous refinement, reprioritization, and removal of achieved or obsolete outcomes.

## Rules

1. One file. `docs/plan/ROADMAP.md` is the single source of truth for intended outcomes.
2. Three horizons. `Now`, `Next`, and `Later`, represented by Markdown headings. Omit empty sections.
3. One line per outcome. Use `- ID | Outcome | optional:metadata`.
4. Outcomes, not outputs. Describe the measurable change or value sought, not features, deliverables, or tasks.
5. Progressive refinement. Keep distant outcomes broad and refine them as evidence accumulates and they approach execution.
6. Move to change horizons. Each outcome exists in exactly one horizon. Horizons reflect priority and readiness, not fixed deadlines.
7. Evidence-driven evolution. Add, refine, split, consolidate, or reprioritize outcomes as learning changes what matters.
8. Separate strategy from execution. Keep tasks, implementation details, designs, and detailed plans outside `docs/plan/ROADMAP.md`.
9. Delete aggressively. Remove achieved, abandoned, superseded, or irrelevant outcomes. Git preserves history.
10. Keep it lean. No progress narratives, historical archives, speculative detail, or redundant metadata.

## Example

`docs/plan/ROADMAP.md`

```

# ROADMAP.md

## Now
- O01 | Reduce customer onboarding time from 5 days to 1
- O02 | Increase self-service issue resolution from 40% to 75%

## Next
- O03 | Reduce customer churn by 25%
- O04 | Improve deployment reliability and recovery speed

## Later
- O05 | Enable customers to configure their own workflows
- O06 | Expand adoption into underserved market segments

```

## Gotchas

- **Outputs masquerading as outcomes:** "Implement authentication" is a deliverable, not an outcome. Describe the resulting improvement in security, access, or user experience.
- **Premature precision:** Agents invent metrics, targets, dates, or implementation details to make distant outcomes appear well-defined. Preserve uncertainty until evidence justifies refinement.
- **Horizons becoming schedules:** Agents interpret Now, Next, and Later as fixed delivery periods. Horizons express relative priority and readiness, not calendar commitments.
- **Roadmap accumulation:** Agents continually add desirable outcomes without removing those that have been achieved, superseded, or deprioritized beyond relevance. Prune as actively as you add.
- **Features replacing strategy:** Agents turn outcomes into feature lists, technical milestones, or implementation sequences. Those belong in execution planning, not the roadmap.
- **Refinement becoming expansion:** Progressive refinement should improve the definition of the desired result, not generate more documentation or subdivide outcomes unnecessarily.
- **False certainty:** Agents treat proposed outcomes and targets as established facts. Preserve the distinction between strategic intent, assumptions, and validated evidence.
- **Execution detail leaking upward:** Agents copy tasks and implementation progress into the roadmap. Use execution evidence to refine outcomes, not to duplicate the Kanban.
- **Treating the roadmap as immutable:** Agents preserve previously agreed priorities even when learning contradicts them. Reprioritize, revise, consolidate, or delete outcomes as evidence changes.
- **Confusing completion with delivery:** Shipping a feature does not mean the intended outcome was achieved. Evaluate the actual result before removing the outcome.
