# Package tests

## Mandatory preparation

Before creating, changing, or reviewing tests, agents MUST read `.agents/skills/tca-testing/SKILL.md` completely, then the complete `docs/product.md` and `docs/TCA_ARCHITECTURAL_FOUNDATIONS.md`. Paths are relative to the repository root. Read `docs/ADR.md` completely when it exists. Current human instructions and approved contracts govern; tests and ADRs MUST NOT contradict the current architecture. Old tests and implementations are not alternate authority.

## Placement

Use `tests/<package_namespace>/unit/`, `integration/`, and `acceptance/`. Create categories only when needed. Name test modules `test_<behavior>.py`; keep domain declarations and small support helpers beside their consuming tests. Tests MUST NOT import another test module. Cross-package scenarios belong to the package exposing the tested public behavior. World tests MUST NOT import the engine.

This file MUST match `.agents/skills/tca-testing/AGENTS.md` byte for byte in every package. Edit the canonical file and synchronize all copies together.

## Execution

From the package directory:

- Package: `uv run --all-packages pytest tests -q`
- Focused: `uv run --all-packages pytest tests -q -k '<test_name>'`

From the repository root:

- Instruction parity: `python scripts/check_test_standards.py`
- All tests: `uv run --all-packages pytest -q`
- Repository gate: `just check`

## Authority and completion

Agents MUST obtain explicit human authorization before weakening or removing established acceptance expectations. Present contradictions with the approved design as concrete examples; MUST NOT change the contract to accommodate the implementation. Routine additions and refactoring that preserve expectations need no additional approval.

Completion reports MUST identify guarantees exercised, exact commands and outcomes, demonstrated defect detection, and unverified behavior. Collection failures, missing implementations, and unexecuted tests MUST remain explicit; they do not establish acceptance.
