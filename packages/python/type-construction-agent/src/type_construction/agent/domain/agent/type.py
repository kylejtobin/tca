from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel, SecretStr


class PromptText(RootModel[str]):
    """The words a person gives the agent."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class AnswerText(RootModel[str]):
    """The words the agent gives back for a prompt."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str


class ModelName(RootModel[str]):
    """The name a model provider knows one of its models by."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ApiKey(RootModel[SecretStr]):
    """The key a model provider knows this program by; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class AzureEndpoint(RootModel[str]):
    """The address of an Azure OpenAI resource."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^https://\S+$")


class ApiVersion(RootModel[str]):
    """The version of the Azure OpenAI interface a resource is spoken to in."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class AwsRegion(RootModel[str]):
    """The AWS region whose Bedrock models are spoken to."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z]{2}(-[a-z]+)+-\d+$")


class AwsAccessKeyId(RootModel[SecretStr]):
    """The identity of an AWS access key; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class AwsSecretAccessKey(RootModel[SecretStr]):
    """The secret of an AWS access key; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class AwsSessionToken(RootModel[SecretStr]):
    """The session token of a temporary AWS access key; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class CloudflareAccountId(RootModel[str]):
    """The identity of the Cloudflare account whose Workers AI models are spoken to."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[0-9a-f]{32}$")


class CloudflareUrl(RootModel[str]):
    """The address of a Cloudflare account's OpenAI-compatible Workers AI interface."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(
        pattern=r"^https://api\.cloudflare\.com/client/v4/accounts/[0-9a-f]{32}/ai/v1$"
    )


class Unset(RootModel[str]):
    """A setting the environment does not give."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(default="", max_length=0)


class OpenAIProviderName(StrEnum):
    """OpenAI, as a deployment names the provider of its model."""

    OPENAI = "openai"


class AnthropicProviderName(StrEnum):
    """Anthropic, as a deployment names the provider of its model."""

    ANTHROPIC = "anthropic"


class AzureProviderName(StrEnum):
    """Azure, as a deployment names the provider of its model."""

    AZURE = "azure"


class AwsProviderName(StrEnum):
    """AWS, as a deployment names the provider of its model."""

    AWS = "aws"


class CloudflareProviderName(StrEnum):
    """Cloudflare, as a deployment names the provider of its model."""

    CLOUDFLARE = "cloudflare"


class SkillName(RootModel[str]):
    """The name an agent's words are known by, the same as their directory."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")


class SkillDescription(RootModel[str]):
    """What an agent's words are for, and when they are used."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SkillBody(RootModel[str]):
    """The words an agent is given."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SkillLocation(StrEnum):
    """Where each agent's own words are kept, within the package."""

    TCA_AGENT = "prompts/agents/tca-agent/SKILL.md"


class SkillLibrary(StrEnum):
    """Where the skills an agent may load are kept, within the package."""

    SKILLS = "prompts/skills"
