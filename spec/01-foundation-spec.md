# Foundational Program Design Specification

A planning artifact for establishing shared understanding before implementation. This document defines the logical foundation of a system: what it does, why, what can go wrong, and what rules govern all downstream decisions. Nothing in this document addresses infrastructure, frameworks, languages, or deployment. Those are implementation concerns that derive from this foundation. They do not shape it.

## How to use this document

The spec has eight layers. Each derives from the one above. If a domain invariant doesn't trace to a condition, it shouldn't exist. If a condition doesn't have at least one invariant governing it, you have a gap. If an invariant doesn't name its carrying construct, it floats without a mechanism. Work top-down to build it. Validate bottom-up to verify it. The order is Scope → Strategy → Conditions → Construct Classification → Premises → Configuration Models → Domain Invariants → Coverage.

---

## 1\. Scope

Define the boundaries of the system. What it is. What it is not. What venue, environment, or context it operates in. What constraints that venue imposes. This section exists to prevent participants from evaluating the system against the wrong frame.

**Template:**

System: {What the system is in one sentence}

Venue/Environment: {Where it operates and what that implies}

The system IS: {Concise list of what it does}

The system IS NOT: {Concise list of what it does not do, especially things

  that could be assumed}

Venue constraints: {Non-negotiable properties of the operating environment

  that shape everything downstream}

**Example (inventory management):**

System: Automated reorder system for a single retail store

Venue/Environment: One physical location with one POS system and one supplier API

The system IS: A monitor that tracks inventory levels and triggers reorders

  when stock falls below thresholds

The system IS NOT: A demand forecasting engine, a multi-store coordinator,

  or a supplier negotiation tool

Venue constraints: The POS system reports sales with up to 15-minute delay.

  The supplier API accepts orders only during business hours.

  Delivery lead time is 24-72 hours. Returns are handled manually

  and not reflected in POS data until end of day.

---

## 2\. Strategy

How the system creates value. The general approach, not the implementation details. This should be explainable to a smart person who knows nothing about your technology stack.

**Template:**

We observe {observable phenomenon}.

We identify {specific condition within that phenomenon}.

We act by {concrete action}.

We exit/complete by {concrete completion criteria}.

Our edge is {why this works better than alternatives}.

**Example (inventory management):**

We observe real-time sales velocity from the POS system.

We identify when current stock minus projected sales over lead time

  approaches the safety stock threshold.

We act by placing a reorder with the supplier API sized to restore

  stock to the target level.

We exit/complete when the delivery is confirmed received and inventory

  is updated.

Our edge is that automated monitoring catches reorder points faster

  than manual weekly checks, reducing both stockouts and overstock.

---

## 3\. Conditions

Everything that can go wrong, needs to be managed, or represents a scenario the system must handle. These are the realities of operating in your specific venue/environment. Each condition is a statement of fact about something that WILL happen, not something that might happen hypothetically.

**Template:**

1\. {Condition name}: {One sentence describing the scenario}

2\. {Condition name}: {One sentence describing the scenario}

...

**Example (inventory management):**

1\. POS delay: Sales data arrives up to 15 minutes late,

   meaning stock levels may be overstated.

2\. Supplier unavailability: The supplier API is offline outside

   business hours and orders cannot be placed.

3\. Demand spikes: Unexpected high-volume sales can deplete stock

   faster than the reorder point calculation predicts.

4\. Delivery failure: An order may be confirmed by the supplier

   but not actually delivered.

5\. Data mismatch: POS-reported inventory may drift from actual

   shelf inventory due to theft, breakage, or return timing.

6\. Duplicate orders: A reorder could trigger twice if the first

   order confirmation is delayed.

7\. Stale thresholds: Safety stock levels set for normal demand

   may be wrong during seasonal peaks or promotions.

---

## 4\. Construct Classification

