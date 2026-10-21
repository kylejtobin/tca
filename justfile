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

programs := "packages/python/type-construction-demo/src"
packages := "packages/python/type-construction-world packages/python/type-construction-engine packages/python/type-construction-cli packages/python/type-construction-http packages/python/type-construction-demo"

# Prove the programs: the smell check and the types, in the container.
check:
    .agents/skills/smell-check/smell-check {{programs}}
    {{dev}} uv run --no-sync basedpyright {{packages}}
