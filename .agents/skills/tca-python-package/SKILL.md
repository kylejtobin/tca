---
name: tca-python-package
description: Maintain TCA's Python distribution, module boundaries, public exports, and build configuration. Use when changing package structure, dependencies, import paths, or distribution metadata, or deciding whether functionality needs a separate package.
---

# TCA Python Package

Read `docs/architecture/DESIGN.md` sections 3 and 5 before changing package boundaries.

Maintain one framework distribution, `type-construction`, in
`packages/python/type-construction/`, with import namespace `type_construction`.

- Keep `Model` and `Root` in `src/type_construction/models.py`, export them from
  `src/type_construction/__init__.py`, and retain the package-level `py.typed` marker.
- Add internal modules according to actual dependencies and implemented contracts.
  Semantic distinctions alone do not justify distributions or empty module trees.
- Keep application packages separate from the framework. Create an extension
  distribution only when independent use or release requirements justify it.
- Declare dependencies where consumed. Use `uv add` from the package directory and
  regenerate `uv.lock`; do not add dependencies for unimplemented functionality.
- Keep manifests, Docker manifest copies, CI, test instructions, and public imports
  consistent with the package structure. Preserve license and typing metadata.

Run `just check` and `uv build --package type-construction`. Inspect the wheel and
source distribution and verify public imports from an installed wheel outside the
source tree. Report missing tests and unavailable checks explicitly.
