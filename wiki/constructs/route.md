---
type: Construct
description: A frozen model of one transport crossing, constructing ingress and projecting egress.
---

# Route

## Definition

Where a transport representation enters or leaves the program. A route is a frozen model whose construction completes one transport crossing. `Route` is an admitted edge suffix: it identifies the crossing rather than claiming another domain meaning, and it is not permission for role-named domain models.

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
```

The [composition-root callback](./composition-root.md) returns `FillReplyRoute` holding the interpreter's `PositionRecorded` fact once. `emit` projects its sequence and net quantity into `FillBooked` and serializes only that contract, not the recorded position history.

- Exactly one route constructs from the whole transport representation.
- The route's annotated domain, foreign, or contract field recursively constructs the ingress value. Here `data.payload` already has the domain `Fill` shape and meaning, so a foreign model or lift would duplicate that construction.
- The constructed field is exposed to the transformation, transition, or interpreter that consumes it.
- A separate egress route holds the constructed fact from which it projects the declared outbound contract.
- `FillRoute.receive` is registered as the framework's input constructor and `FillReplyRoute.emit` as its output serializer. The route contains no domain execution.
- Authentication extraction, status codes, headers, and protocol framing stay inside the route when they are transport facts.

## Forbidden

- a domain decision
- a successor state constructed
- an action executed
- current state or a concrete client held
- fields parsed by hand where the declared construction graph expresses the transport
- a transport wrapper passed into a domain construct
- a domain transformation; projecting already-declared facts into an outbound contract is egress, not a new domain calculation
- reply dictionaries assembled, or semantic fields selectively included or excluded
