---
name: tca-union
description: Build a union, the only legal shape for a choice among structures. MUST be invoked before modeling any set of kinds, any decision, any either/or, any status whose members carry payloads. Replaces the forbidden forms; if an if/elif chain or isinstance ladder selecting by kind, a bool decision, a raw-string kind field, an untagged union, or a label-set enum with mixed payloads is about to appear, stop and build the union instead.
---

# union

A union is a closed set of frozen-model variants over one domain axis. The axis is
named once as a `StrEnum`; each variant pins exactly one member as its typed identity,
defaulted so the kind is supplied at minting and projected into every dump.

    class PaymentMethodKind(StrEnum):
        CARD = "card"
        BANK_ACCOUNT = "bank_account"

    class Card(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[PaymentMethodKind.CARD] = PaymentMethodKind.CARD
        last_four: CardLastFour
        expiry: CardExpiry

    class BankAccount(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[PaymentMethodKind.BANK_ACCOUNT] = PaymentMethodKind.BANK_ACCOUNT
        account_number: AccountNumber
        routing_number: RoutingNumber

The kind field is identity's one structural home. It carries identity where shape
inference cannot: variants with identical payloads differ in nothing but identity, so
identity is a field or it is nowhere. Every state-transition pair is this case:

    class Engaged(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[BreakerKind.ENGAGED] = BreakerKind.ENGAGED
        at: Timestamp

    class Released(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[BreakerKind.RELEASED] = BreakerKind.RELEASED
        at: Timestamp          # identical payload; only the pin tells them apart

The pin must be `Literal`: a raw-string kind, or the axis enum unpinned
(`kind: PaymentMethodKind`), admits every member on every variant and identifies
nothing.

A decision is this construct, never a `bool`: the outcomes carry their own payloads,
and one bit fuses them and loses both.

    class Approved(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[ReviewKind.APPROVED] = ReviewKind.APPROVED
        terms: ApprovalTerms

    class Refused(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        kind: Literal[ReviewKind.REFUSED] = ReviewKind.REFUSED
        reason: RefusalReason

Behavior divides by where its meaning lives. A fact a variant implies from its own
fields is the variant's: a same-named derivation on every variant, exhaustive because
the checker requires every variant to define it. What a consumer does about a variant
is the consumer's: one exhaustive `match`, written in the consumer (the consistency model),
proven total by the checker. Never an `if`/`elif` chain or `isinstance` ladder, which
re-implement the dispatch without the exhaustiveness proof.

In the graph the union is a type like any
other: a field's declared type, the choice a derivation returns, the decision a
consumer matches on, narrowed by the checker with no machinery between. When raw data
must construct it, build its crossing form (`tca-discriminated-union`); never mint an
envelope for a choice that stays in-graph.

The probe, before rendering: construct one variant directly and read the pin back.

    card = Card(last_four=CardLastFour("4242"), expiry=CardExpiry("12/30"))
    # card.kind is PaymentMethodKind.CARD; "kind" appears in card.model_dump()

## The row

The spec row this card expands. `axis` is the `StrEnum` class, `members` its
values, `variants` the frozen_model rows, each pinning one member in its own
row's `kind`. The in-graph union renders as a type alias, never a class; the
class form is the envelope (`tca-discriminated-union`), at crossings only.

    {"construct": "union", "name": "PaymentChoice", "file": "payment.py", "axis": "PaymentMethodKind", "members": ["card", "bank_account"], "variants": ["Card", "BankAccount"]}

## Allowed patterns

- one `StrEnum` naming the union's kind axis, declared beside the variants
- two or more frozen variant models, each `frozen=True, extra="forbid"`, each pinning
  exactly one axis member: `kind: Literal[{Axis}.{MEMBER}] = {Axis}.{MEMBER}`
- the bare union in the graph: a field's declared type, a derivation's returned choice
- a same-named derivation on every variant for a fact the variant itself implies
- one exhaustive `match` over the union, in the consumer that owns the reaction
- a union of typed result variants as the shape of any decision

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
