"""Classes that hold each other, which the proof refuses as a cycle: not a program a run
accepts, so a test places them by hand, unproven, and the run must report the deadlock as a
failure, not as the business refusing."""

from pydantic import Field

from type_construction.world import Config, Fact, Reply, Request, Route, Scalar


class Name(Scalar[str]):
    """What is asked about."""

    root: str = Field(min_length=1)


class Ask(Request):
    """What arrives."""

    name: Name


class Egg(Fact):
    """A fact that holds the fact that holds it."""

    chicken: "Chicken"  # noqa: UP037
    ask: Ask


class Chicken(Fact):
    """The other half."""

    egg: Egg


class Hatched(Fact):
    """What the route would conclude."""

    egg: Egg


class Told(Reply[Hatched]):
    """What would leave."""


class Hatch(Route[Ask, Told]):
    """A route that can never construct."""


class Deployment(Config):
    """No party."""