There is one proof, and it is construction. A value's existence as a well-typed frozen object is the evidence its constraints held, so an illegal value cannot be built. There is no separate validation step, no strength ladder, no mechanism that admits an illegal value and then rejects it. Every invariant in section 7 names **which construct from the closed set carries it** — and the question is shape-fit, "which construct *is* this invariant?", under one discipline: push the meaning to the most structural construct available, so the illegal state is *unconstructable* rather than caught after the fact.

The closed construct set is the authority's. The constructs that carry domain invariants are these:

**Semantic scalar.** A bound on one open value — a frozen `RootModel[P]` over a single primitive carrying a `Field(...)` constraint or a domain-meaningful name. It names a bounded region of an open value space (a non-empty SKU, a non-negative quantity), and its existence is the proof of that bound. Use when the invariant is a static bound on one value.

**Frozen-model field.** That scalar — or another frozen model — composed as a field of a larger frozen model. Construction of the parent triggers construction of the field, which carries the scalar's proof one level deeper. The parent's existence is the proof that every field's constraint held together. Use when the invariant is carried into a larger structure by the field type alone, and when `extra="forbid"` closing the structure is itself part of the proof.

**Union (structural).** A closed set of two or more disjoint frozen-model variants, told apart by their structure and nothing else. The union **absorbs every state machine and every "impossible composition."** The legal states are the variants; an impossible composition is unconstructable because no variant has its shape. A delivered order receiving an acknowledgment is not a cell a validator rejects — it is a (state, event) combination that no variant of the order-transition union admits, so it cannot be built. **There is no cross-field after-validator** carrying this: a forbidden composition of individually-legal values is a *missing variant*, not a rule run over a constructed value. **There is no stored discriminator and no `kind` tag**: the variants' disjoint structure is the selection, and a tag would only copy what the fields already prove. The test is the authority's — delete every field that names the kind; if construction still lands exactly one variant, the structure already holds the union.

**Derivation.** A fact a frozen model implies from its own already-proven fields — `@cached_property`, `@computed_field` over it when the fact must cross the wire, or a bare `@property` for a trivial read. It composes proven inputs and returns a declared type or a closed set of typed result variants, never a bare `bool`/`str`/`int`. Two cases carry invariants: a **computed value** (a derived quantity — a buffered stock level, a depletion rate — proven by the construction of the declared type it returns), and a **decision** — "should the system act on this?" — which returns a result union (`ReorderTriggered(intent) | ReorderSuppressed(reason)`) where **both outcomes construct**; construction failure is reserved for malformed input, never for a well-formed value the system decided against. Either way the consumer reads the result off the model — there is no `match`, no dispatch, no boolean — and the model that carries the derivation is just a frozen model holding it, not a construct of its own. A spec line that reads "is this value well-formed?" is a scalar, a field, or a union; a spec line that reads "should the system act?" is a derivation returning a union.

**Active-model world-edge guard.** Genuinely external prerequisites that no field on any frozen model represents — connection liveness, scheduled cadence, the live readiness of the world. The single active model of a context constructs the domain fact only when the live world is ready, and emits effects only after proof. The fact's absence is the proof: when the world is not ready, nothing is constructed. This is for *world-state* prerequisites only. An **event-type** prerequisite — "this outcome holds only for this kind of incoming event" — is not a guard but a **union of event variants** lifted at the boundary; the variant the world delivered is the prerequisite, carried structurally.

Prefer the most structural construct that will carry the invariant: a bound on one value is a scalar before it is anything else; a forbidden composition is a union before it is ever a validator; a decision is a derivation before it is ever a branch. Reaching for a looser construct when a tighter one would make the illegal state unconstructable is the deepest specification defect this section prevents.

**Example (inventory management):**

Constructs this system uses:

Semantic scalars — `Sku`, `StockLevel`, `Quantity`, `Duration`, `SupplierId` as narrowed `RootModel` scalars with declarative constraints (non-negativity, format, range bounds). The bound on each open value is proven by the scalar's existence.

