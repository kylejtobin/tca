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

# Resolve the declared dependencies into the lockfile.
lock:
    {{dev}} uv lock

# Open a shell in the development container.
shell:
    {{dev}} bash

programs := "packages/python/type-construction-demo/src $(find packages/python/type-construction/tests/type_construction_engine packages/python/type-construction-http/tests/type_construction_http -name '*.py' ! -name 'test_*' ! -name '__init__.py' ! -name 'agentlib.py')"
packages := "packages/python/type-construction packages/python/type-construction-http packages/python/type-construction-demo"

# Prove the programs: the smell check, the noun lists, the types and the tests, in the container.
check:
    .agents/skills/smell-check/smell-check {{programs}}
    python3 -I .agents/skills/tca-noun-list/noun-check.py packages/python/type-construction-demo
    {{dev}} uv run --no-sync basedpyright {{packages}}
    {{dev}} uv run --no-sync pytest {{packages}} -q -W error
