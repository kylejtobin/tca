---
type: Construct
description: "The one way in: each action one recipe, one command run in the service. Holds recipes. Lives in justfile."
---

```just
# justfile
set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

export UID := `id -u`
export GID := `id -g`

dev := "docker compose run --rm dev"

# List the recipes.
default:
    @just --list

# Build the development image with the locked dependencies.
build:
    docker compose build

# Run the tests.
test:
    {{dev}} pytest

# Lint and type-check.
lint:
    {{dev}} ruff check packages/python
    {{dev}} basedpyright

# Scan the packages' source for procedure.
smell:
    {{dev}} bash -c '.agents/skills/smell-check/smell-check packages/python/*/src'

# Run every check.
check: lint smell test

# Open a shell in the development container.
shell:
    {{dev}} bash

# Ask the TCA agent a question.
ask prompt:
    {{dev}} python -c 'import sys; from type_construction.agent import Prompt, run_sync; print(run_sync(Prompt(text=sys.argv[1])).text.root)' "$1"
```