Frozen-model fields — `ReorderIntent`, `PhysicalCount`, `SalesEvent` as frozen models composing those scalars as fields. The model's existence proves the field-level constraints hold together, with `extra="forbid"` closing each to foreign noise.

Unions — `OrderTransition` as a structural union over the legal (state, event) shapes. A delivered order receiving an acknowledgment is a meaningless composition: no variant has that shape, so it is unconstructable. There is no validator rejecting it and no `kind` field selecting the variant — the disjoint structure of the variants is the selection. Distinct *event* kinds (a supplier acknowledgment versus a physical receipt) are likewise variants of an event union, not a tagged record.

Derivations returning unions — every decision. `ReorderEvaluation` composes proven inputs and its `@cached_property` returns `ReorderResult = ReorderTriggered(intent) | ReorderSuppressed(reason)`. Both outcomes construct; the consumer reads the selected variant's own derivation. Construction of `ReorderEvaluation` always succeeds for well-formed inputs.

Active-model world-edge guards — supplier business hours, the scheduled threshold-review cadence, the liveness of the supplier connection. The active model constructs an order-placement fact only when the supplier window is open and the connection is live; outside the window it constructs nothing. The scheduled threshold review fires only on its cadence; between fires there is no construction to make.

---

## 5\. Premises

The foundational assumptions about how the system is structured that determine how invariants are expressed and enforced. Premises are not domain rules. They are axioms about the system's architecture that shape where domain rules live and how they work. They sit between the conditions (what can go wrong) and the invariants (what must be true) because invariants cannot be properly grounded without knowing these structural commitments.

If conditions are the terrain and invariants are the rules of engagement, premises are the physics of the world the rules operate in.

**Template:**

PRE-{N}: {Foundational structural assumption}

  Implies: {What this means for how invariants are expressed}

**Example (inventory management):**

PRE-1: The inventory ledger is the single source of truth for

  stock levels. All decisions derive from it. If a transaction

  is not in the ledger, it did not happen.

  Implies: Every invariant about stock levels is enforced at the

  point of ledger write or read, not in application logic

  that bypasses the ledger.

PRE-2: State is a projection of ledger entries. Current stock

  is not stored as a separate number. It is a derivation off

  the ledger: receipts in, sales out, adjustments applied.

  Implies: Invariants about "current stock" are really invariants

  about the derivation, not about a cached value.

PRE-3: Each domain rule lives in a named construct — the active

  model, or a derivation on a frozen model — never floating as a

  system-wide decree.

  Implies: Every invariant must name the construct that carries it:

  which construct, on what proven input, refuses to construct or

  emit what fact.

PRE-4: Construction is the proof. A constructed value is proven,

  not validated; if a value can be constructed, its constraints

  held. The type is the contract between components.

  Implies: Invariants about data quality are carried by the type,

  not by runtime checks in consuming constructs. A value that

  could not be proven was never constructed and never moves forward.

---

## 6\. Configuration Models

Every system has parameters that are not constants and not domain truths — they sit between. Configuration is typed and proven at construction; this section names what is parameterized, who owns each parameter, and how often it changes. A parameter discovered during invariant writing belongs here, not in the invariant's body.

Decomposition by owner and change cadence prevents two failure modes: parameters scattered across the codebase with no canonical home, and configuration treated as a uniform bag when it actually contains distinct lifecycles.

**Template:**

CFG-{N}: {ConfigModelName}

  Owner: {who changes this}

  Cadence: {how often it changes}

  Parameters: {field name with type and constraint, one per line}

  Consumed by: {the construct that holds it — the active model, a route,

    or a derivation on a frozen model}

**Example (inventory management):**

CFG-1: SkuPolicy

  Owner: Operations team

  Cadence: Daily to weekly per SKU; lifecycle changes when SKUs
    are introduced or retired

  Parameters:

    sku: Sku

    safety_stock: StockLevel (ge=0)

    target_reorder_level: StockLevel (ge=safety_stock)

    preferred_supplier: SupplierId

  Consumed by: ReorderEvaluation (the derivation that decides reorders)

