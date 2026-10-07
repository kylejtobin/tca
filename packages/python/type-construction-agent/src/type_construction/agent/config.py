from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.azure import AzureProvider
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_settings import BaseSettings, SettingsConfigDict

from type_construction.agent.domain.agent.type import (
    AnthropicProviderName,
    ApiKey,
    ApiVersion,
    AwsAccessKeyId,
    AwsProviderName,
    AwsRegion,
    AwsSecretAccessKey,
    AwsSessionToken,
    AzureEndpoint,
    AzureProviderName,
    CloudflareAccountId,
    CloudflareProviderName,
    CloudflareUrl,
    ModelName,
    OpenAIProviderName,
    Unset,
)


class OpenAI(BaseModel):
    """A model at OpenAI, and the OpenAI API key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: OpenAIProviderName
    tca_agent_model: ModelName
    openai_api_key: ApiKey

    @property
    def client(self) -> OpenAIChatModel:
        return OpenAIChatModel(
            self.tca_agent_model.root,
            provider=OpenAIProvider(api_key=self.openai_api_key.root.get_secret_value()),
        )


class Anthropic(BaseModel):
    """A model at Anthropic, and the Anthropic API key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: AnthropicProviderName
    tca_agent_model: ModelName
    anthropic_api_key: ApiKey

    @property
    def client(self) -> AnthropicModel:
        return AnthropicModel(
            self.tca_agent_model.root,
            provider=AnthropicProvider(api_key=self.anthropic_api_key.root.get_secret_value()),
        )


class Azure(BaseModel):
    """A model deployed on an Azure OpenAI resource, and that resource's key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: AzureProviderName
    tca_agent_model: ModelName
    azure_openai_endpoint: AzureEndpoint
    openai_api_version: ApiVersion
    azure_openai_api_key: ApiKey

    @property
    def client(self) -> OpenAIChatModel:
        return OpenAIChatModel(
            self.tca_agent_model.root,
            provider=AzureProvider(
                azure_endpoint=self.azure_openai_endpoint.root,
                api_version=self.openai_api_version.root,
                api_key=self.azure_openai_api_key.root.get_secret_value(),
            ),
        )


class Cloudflare(BaseModel):
    """A Workers AI model in a Cloudflare account, and that account's API token."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: CloudflareProviderName
    tca_agent_model: ModelName
    cloudflare_account_id: CloudflareAccountId
    cloudflare_api_token: ApiKey

    @property
    def url(self) -> CloudflareUrl:
        return CloudflareUrl(
            f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id.root}/ai/v1"
        )

    @property
    def client(self) -> OpenAIChatModel:
        return OpenAIChatModel(
            self.tca_agent_model.root,
            provider=OpenAIProvider(
                base_url=self.url.root,
                api_key=self.cloudflare_api_token.root.get_secret_value(),
            ),
        )


class AwsSession(BaseModel):
    """A Bedrock model in an AWS region, reached with a temporary AWS access key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: AwsProviderName
    tca_agent_model: ModelName
    aws_default_region: AwsRegion
    aws_access_key_id: AwsAccessKeyId
    aws_secret_access_key: AwsSecretAccessKey
    aws_session_token: AwsSessionToken

    @property
    def client(self) -> BedrockConverseModel:
        return BedrockConverseModel(
            self.tca_agent_model.root,
            provider=BedrockProvider(
                region_name=self.aws_default_region.root,
                aws_access_key_id=self.aws_access_key_id.root.get_secret_value(),
                aws_secret_access_key=self.aws_secret_access_key.root.get_secret_value(),
                aws_session_token=self.aws_session_token.root.get_secret_value(),
            ),
        )


class AwsKey(BaseModel):
    """A Bedrock model in an AWS region, reached with a long-lived AWS access key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: AwsProviderName
    tca_agent_model: ModelName
    aws_default_region: AwsRegion
    aws_access_key_id: AwsAccessKeyId
    aws_secret_access_key: AwsSecretAccessKey

    @property
    def client(self) -> BedrockConverseModel:
        return BedrockConverseModel(
            self.tca_agent_model.root,
            provider=BedrockProvider(
                region_name=self.aws_default_region.root,
                aws_access_key_id=self.aws_access_key_id.root.get_secret_value(),
                aws_secret_access_key=self.aws_secret_access_key.root.get_secret_value(),
            ),
        )


class AwsBearer(BaseModel):
    """A Bedrock model in an AWS region, reached with a Bedrock API key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    tca_agent_provider: AwsProviderName
    tca_agent_model: ModelName
    aws_default_region: AwsRegion
    aws_bearer_token_bedrock: ApiKey

    @property
    def client(self) -> BedrockConverseModel:
        return BedrockConverseModel(
            self.tca_agent_model.root,
            provider=BedrockProvider(
                region_name=self.aws_default_region.root,
                api_key=self.aws_bearer_token_bedrock.root.get_secret_value(),
            ),
        )


class ModelProvider(
    RootModel[
        Annotated[
            OpenAI | Anthropic | Azure | Cloudflare | AwsSession | AwsKey | AwsBearer,
            Field(union_mode="left_to_right"),
        ]
    ]
):
    """The provider of the model the deployment names, with the credentials that provider takes."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def client(self) -> OpenAIChatModel | AnthropicModel | BedrockConverseModel:
        return self.root.client


class AgentConfig(BaseSettings):
    """The deployment's model and its provider, and every provider's credentials by its own name."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
    )
    tca_agent_provider: (
        OpenAIProviderName
        | AnthropicProviderName
        | AzureProviderName
        | AwsProviderName
        | CloudflareProviderName
    )
    tca_agent_model: ModelName
    openai_api_key: ApiKey | Unset = Unset()
    anthropic_api_key: ApiKey | Unset = Unset()
    azure_openai_endpoint: AzureEndpoint | Unset = Unset()
    openai_api_version: ApiVersion | Unset = Unset()
    azure_openai_api_key: ApiKey | Unset = Unset()
    aws_default_region: AwsRegion | Unset = Unset()
    aws_access_key_id: AwsAccessKeyId | Unset = Unset()
    aws_secret_access_key: AwsSecretAccessKey | Unset = Unset()
    aws_session_token: AwsSessionToken | Unset = Unset()
    aws_bearer_token_bedrock: ApiKey | Unset = Unset()
    cloudflare_account_id: CloudflareAccountId | Unset = Unset()
    cloudflare_api_token: ApiKey | Unset = Unset()

    @property
    def provider(self) -> ModelProvider:
        return ModelProvider.model_validate(self)
