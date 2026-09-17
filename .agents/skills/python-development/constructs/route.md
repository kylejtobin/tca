---
type: Reference
description: How transport ingress constructs typed input and projects declared output. Read when implementing an HTTP, CLI, message, stream, or framework entrypoint.
---

# Route

## Use

Use where a transport representation enters or leaves the program. A route is a frozen Pydantic model whose construction completes one transport crossing.

`Route` is an admitted edge suffix: it identifies the crossing rather than claiming another domain meaning. It is not permission for role-named domain models.

## Required Form

```python
class FillRoute(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    fill: Fill = Field(
        validation_alias=AliasPath("data", "payload")
    )

    @classmethod
    def receive(cls, raw: str) -> "FillRoute":
        return cls.model_validate_json(raw)


class FillReplyRoute(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    recorded: PositionRecorded

    def emit(self) -> str:
        return FillBooked(
            sequence=self.recorded.sequence,
            net_quantity=self.recorded.position.net_quantity,
        ).model_dump_json(by_alias=True)


route = FillRoute.receive(raw)
```

The [composition-root callback](composition-root.md) returns `FillReplyRoute` holding the interpreter's `PositionRecorded` fact once. `emit` projects its sequence and net quantity into `FillBooked` and serializes only that contract, not the recorded position history. No computed fields or staged successor are needed.

- Construct exactly one route from the whole transport representation.
- Let the route's annotated domain, foreign, or contract field recursively construct the ingress value. Here `data.payload` already has the domain `Fill` shape and meaning; a foreign model or lift would duplicate that construction.
- Expose that constructed field to the transformation, transition, or interpreter that consumes it.
- Use a separate egress route holding the constructed fact from which it projects the declared outbound contract.
- Register `FillRoute.receive` as the framework's input constructor and `FillReplyRoute.emit` as its output serializer. The one-expression callback at the [composition-root site](composition-root.md) consumes the constructed route fields and returns the reply route; the route itself contains no domain execution.
- Keep authentication extraction, status codes, headers, and protocol framing inside the route when they are transport facts.

## Do Not

- decide domain policy
- construct a successor state
- execute an action
- hold current state or a concrete client
- parse fields by hand when Pydantic's declared construction graph expresses the transport
- pass transport wrappers into domain constructs
- perform a domain transformation; projecting already-declared facts into an outbound contract is egress, not a new domain calculation
- assemble reply dictionaries or selectively include/exclude semantic fields