CFG-2: VenueProfile

  Owner: System operator

  Cadence: Set at deployment; changes when the venue itself changes
    (new POS, new supplier integration)

  Parameters:

    max_pos_reporting_delay: Duration (gt=0)

    supplier_business_hours: TimeWindow

    delivery_lead_time_bounds: DurationRange (lower ge=0, upper ge=lower)

  Consumed by: the active model (order placement at the supplier edge)
    and BufferedStockProjection (the stock derivation)

CFG-3: ReviewCadence

  Owner: Operations team

  Cadence: Adjusted when demand patterns shift seasonally

  Parameters:

    threshold_review_interval: Duration (gt=0)

    velocity_window_short: Duration (gt=0)

    velocity_window_long: Duration (gt=velocity_window_short)

  Consumed by: the active model (the scheduled review cadence) and
    DepletionProjection (the depletion derivation)

Configuration models are frozen models whose fields are semantic scalars or value objects from section 4. They enter the construction graph at startup; the act of constructing them is the proof. A construct receives configuration as a proven model, never as a dict.

---

## 7\. Domain Invariants

The rules that govern the system's behavior. Each invariant is a proposition that must always be true. Each one must trace to at least one condition it governs. If an invariant doesn't connect to a condition, it's either protecting against something that can't happen in your venue (dead weight) or you're missing a condition (gap in your analysis).

Invariants are not implementation instructions. They don't say HOW to enforce the rule. They state WHAT must be true. But each invariant must be grounded in the premises. It must have a home: a named construct, a specific proven input, and the fact it constructs or refuses to construct. If an invariant can't name the construct that carries it, it's a wish, not a rule.

**Template:**

{InvariantName}: {Statement of what must always be true}

  Governs: {Condition number(s)}

  Construct: {which construct carries it — semantic scalar / frozen-model
    field / union (structural) / derivation returning a union /
    active-model world-edge guard}

  Home: {The named construct — active model, route, boundary model, or a
    derivation on a frozen model — on what proven input, by what fact it
    constructs or refuses to construct}

  Rationale: {Why this rule exists, what goes wrong if violated}

**Example (inventory management):**

PosStockBuffered: Never use POS-reported stock as ground truth without

  applying the maximum reporting delay as a buffer.

  Governs: Condition 1 (POS delay)

  Construct: derivation returning a value — `BufferedStockProjection`
    composes proven `PosStockReading` and `Duration` (max reporting
    delay) and yields a buffered stock value via `@cached_property`.
    Construction always succeeds for well-formed inputs.

  Home: `BufferedStockProjection`, a derivation on a frozen model.

    Given proven ledger entries and the max-reporting-delay `Duration`,

    its `@cached_property` subtracts a buffer (delay times recent

    velocity) and yields the buffered stock value the rest of the

    graph reads. The active model emits the projected-stock fact only

    after this derivation has been read.

  Rationale: Acting on overstated stock leads to missed reorders

  and stockouts.

NoDuplicateReorder: Never place a reorder for a SKU while a confirmed but

  undelivered order for that SKU exists.

  Governs: Condition 6 (Duplicate orders)

  Construct: derivation returning a union — `ReorderEvaluation` returns
    `ReorderResult = ReorderTriggered(intent) | ReorderSuppressed(reason)`.
    When a pending order exists for the SKU, the result is the
    `ReorderSuppressed(reason=PendingOrderExists)` variant.

  Home: `ReorderEvaluation`, a derivation on a frozen model that

    composes the proven pending-order projection with the SKU's

    policy. When a pending order exists for the SKU, its derivation

    constructs the `ReorderSuppressed` variant. The active model

    reads the selected variant and emits a reorder fact only for

    `ReorderTriggered`; for `ReorderSuppressed` it emits nothing.

  Rationale: Duplicate orders create overstock and wasted capital.

