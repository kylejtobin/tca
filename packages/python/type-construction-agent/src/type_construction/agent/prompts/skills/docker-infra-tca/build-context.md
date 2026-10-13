---
type: Construct
description: "What the build may see: everything the image does not need, left out. Holds paths. Lives in .dockerignore."
---

```text
# .dockerignore
.git
.env
.venv
**/__pycache__
**/.pytest_cache
.ruff_cache
dist
```
