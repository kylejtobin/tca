# Package tests

## Mandatory preparation

Before creating, changing, or reviewing tests, read `.agents/skills/tca-testing/SKILL.md` completely, then the complete `docs/product.md` and `docs/architecture/DESIGN.md`. Read applicable ADRs when present. All paths are relative to the repository root.

Current human instructions and approved contracts govern. Tests and ADRs MUST NOT contradict the current architecture. Existing tests and implementations are not alternate authorities.

## Placement

Use `tests/<package_namespace>/unit/`, `integration/`, and `acceptance/`. Create categories only when needed.

Name test modules `test_<behavior>.py`. Keep domain declarations and small support helpers beside their consuming tests. Tests MUST NOT import other test modules.

Test the unified framework through its public `type_construction` API. Value-foundation tests remain independent of messaging and execution integrations.

Every package's `tests/AGENTS.md` MUST match `.agents/skills/tca-testing/TEST_DIR_AGENTS.md` byte for byte. Edit the canonical file and synchronize all copies together.

## Execution

Set up the environment from the repository root against the lockfile:

```bash
uv sync --locked --all-packages
uv run which pytest
```

The environment's `pytest` MUST be used, not a same-named host tool.

From the package directory:

- Package tests: `uv run pytest tests -q`
- Focused tests: `uv run pytest tests -q -k '<test_name>'`

From the repository root:

- Instruction parity: `python scripts/check_test_standards.py`
- All tests: `uv run --all-packages pytest -q`
- Repository gate: `just check`

Run focused tests during development and the repository gate before declaring work complete. Missing tests, collection failures, and missing implementations MUST remain visible; do not conceal them with skips or stubs.

## Authority and completion

Obtain explicit human authorization before weakening or removing established acceptance expectations. Present contradictions with the approved design as concrete examples. Do not change the contract to accommodate the implementation. Routine additions and refactoring that preserve expectations require no additional authorization.

Required quality gates MUST pass before work is declared complete. Investigate failures and flaky tests; do not normalize retries or weaken assertions to obtain a passing result.

Completion reports MUST identify guarantees exercised, exact commands and outcomes, demonstrated defect detection, and unverified behavior. Collection failures, missing implementations, and unexecuted tests MUST remain explicit; they do not establish acceptance.
