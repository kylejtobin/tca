import httpx
from pydantic import BaseModel, ConfigDict

from type_construction.registrar.integration.registrar.model import ProviderKey, ProviderUrl


class Registrar(BaseModel):
    """The registrar, at its address, under this program's key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    url: ProviderUrl
    key: ProviderKey

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.url.root,
            auth=(self.key.root.get_secret_value(), ""),
            headers=(("Content-Type", "application/json"),),
        )
