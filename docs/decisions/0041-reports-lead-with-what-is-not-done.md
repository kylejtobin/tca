# 0041. Reports lead with what is not done, and checks run only as just declares

Status: accepted

## Context

Reports that led with what passed hid a weakened design behind a list of green results. Ad hoc test invocations produced results the declared check did not. A check that runs in one place and not another lets a defect through the place it does not run.

## Rejected

Three lists of checks, one in the justfile, one in the commit hook and one in CI. Removing a check from the hook to match a shorter justfile.

## Decision

A report states first what is not done and why, whole. Checks are two recipes: `just check`, the smell check on every program, ruff check, ruff format, basedpyright strict, import-linter and bandit on the five packages and `tests`, and pytest over `packages/python`; and `just audit`, the lockfile check, pip-audit, semgrep and the pinned-image check. The commit hook and CI run those two recipes and no other command; `just` is a locked dev dependency, so the recipes run the same from the hook, CI and a shell. A passing check is not proof of the design, and a result from any other command is not reported. A vulnerability in a tool we run and never ship is ignored by id in the recipe, with the pin that holds it named beside the ignore.

## Evidence

`uv run just check` and `uv run just audit` exit 0 on the host, with the import contracts reporting three kept, none broken, thirteen tests passing, and pip-audit reporting no vulnerability beyond the one ignored; the commit hook ran both on commit c1db904.

## Consequences

A report whose first line is a pass is a defect in the report. A check is added to a recipe or it does not exist; a hook or a CI step that runs a command the justfile does not is a defect. Refuted by a check that cannot run outside CI; none identified.
