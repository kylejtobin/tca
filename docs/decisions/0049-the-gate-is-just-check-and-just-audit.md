# 0049. The gate is `just check` and `just audit`; the commit hook and CI run them and nothing else

Status: accepted

## Context

A check that runs in one place and not another lets a defect through the place it does not run. The justfile ran the smell check and basedpyright; the commit hook also ran ruff, bandit, semgrep and pip-audit; CI ran a third list.

## Rejected

Removing ruff and bandit from the hook so the hook matched the justfile. Keeping three lists.

## Decision

`just check` is the smell check on every program, ruff check, ruff format, basedpyright strict, import-linter and bandit, on the five packages and `tests`. `just audit` is the lockfile check, pip-audit, semgrep and the pinned-image check. The commit hook runs `just check` on every commit and `just audit` when the lockfile, the project file, the images or a package change. CI runs both. `just` is a locked dev dependency, `rust-just`, so the recipes run the same from the hook, CI and a shell. A vulnerability in a tool we run and never ship is ignored by id in the recipe, with the pin that holds it named beside the ignore.

## Evidence

The hook refused a commit on findings the justfile could not see: nine asserts, a boolean parameter, eight unused parameters and two complexity limits. After the engine and CLI rewrite, `uv run just check` and `uv run just audit` both exit 0 on the host; the import contracts report three kept, none broken.

## Consequences

A check is added to a recipe or it does not exist. A hook or a CI step that runs a command the justfile does not is a defect. Refuted by a check that cannot run outside CI; none identified.
