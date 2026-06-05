---
paths:
  - "**/config.py"
---

# config — typed, frozen startup proof

Derived from the Config construct in `docs/type-construction-architecture.md`. A config is a
frozen `BaseSettings` model that constructs typed fields from the environment, so
configuration is proven the moment the program starts. Each field is a declared type, never
a bare primitive where a scalar belongs. The config root is constructed once, frozen, and
injected by the composition root.

    class FeedConfig(BaseSettings):
        model_config = ConfigDict(frozen=True, extra="forbid")
        socket_url: SocketUrl
        store_dsn: StoreDsn

**The breaks this file forbids:**
- A bare primitive field where a semantic scalar belongs (escaped).
- A scattered `os.environ` read or settings dict elsewhere in the program — the environment
  is read here and only here.
