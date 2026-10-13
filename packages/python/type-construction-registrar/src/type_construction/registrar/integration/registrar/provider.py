import httpx
from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.type import (
    BlankPassword,
    FieldName,
    MediaType,
    ProviderKey,
    ProviderUrl,
)


class Registrar(BaseModel):
    """The registrar, at its address, under this program's key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
    )
    url: ProviderUrl
    key: ProviderKey

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.url.root,
            auth=(self.key.root.get_secret_value(), BlankPassword().root),
            headers=((FieldName.CONTENT_TYPE, MediaType.JSON),),
            limits=httpx.Limits(max_keepalive_connections=0),
        )
