import logfire

from type_construction.agent import AgentConfig, chat
from type_construction.agent.integration.pydantic_ai.model import AgentName

telemetry = logfire.configure(
    send_to_logfire="if-token-present",
    service_name=AgentName.TCA_AGENT,
    console=False,
)


def main() -> None:
    return chat(AgentConfig())  # pyright: ignore[reportCallIssue]
