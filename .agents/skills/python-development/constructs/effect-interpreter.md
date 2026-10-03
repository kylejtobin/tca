---
type: Reference
description: How typed actions are executed through concrete external capabilities and observed outcomes are constructed. Read when binding effects to clients, storage, subprocesses, or transports.
---

# Effect Interpreter

## Use

Use when one typed action must be executed through one concrete external capability and its observed result must become a constructed outcome.

## Required Form

```python
class ReadPositionInterpreter(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: ReadPosition
    client: PositionClient = Field(exclude=True, repr=False)

    def execute(self) -> PositionState:
        return PositionStateConstructor.validate_json(
            self.client.load(
                self.action.account.root,
                self.action.instrument.root,
            )
        )


class PersistPositionInterpreter(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: PersistPosition
    client: PositionClient = Field(exclude=True, repr=False)

    def execute(self) -> PositionRecorded:
        return PositionRecorded(
            sequence=LedgerAcknowledgement.model_validate(
                self.client.save(self.action.position.model_dump(mode="json"))
            ).sequence,
            position=self.action.position,
        )
```

- Use the imported `PositionClient` contract: `load(account, instrument)` returns `PositionState` JSON, including its documented opening-state representation with both identities; construct the `save` reply as [LedgerAcknowledgement](foreign-model.md). Couple its sequence with the submitted position in [PositionRecorded](concept-model.md), so the reply derives from the acknowledged position without staging it again. Never turn a read failure into an opening state.
- Keep `PositionStateConstructor` beside the state alias. Evaluate the read and write at the [composition-root site](composition-root.md).
- Admit the `Interpreter` edge suffix for the capability crossing, not for a new domain meaning.
- Put the action and concrete capability in declared fields.
- Perform the external call only in `execute`. One `execute` is one request and one raw reply.
- Construct `prior` from the read reply on each input: an existing fact has a source, not merely a type. Nest that read in the terminal expression; do not replace it with an unexplained value or cached current-state slot.
- Serialize the action's semantic values at the client call.
- Declare every reply the capability can send, success, refusal, and empty, as one union of foreign models. Hand the raw reply to that union's constructor; construction picks the variant. A refusal is a variant of the reply, never an exception path.
- Construct the returned concept-model or union outcome from the action and the constructed reply.
- Catch nothing. A failure the capability reports is a variant of the reply union; a failure it raises propagates.
- Propagate `CancelledError`, `KeyboardInterrupt`, and `SystemExit` to the invoking runtime.
- Leave programming defects uncaught.
- Use one interpreter type per action meaning.

## Do Not

- decide domain policy, construct a successor from prior state and a new input, or become a receive/transition loop; reconstructing an observed stored state is a read outcome, not a transition
- mutate the action or any domain value
- invent success before the external capability reports it
- catch an exception to produce an outcome, return flags, or collapse failure into absence
- call a client helper that parses, retries, counts, or raises on the reply's content; it decides what the reply meant before the model can
- count, collect, or wait for several replies in `execute`
- hide retries whose repetition semantics are not declared by the action
- retain raw replies after the outcome constructs
