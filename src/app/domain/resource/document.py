"""The doctrine document: a Claude-Code markdown file lifted whole as the foreign model it is.

A doctrine resource is authored as a `.md` file in Claude-Code's format (a YAML frontmatter block
above a markdown body). This model is that file's shape, lifted in one crossing by
`model_validate_context`, the markdown peer of `model_validate_json`. The document names no MCP type:
the wire types are assembled at the route, where the program meets the wire.
"""

from importlib.resources import files
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, RootModel


class ResourceName(RootModel[str], frozen=True):
    """A doctrine resource's name, from frontmatter: the human-readable label shown in discovery."""

    root: str = Field(min_length=1)


class ResourceDescription(RootModel[str], frozen=True):
    """What a doctrine resource holds and when to read it, from frontmatter."""

    root: str = Field(min_length=1)


class ResourceBody(RootModel[str], frozen=True):
    """A doctrine resource's markdown body, the text served whole on read."""

    root: str = Field(min_length=1)


class Document(BaseModel):
    """One Claude-Code markdown document lifted whole: its frontmatter name and description and its
    markdown body. Its existence as a `Document` is the proof the file's format held; it carries the
    facts the route reads at the wire boundary, and names no MCP type itself."""

    model_config = ConfigDict(frozen=True, extra="ignore")
    name: ResourceName
    description: ResourceDescription
    body: ResourceBody

    @classmethod
    def model_validate_context(cls, path: str) -> Self:
        """Read a Claude-Code markdown file bundled in the `app` package and validate it, the markdown
        peer of `model_validate_json`. The frontmatter/body split is the wire crossing, done here at
        the named constructor, so `model_validate` only receives the structured mapping. The path is
        package-relative and resolved through `importlib.resources`, so it loads from the wheel."""
        __tracebackhide__ = True
        _, _, rest = files("app").joinpath(path).read_text().partition("---\n")
        front, _, body = rest.partition("\n---\n")
        return cls.model_validate({**yaml.safe_load(front), "body": body.strip()})
