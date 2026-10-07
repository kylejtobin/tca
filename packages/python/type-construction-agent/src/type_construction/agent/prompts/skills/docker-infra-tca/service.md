---
type: Construct
description: "The one container the code runs in: the image, the code mounted over it, and the configuration given at run time. Holds the build, the env_file, the environment and the mount. Lives in compose.yaml."
---

```yaml
# compose.yaml
services:
  dev:
    build:
      context: .
      args:
        UID: ${UID:-1000}
        GID: ${GID:-1000}
    env_file:
      - path: .env
        required: false
    environment:
      PYDANTIC_AI_NO_BANNER: "1"
    volumes:
      - .:/workspace
    init: true
```
