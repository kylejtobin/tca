# Parse outside the crossing

- **Step kind:** a JSON parse made anywhere but an interpreter's `interpret` or the callback in `main.py`.
- **Hard type:** the payment provider's JSON reply.
- **Source:** `effect-interpreter.md`.

## Incorrect

```python
class ChargeAnswered(BaseModel):
    """The payment provider's answer to a charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    status_code: SuccessStatus
    text: ProviderBody

    @property
    def reply(self) -> ChargeReply:
        return ChargeReply.model_validate_json(self.text.root)
```

## Correct

```python
class ChargeInterpreter(BaseModel):
    """The one place a priced order is charged at the payment provider."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: Charge
    client: httpx.AsyncClient = Field(exclude=True, repr=False)

    async def interpret(self) -> ChargeAttempt:
        return ChargeAttempt(
            order=self.action.order,
            reply=ChargeReply.model_validate_json(
                (
                    await self.client.post(
                        PaymentsResource.CHARGES,
                        content=CardCharge.model_validate(self.action.order).model_dump_json(),
                    )
                ).content
            ),
        )
```
