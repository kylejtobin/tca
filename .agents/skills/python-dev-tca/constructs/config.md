---
type: Construct
description: "Shape and configuration of deployment input constructed once as frozen settings."
---

# Config

```python
class VenueConfig(BaseSettings):
    """The deployment's address and credential for the clearing house."""

    model_config = SettingsConfigDict(
        frozen=True, extra="forbid", strict=False,
        validate_default=True, revalidate_instances="never",
        env_prefix="VENUE_",
    )
    url: VenueUrl
    token: SecretStr
```

Constructed:

With `VENUE_URL=https://clearing.example` and `VENUE_TOKEN=s3cret` in the environment, `VenueConfig().url` is `VenueUrl("https://clearing.example")` and `VenueConfig().token` is a `SecretStr`.

With `VENUE_URL` unset, `VenueConfig()` raises `ValidationError`.

`repr(VenueConfig().token)` is `"SecretStr('**********')"`.

In the file:

- `strict=False` is in this `model_config`: environment text constructs the typed value.
- The other settings are those of an owned model: `frozen=True`, `extra="forbid"`, `validate_default=True`, `revalidate_instances="never"`.
- Every non-secret field is a semantic scalar or a value object: `url: VenueUrl`.
- A credential is `SecretStr`, and `get_secret_value()` is called once, where the client is constructed.
- Source names come from `env_prefix`: `VENUE_URL`, `VENUE_TOKEN`.
- `VenueConfig()` is constructed once, in `main.py`, and `config` is the one place settings are read from.
- Placement: `config.py`.