SupplierUnavailableQueues: A reorder that cannot be placed due to supplier

  unavailability must be queued, not dropped.

  Governs: Condition 2 (Supplier unavailability)

  Construct: active-model world-edge guard plus a union — supplier

    availability is live world state, not a field. The active model

    constructs an order-placement fact only when the supplier window

    is open; otherwise it constructs `OrderQueued(intent)`, holding

    the proven intent until the next admissible window.

  Home: The active model, at the supplier edge. On a `ReorderTriggered`

    intent, when the supplier window is closed or the connection is

    not live, it does not construct an order-placed fact; it constructs

    and holds an `OrderQueued(intent)` fact instead, releasing it when

    the window reopens.

  Rationale: Dropping a valid reorder because the API is down

  means the stockout the system detected goes unaddressed.

DepletionUsesFasterVelocity: Projected depletion rate must use the faster of

  the trailing 24-hour velocity and the trailing 7-day velocity.

  Governs: Condition 3 (Demand spikes)

  Construct: derivation returning a value — `DepletionProjection`
    composes the two proven velocity windows and yields the projected
    depletion rate via `@cached_property`, taking the maximum.

  Home: `DepletionProjection`, a derivation on a frozen model. Given

    the two proven velocity-window values, its `@cached_property`

    yields the higher rate as the projected depletion. The active

    model reads it before emitting the depletion-projection fact.

  Rationale: Using only 7-day average masks sudden acceleration

  in sales, leading to stockouts during spikes.

DeliveryRequiresPhysicalReceipt: A delivery is not confirmed until physical receipt is

  recorded, not when the supplier API acknowledges the order.

  Governs: Condition 4 (Delivery failure)

  Construct: union (structural) — incoming events are a union whose

    variants are `SupplierAcknowledged` and `PhysicalReceipt`, disjoint

    by structure. A delivery-confirmed fact has the `PhysicalReceipt`

    variant as the only shape from which it can be constructed; the

    `SupplierAcknowledged` variant cannot produce one.

  Home: The boundary model lifts each incoming event into its variant,

    and the active model constructs a delivery-confirmed fact only from

    the `PhysicalReceipt` variant. A `SupplierAcknowledged` event has

    no shape from which the delivery-confirmed fact can be built, so

    none is constructed.

  Rationale: Treating supplier acknowledgment as delivery

  confirmation overstates incoming stock and suppresses

  necessary reorders.

PhysicalCountOverridesCalculated: Actual shelf count, when available, overrides

  POS-calculated inventory.

  Governs: Condition 5 (Data mismatch)

  Construct: derivation returning a value — the stock projection

    composes the most recent `PhysicalCount` (when present) with

    subsequent ledger entries; its `@cached_property` for current

    stock uses the physical count as the baseline.

  Home: The stock-projection derivation on a frozen model. When a

    `PhysicalCount` is present, its `@cached_property` takes the

    counted value as the baseline and applies subsequent ledger

    entries to it. The active model emits the resulting adjustment

    fact.

  Rationale: The physical world is the source of truth.

  Calculated inventory drifts from reality over time.

ThresholdsReviewedOnCadence: Safety stock thresholds must be reviewed against actual

  demand data on a defined cadence, not set once and assumed valid.

  Governs: Condition 7 (Stale thresholds)

  Construct: active-model world-edge guard plus a derivation returning

    a union — the scheduled cadence is live world state: the active

    model constructs a review only when the cadence fires. When it

    fires, `ThresholdReview` composes proven demand projections and

    returns `ReviewResult = ThresholdHeld | ThresholdAdjusted(new_value)`.

  Home: The active model, gated by the scheduled cadence — between

    fires there is no review to construct. On a fire, it constructs

    `ThresholdReview` over the proven demand projection; the review's

    derivation yields `ThresholdHeld` or `ThresholdAdjusted(new_value)`,

    and the active model emits a threshold-adjustment fact only for

    the `ThresholdAdjusted` variant.

  Rationale: Static thresholds become wrong as demand patterns

  change, leading to either stockouts or waste.

---

## 8\. Coverage

