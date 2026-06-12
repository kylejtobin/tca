---
name: tca-discriminated-union
description: Build a discriminated union envelope, the only legal crossing for identity-carrying raw data into a choice. MUST be invoked before any transport payload, stored fact, or re-entering published fact constructs a union, and before writing any RootModel[A | B]. Replaces the forbidden forms; if shape inference at a crossing, a routing validator selecting a variant, json.loads-then-dispatch, or an envelope around an in-graph-only choice is about to appear, stop and build the envelope instead.
---

# discriminated union

The discriminated union is the union's constructing form; the axis and variants are
built first (`tca-union`). It is a frozen `RootModel[A | B | C]` discriminating on the
kind field, so construction proves identity and selects the variant in one O(1) step
with exact per-variant errors.

    class PaymentMethod(RootModel[Card | BankAccount], frozen=True):
        root: Card | BankAccount = Field(discriminator="kind")

It stands wherever identity-carrying data enters: a transport payload, a stored fact
read back, a published fact re-entering through the consuming context's boundary. The
defaulted kind pins (`tca-union`) project into every dump, so identity travels with the
fact and re-proof by discriminated construction is always possible on the far side. A
choice that never meets raw data needs no envelope: the checker already selects
in-graph, and an envelope minted there is structure without meaning.

A fact every variant implies under the same name is forwarded by the envelope in one
expression, so it reads the same off the envelope as off the variant:

    class PaymentMethod(RootModel[Card | BankAccount], frozen=True):
        root: Card | BankAccount = Field(discriminator="kind")

        @cached_property
        def settlement_days(self) -> SettlementDays:
            return self.root.settlement_days

Foreign data that carries no identity cannot be discriminated; its crossing is the
ordered union (`tca-boundary`), which mints the identity the wire lacked.

The probe, before rendering: validate one wire payload per kind through the envelope
and read the variant type back.

    method = PaymentMethod.model_validate({"kind": "card", "last_four": "4242", "expiry": "12/30"})
    # type(method.root) is Card; method.root.kind is PaymentMethodKind.CARD

    wire = method.model_dump_json()                  # the defaulted pin travels in the data
    again = PaymentMethod.model_validate_json(wire)  # re-proof on the far side, same fact
    # type(again.root) is Card; this round trip is the construct's entire purpose

    # discrimination buys exact per-variant errors: a payload claiming "card" fails on
    # Card's own fields, never on a smear across all variants
    # PaymentMethod.model_validate({"kind": "card"}) -> errors name card.last_four, card.expiry

## The row

The spec row this card expands. `over` names the union row; the envelope class
takes this row's `name`, and the gate requires its root to be exactly the
union's variants with `Field(discriminator="kind")`.

    {"construct": "discriminated_union", "name": "PaymentMethod", "file": "payment.py", "over": "PaymentChoice"}

## Allowed patterns

- `class X(RootModel[A | B | C], frozen=True)` with
  `root: A | B | C = Field(discriminator="kind")`, only where raw data crosses
- a forwarding derivation: one expression, `return self.root.<name>`
- re-entry of a projected fact by discriminated construction at the consuming boundary

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
