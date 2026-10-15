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

# Lint, type-check, enforce the dependency contracts, and verify the lockfile and the pinned images.
lint:
    {{dev}} ruff check packages tests
    {{dev}} ruff format --check packages tests
    {{dev}} basedpyright
    {{dev}} lint-imports
    {{dev}} uv lock --check
    {{dev}} bash -c '! grep -hE "^FROM |^COPY --from=|image: " Dockerfile compose.yaml | grep -vE "@sha256:[0-9a-f]{64}"'

# Scan the packages' source for procedure.
smell:
    {{dev}} bash -c '.agents/skills/smell-check/smell-check packages/python/*/src'

# Run every check.
check: lint smell test

# Open a shell in the development container.
shell:
    {{dev}} bash
