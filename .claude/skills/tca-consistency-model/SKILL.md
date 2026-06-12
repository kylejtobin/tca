---
name: tca-consistency-model
description: Build the consistency model, the single legal home for live clients and mutable state. MUST be invoked before holding any socket, database, bus, or client, and before writing any state-evolving method or verb body. Replaces the forbidden forms; if a manager, engine, second unfrozen model, module-level client, an if/elif ladder choosing an effect, a try/except in a verb body, or a match whose arms differ only in which client they call is about to appear, stop and build the consistency model instead.
---

# consistency model

The consistency model is the single unfrozen model of a context, and its obligation is its name: every state it holds is a proven fact. It holds the transport
clients, constructs frozen facts from live input, and emits effects only after proof. It
is the context's present: state evolution is reassigning which proven fact a field
points to, and even here no unproven value is ever held. A construction refusal is never
caught into a value; an expected-failure crossing is the boundary's ordered union
(`tca-boundary`). A second unfrozen model means the context is two contexts: stop and
report it.

    class AnalysisConsistencyModel(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        bus: EventBusClient

        def analyze(self, tool_input: HookToolInputBoundary) -> None:
            file_context = FileContext(
                file_path=tool_input.file_path,
                file_source_text=tool_input.source_text,
            )
            self.bus.publish(file_context.analysis.model_dump_json())

Every statement in a mutation method is one of these six forms:

1. construct a frozen fact: `file_context = FileContext(...)`
2. assign a constructed value to a field: `self.latest = file_context`
3. read a derivation: `analysis = file_context.analysis`
4. emit: one call on one client field, its argument a constructed value or its
   projection: `self.bus.publish(analysis.model_dump_json())`
5. capture a foreign reply: the licensed three lines, one call assigned, each
   declared signal reassigned as the arrived value, feeding a crossing's
   construction (`tca-failure`)
6. one exhaustive `match` over a union's narrowed root, each arm a sequence of
   forms 1-4

Sort what varies before reaching for `match`. When only the *destination* varies, the
authority rules with no exemption: "an effect whose channel varies crosses as a
projected fact and is re-selected by discriminated construction at the consuming
boundary." A static variant-to-channel mapping is the variant's own fact: each variant
derives its subject (`tca-union`), the envelope forwards it, and the consumer holds one
client and emits once. No dispatch exists to write. A `match` whose arms differ only in
which client they call is the unfactored form and is never built:

    def settle(self, outcome: OrderOutcome) -> None:
        self.bus.publish(outcome.subject.root, outcome.notification.model_dump_json())

The `match` is the consumer's form when *reactions* genuinely diverge in behavior:
different constructions, different state evolution per variant. The type checker proves
it total, so a new variant fails the build until every consumer handles it. A variant's
own facts stay on the variant as derivations and are read off the arm. No `if`/`elif`
chains and no `isinstance` ladders: the same dispatch without the exhaustiveness proof.

    def reconcile(self, outcome: OrderOutcome) -> None:
        match outcome.root:
            case Filled() as filled:
                position = Position(account_id=filled.account_id, price=filled.fill_price)
                self.latest = position                  # the present re-points on a fill
                self.bus.publish(outcome.subject.root, position.model_dump_json())
            case Rejected():
                self.bus.publish(outcome.subject.root, outcome.notification.model_dump_json())

State evolution is the construct's defining act and is always this shape: construct the
newer proven fact, reassign the field to it. Reassignment of proofs, never mutation of
their contents, and never an unproven value held even for one statement. When the
reacting context is another process, the projected fact crossed already; the consuming
context re-selects the variant by discriminated construction at its own boundary.

## Verb-body template

A verb expands from its row's declared chain. Statement order is the dependency order of
the constructions, never authored. A stub body (`raise NotImplementedError`, bare `...`,
`pass`) is a mismatch between file and row, denied at the write, never a placeholder. The chain is never empty; an empty chain is refused as a row, not expanded as a body.

`try`/`except` in a verb body is legal in exactly one shape, the capture: one
call assigned, each declared signal reassigned as the arrived value, and the
crossing constructed from whatever arrived (`tca-failure`). Anything past that
shape, a broad except, a second statement in an arm, a substituted default, a
caught `ValidationError`, is denied at the write: the conversion is the
railroad's, and the refusal propagates.

    async def get(self, name: ObjectName) -> GetReply:
        try:
            raw: object = await self.store.get(name.root)
        except ObjectNotFoundError as signal:
            raw = signal
        return GetReplyCrossing.model_validate(raw).root

The corpus pulls hardest inside a verb body, and each pull has one answer. A
hand-assembled dict where a constructed type belongs: construct with keywords, the
constructor proves the constituents. A coalesce or inline default: it forges an
unproven value, and absence is declared in the model, never defaulted in a body. A
check after a construction: it un-proves the value it guards. A step, a helper, a
conversion that fits no form: the model is not finished, and the answer is a halt and
a report, never an improvisation.

Returning form: the method takes the row's `accepts` type, constructs each row in
`constructs` in dependency order, reassigns `self.<field>` where the chain evolves state,
emits each row in `emits` only after the fact it projects is constructed, and returns the
row's `returns` type.

    def <name>(self, arg: <accepts>) -> <returns>:
        <fact_a> = <RowA>(...)          # construct in dependency order
        <fact_b> = <RowB>(<fact_a>)     # each construction before its dependents
        self.<field> = <fact_b>         # reassign present where chain evolves state
        self.<client>.publish(          # emit only after the projected fact is constructed
            <fact_b>.<projection>()
        )
        return <fact_b>.<returns_field>

Yielding form: the method yields the row named in `yields` as constructed proven
facts, one per fact, each constructed before it is emitted. It yields the fact itself,
never its projection: projection is the exit relation at a transport, and a stream's
consumer receives proven facts.

    async def <name>(self, arg: <accepts>) -> AsyncIterator[<yields>]:
        <fact_a> = <RowA>(...)
        yield <fact_a>

## The row

The spec row this card expands. One per context. `clients` name foreign classes
and are legal only on this row; `fields` are declared rows and are the context's
state. A row with no fields declares `stateless` with the reason; one of the two
holds, never both, never neither. Every client held must be reached by some
verb's body. `arbitrary_types_allowed` passes the gate only on the class this
row names.

    {"construct": "consistency_model", "name": "AnalysisConsistencyModel", "file": "analysis.py", "clients": {"bus": "EventBusClient"}, "fields": {"latest": "FileContext"}}

## Allowed patterns

- one unfrozen `BaseModel` per context, `arbitrary_types_allowed=True` here and nowhere
  else, clients as fields
- `-> None` mutation methods whose every statement is one of the six forms
- non-client fields as declared types
- the fact constructed before its effect is emitted
- one exhaustive `match` over the narrowed root, arms holding only forms 1-4
- every client reached by at least one verb body; a body touching only the rows
  its declared chain names

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
