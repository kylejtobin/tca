---
name: tca-python-package
description: "Creates a new Python package in this workspace in the one shape every package has: pyproject, LICENSE, README, source module, tests package, and the two root edits. Use when a new package is needed, before any file in it is written by hand."
---

# TCA Python Package

Run it:

```
.agents/skills/tca-python-package/new-package <name> <description>
```

`<name>` is the short name in lower-case words joined by hyphens, `noun-list`. `<description>` is one sentence in quotes. Everything else is derived: the distribution is `type-construction-<name>`, the module is `type_construction.<name>` with hyphens as underscores, the tests package is `type_construction_<name>`.

It writes:

```text
packages/python/type-construction-<name>/
    pyproject.toml                               the fields every package here declares; dependencies empty
    LICENSE                                      a copy of the root LICENSE
    README.md                                    the title and the description
    src/type_construction/<name>/__init__.py     empty
    src/type_construction/<name>/py.typed
    tests/type_construction_<name>/__init__.py   empty
```

and makes the two root edits the workspace glob does not: the module joins `root_packages` under `[tool.importlinter]` in `pyproject.toml`, and the package's `pyproject.toml` gets its `COPY` line in the `Dockerfile` after the last one there. It refuses if the package directory exists and changes nothing.

Afterwards: `uv add` the dependencies from inside the package directory, then `just lock`..

Tests are not included in the wheel. The world and the engine are `type-construction-world` and `type-construction-engine`, named like every other package.
