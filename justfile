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

# The gate: every check the commit hook and CI run, and nothing they do not.
check:
    .agents/skills/smell-check/smell-check {{programs}}
    uv run ruff check {{packages}} tests
    uv run ruff format --check {{packages}} tests
    uv run basedpyright {{packages}}
    uv run lint-imports
    uv run bandit -c pyproject.toml -q -r {{packages}}
    uv run pytest -q

# The supply chain: the lockfile, known vulnerabilities, code patterns, pinned images.
# semgrep runs from its own locked group in an isolated environment, since its exact
# OpenTelemetry pin must not hold the engine's dependency back.
audit:
    uv lock --check
    uv run pip-audit
    uv run --isolated --only-group audit semgrep scan --config p/python --config p/secrets --error --quiet -j 1 {{packages}}
    ! grep -hE "^FROM |^COPY --from=|image: " Dockerfile compose.yaml | grep -vE "@sha256:[0-9a-f]{64}"