The verification step that closes the loop. Every condition must have at least one invariant. Every invariant must trace to at least one condition. Every invariant must name the construct that carries it from section 4. Every configuration parameter from section 6 must be consumed somewhere. Coverage is the artifact that makes the trace explicit — without it, gaps and orphans hide.

**Coverage matrix — conditions to invariants:**

| Condition | Governing Invariants |
|---|---|
| {N} {name} | {invariant names that govern this condition} |

A row with no invariants is a gap. Either the condition does not actually happen in the venue (delete it from section 3) or an invariant is missing.

**Coverage matrix — invariants to conditions and carrying construct:**

| Invariant | Condition(s) | Carrying Construct |
|---|---|---|
| {InvariantName} | {N} | {semantic scalar / frozen-model field / union / derivation / active-model guard} |

An invariant row not traceable to any condition is dead weight — either the condition is missing or the invariant exists for a reason outside the venue.

**Validation checklist:**

- [ ] Every condition has at least one invariant governing it
- [ ] Every invariant traces to at least one condition
- [ ] Every invariant names its carrying construct from section 4
- [ ] Every impossible-composition invariant is a structural union (no field rejected after construction, no discriminator selecting the variant), not a cross-field check in disguise
- [ ] Every decision is a derivation returning a union of typed result variants — both outcomes construct, and the consumer reads the selected variant, never a branch
- [ ] Every active-model world-edge guard is genuinely external world state (liveness, cadence), not a field that was never forged; every event-type prerequisite is a union of event variants, not a guard
- [ ] Every invariant names its home: which named construct, on what proven input, constructing or refusing to construct what fact
- [ ] No invariant names a generic "handler" or a "validator"; the live edge is the active model
- [ ] Every invariant is grounded in the premises
- [ ] Every configuration parameter from section 6 is consumed by at least one named construct (the active model, a route, or a derivation)
- [ ] No invariant references a constraint that doesn't exist in your venue
- [ ] No invariant prescribes implementation (HOW) rather than stating a rule (WHAT)
- [ ] Premises are structural axioms, not domain rules disguised as premises
- [ ] The scope explicitly excludes things that participants might assume
- [ ] The strategy is explainable without referencing technology
- [ ] The conditions list includes things that WILL happen, not hypotheticals

**Example (inventory management):**

Conditions → Invariants:

| Condition | Governing Invariants |
|---|---|
| 1 POS delay | PosStockBuffered |
| 2 Supplier unavailability | SupplierUnavailableQueues |
| 3 Demand spikes | DepletionUsesFasterVelocity |
| 4 Delivery failure | DeliveryRequiresPhysicalReceipt |
| 5 Data mismatch | PhysicalCountOverridesCalculated |
| 6 Duplicate orders | NoDuplicateReorder |
| 7 Stale thresholds | ThresholdsReviewedOnCadence |

Invariants → Conditions and Carrying Construct:

| Invariant | Condition | Carrying Construct |
|---|---|---|
| PosStockBuffered | 1 | derivation (BufferedStockProjection) |
| SupplierUnavailableQueues | 2 | active-model guard + union (OrderQueued) |
| DepletionUsesFasterVelocity | 3 | derivation (DepletionProjection) |
| DeliveryRequiresPhysicalReceipt | 4 | union (event variants; PhysicalReceipt only) |
| PhysicalCountOverridesCalculated | 5 | derivation (projection baseline) |
| NoDuplicateReorder | 6 | derivation returning a union (ReorderResult) |
| ThresholdsReviewedOnCadence | 7 | active-model guard + derivation returning a union |

Every condition is covered. Every invariant traces to its condition. Every invariant names the construct that carries it. The foundation is closed.

If every row of every matrix has a value and every checkbox is green, downstream work has a stable foundation to build on: the type catalog of constructs, and the `tca-architect` construction-graph plan the forge agents render from it. If any cell is empty or any box fails, the foundation has a crack that will propagate into every construct built on top of it.
