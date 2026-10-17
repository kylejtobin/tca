from opentelemetry.distro import OpenTelemetryConfigurator

from type_construction.agent import AgentConfig, chat

telemetry = OpenTelemetryConfigurator().configure()  # pyright: ignore[reportUnknownMemberType]


def main() -> None:
    return chat(AgentConfig())  # pyright: ignore[reportCallIssue]
