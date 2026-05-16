#!/usr/bin/env bash
# scripts/compose.sh — env-aware docker compose dispatch.
#
# Usage: scripts/compose.sh <env> [docker-compose-args...]
#
#   env=dev → compose.yml + compose.dev.override.yml (+ local override if present)
#   env=*   → compose.yml (+ local override if present)
#
# The optional local override `compose.local.override.yml` is layered on
# every invocation when the file exists on disk. It is gitignored.
#
# Invoked by justfile recipes. The bash logic lives here rather than in a
# justfile recipe so shellcheck can lint it correctly.

set -euo pipefail

local_override_args() {
	if [ -f compose.local.override.yml ]; then
		printf -- "-f\ncompose.local.override.yml\n"
	fi
}

if [ $# -lt 1 ]; then
	echo "usage: $0 <env> [docker-compose-args...]" >&2
	exit 2
fi

env=$1
shift

case "$env" in
	dev)
		# shellcheck disable=SC2046 # local_override_args emits 0 or 2 tokens
		exec docker compose -f compose.yml -f compose.dev.override.yml \
			$(local_override_args) --env-file "env/.env.dev" "$@"
		;;
	*)
		# shellcheck disable=SC2046 # local_override_args emits 0 or 2 tokens
		exec docker compose -f compose.yml \
			$(local_override_args) --env-file "env/.env.$env" "$@"
		;;
esac
