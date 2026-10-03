---
type: Construct
description: Execution of one typed action through one imported capability, constructing the observed outcome.
---

# Effect Interpreter

## Definition

One typed action is executed through one concrete external capability, and its observed result becomes a constructed outcome. The intent to have an effect and the fact that it occurred are two propositions with two proofs: the [action](./action.md) proves the first, the interpreter's outcome proves the second. `Interpreter` is an admitted edge suffix for the capability crossing, not for a new domain meaning.

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

`PositionClient` is the imported capability: `load(account, instrument)` returns `PositionState` JSON, including its documented opening-state representation with both identities; `save` returns the ledger's acknowledgement, constructed as [LedgerAcknowledgement](./foreign-model.md) and coupled with the submitted position in [PositionRecorded](./concept-model.md). A read failure never becomes an opening state.

- The action and the concrete capability are declared fields; the capability is neither semantic proof nor serializable state, so it is excluded from dump and repr.
- The external call happens only in `execute`, evaluated at the [composition-root site](./composition-root.md).
- `prior` constructs from the read reply on each input: an existing fact has a source, not merely a type. That read nests in the terminal expression, never a cached current-state slot.
- The action's semantic values serialize at the client call.
- Every reply the capability can send, success, refusal, and empty, is one union of foreign models. The raw reply goes to that union's constructor and construction picks the variant; a refusal is a variant of the reply, never an exception path. The returned concept-model or union outcome constructs from the action and the constructed reply.
- Nothing is caught. A failure the capability reports is a variant of the reply union; a failure it raises propagates. One `execute` is one request and one raw reply. `CancelledError`, `KeyboardInterrupt`, and `SystemExit` propagate to the invoking runtime. Programming defects stay uncaught.
- One interpreter type per action meaning.

## Forbidden

- a domain decision, a successor constructed from prior state and new input, or a receive loop; reconstructing an observed stored state is a read outcome, not a transition
- mutation of the action or any domain value
- success invented before the capability reports it
- an exception caught to produce an outcome, flags returned, or failure collapsed into absence
- a client helper that parses, retries, counts, or raises on the reply's content; it decides what the reply meant before the model can
- several replies counted, collected, or waited for in `execute`
- retries whose repetition semantics the action does not declare
- raw replies retained after the outcome constructs
