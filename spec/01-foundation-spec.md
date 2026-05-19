# Foundational Program Design Specification

A planning artifact for establishing shared understanding before implementation. This document defines the logical foundation of a system: what it does, why, what can go wrong, and what rules govern all downstream decisions. Nothing in this document addresses infrastructure, frameworks, languages, or deployment. Those are implementation concerns that derive from this foundation. They do not shape it.

## How to use this document

The spec has eight layers. Each derives from the one above. If a domain invariant doesn't trace to a condition, it shouldn't exist. If a condition doesn't have at least one invariant governing it, you have a gap. If an invariant doesn't name its proof level, it floats without a mechanism. Work top-down to build it. Validate bottom-up to verify it. The order is Scope → Strategy → Conditions → Proof Hierarchy Classification → Premises → Configuration Models → Domain Invariants → Coverage.

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

## 4\. Proof Hierarchy Classification

The mechanisms by which invariants are proven, ordered from strongest to weakest. Every invariant in section 7 names the level it sits at. A weaker mechanism is admissible only when every stronger mechanism is demonstrably insufficient for that invariant. This section is a fixed taxonomy, not a free design space — the classification names which slot each invariant occupies.

**Level 1 — Field constraint on a narrowed scalar.** The strongest. A constraint expressed declaratively on a single-value root model. The type's existence IS the proof: if the instance exists, the bound holds. Use when the invariant is a static bound on one value against a constant.

**Level 2 — Narrowed type as a field on a composed model.** The composed model declares a Level-1 type as a field. Construction of the parent triggers construction of the field, which triggers the Level-1 proof. Use when the invariant is carried into a larger model by the field type alone.

**Level 3 — Cross-field validator over composed fields.** A validator that rejects a state composed of individually-valid values whose composition is structurally impossible. Reserved for invariants that cannot be carried by any Level-1 or Level-2 shape. A validator referencing one field against a constant is a Level-1 unforged. A validator comparing fields against a configured threshold is a decision, not an integrity check — its home is a derivation returning a typed result variant, not a Level-3 validator.

**Level 4 — Handler-gated absence.** External state that no field on any model represents. The handler refuses to attempt construction when the prerequisite is missing. The composed model's absence is the proof. Use for connection liveness, scheduled cadence, prerequisite events, halt conditions.

**Decisions are not validators.** When a rule answers "should the system act on this?" rather than "is this value well-formed?", the answer is not a validator at any level. Its home is a derivation on a composed evaluation model that returns a typed result variant. Construction always succeeds; the consumer dispatches on the variant. A spec line that reads like a decision must say so — it carries Level-2 inputs into a derivation, not a validator.

**Strongest available wins.** Each invariant is tested at Level 1 first, then 2, then 3, then 4. The first level that holds is the home. Reaching for a weaker level when a stronger one would carry the proof is the deepest specification defect this section prevents.

**Example (inventory management):**

Mechanisms this system uses:

Level 1 — `Sku`, `StockLevel`, `Quantity`, `Duration`, `SupplierId` as narrowed scalars with declarative constraints (non-negativity, format, range bounds).

Level 2 — `ReorderIntent`, `PhysicalCount`, `SalesEvent` as composed models carrying Level-1 types as fields. The composed model's existence proves the field-level constraints hold.

Level 3 — `OrderTransition` rejecting impossible (state, event) cells. A delivered order receiving an acknowledgment is a meaningless composition; the validator refuses it. Not used for thresholds.

Level 4 — Supplier business hours, scheduled threshold review cadence, pending-order absence. The order placement handler does not exist as a construction site outside business hours. The threshold review handler does not exist outside its scheduled cadence.

Decisions appear as derivations, not levels. `ReorderEvaluation` composes proven inputs and returns `ReorderResult = ReorderTriggered(intent) | ReorderSuppressed(reason)`. The reorder handler dispatches on the variant; construction of `ReorderEvaluation` always succeeds for well-formed inputs.

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

  is not stored as a separate number. It is computed by replaying

  the ledger: receipts in, sales out, adjustments applied.

  Implies: Invariants about "current stock" are really invariants

  about the projection function, not about a cached value.

PRE-3: Each business rule lives in a specific handler that

  processes a specific event type. Rules do not float as

  system-wide decrees.

  Implies: Every invariant must name where it is enforced:

  which handler, on what input, refuses to produce what output.

PRE-4: Validation happens at construction. If a data object

  can be constructed, it is valid. The schema is the contract

  between components.

  Implies: Invariants about data quality are enforced by the

  schema, not by runtime checks in consuming handlers.

---

## 6\. Configuration Models

Every system has parameters that are not constants and not domain truths — they sit between. Configuration is typed and validated at construction; this section names what is parameterized, who owns each parameter, and how often it changes. A parameter discovered during invariant writing belongs here, not in the invariant's body.

Decomposition by owner and change cadence prevents two failure modes: parameters scattered across the codebase with no canonical home, and configuration treated as a uniform bag when it actually contains distinct lifecycles.

**Template:**

CFG-{N}: {ConfigModelName}

  Owner: {who changes this}

  Cadence: {how often it changes}

  Parameters: {field name with type and constraint, one per line}

  Consumed by: {which handler or evaluation model takes this as input}

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

  Consumed by: ReorderEvaluation

CFG-2: VenueProfile

  Owner: System operator

  Cadence: Set at deployment; changes when the venue itself changes
    (new POS, new supplier integration)

  Parameters:

    max_pos_reporting_delay: Duration (gt=0)

    supplier_business_hours: TimeWindow

    delivery_lead_time_bounds: DurationRange (lower ge=0, upper ge=lower)

  Consumed by: Stock projection handler, order placement handler

CFG-3: ReviewCadence

  Owner: Operations team

  Cadence: Adjusted when demand patterns shift seasonally

  Parameters:

    threshold_review_interval: Duration (gt=0)

    velocity_window_short: Duration (gt=0)

    velocity_window_long: Duration (gt=velocity_window_short)

  Consumed by: Threshold review handler, depletion projection handler

Configuration models are frozen composed models whose fields are Level-1 narrowed scalars or Level-2 value objects from section 4. They enter the construction graph at startup; the act of constructing them is the validation. A handler receives configuration as a proven model, never as a dict.

---

## 7\. Domain Invariants

The rules that govern the system's behavior. Each invariant is a proposition that must always be true. Each one must trace to at least one condition it governs. If an invariant doesn't connect to a condition, it's either protecting against something that can't happen in your venue (dead weight) or you're missing a condition (gap in your analysis).

Invariants are not implementation instructions. They don't say HOW to enforce the rule. They state WHAT must be true. But each invariant must be grounded in the premises. It must have a home: a specific handler, a specific input, a specific output it governs. If an invariant can't name where it lives, it's a wish, not a rule.

**Template:**

{InvariantName}: {Statement of what must always be true}

  Governs: {Condition number(s)}

  Proof level: {Level 1-4 from section 4, or "derivation" for decisions
    returning a typed result variant rather than a validator}

  Home: {Which handler enforces this, on what input, 

    by refusing to produce what output}

  Rationale: {Why this rule exists, what goes wrong if violated}

**Example (inventory management):**

PosStockBuffered: Never use POS-reported stock as ground truth without

  applying the maximum reporting delay as a buffer.

  Governs: Condition 1 (POS delay)

  Proof level: derivation — `BufferedStockProjection` composes proven
    `PosStockReading` and `Duration` (max reporting delay) and yields
    a buffered stock value via `@cached_property`. Construction always
    succeeds for well-formed inputs.

  Home: The stock projection handler. When computing current

    stock from ledger entries, it subtracts a buffer equal to

    the maximum POS reporting delay times recent sales velocity

    before publishing the projected stock event.

  Rationale: Acting on overstated stock leads to missed reorders

  and stockouts.

NoDuplicateReorder: Never place a reorder for a SKU while a confirmed but

  undelivered order for that SKU exists.

  Governs: Condition 6 (Duplicate orders)

  Proof level: derivation — `ReorderEvaluation` returns
    `ReorderResult = ReorderTriggered(intent) | ReorderSuppressed(reason)`.
    When a pending order exists for the SKU, the result is
    `ReorderSuppressed(reason=PendingOrderExists)`.

  Home: The reorder handler. When it receives a reorder signal

    event, it projects pending orders from the ledger. If a

    pending order exists for that SKU, it does not publish

    a reorder event.

  Rationale: Duplicate orders create overstock and wasted capital.

SupplierUnavailableQueues: A reorder that cannot be placed due to supplier

  unavailability must be queued, not dropped.

  Governs: Condition 2 (Supplier unavailability)

  Proof level: derivation — `OrderPlacementResult = OrderPlaced(ack) |
    OrderQueued(intent)`. The result is `OrderQueued` outside business
    hours; the queued intent is held until the next admissible window.

  Home: The order placement handler. When it attempts to place

    an order and the supplier API is unavailable, it publishes

    a queued-reorder event instead of discarding the intent.

  Rationale: Dropping a valid reorder because the API is down

  means the stockout the system detected goes unaddressed.

DepletionUsesFasterVelocity: Projected depletion rate must use the faster of

  the trailing 24-hour velocity and the trailing 7-day velocity.

  Governs: Condition 3 (Demand spikes)

  Proof level: derivation — `DepletionProjection` composes the two
    proven velocity windows and yields the projected depletion rate
    via `@cached_property`, taking the maximum.

  Home: The depletion projection handler. When computing

    projected depletion from sales events, it calculates both

    windows and uses the higher rate in the published projection.

  Rationale: Using only 7-day average masks sudden acceleration

  in sales, leading to stockouts during spikes.

DeliveryRequiresPhysicalReceipt: A delivery is not confirmed until physical receipt is

  recorded, not when the supplier API acknowledges the order.

  Governs: Condition 4 (Delivery failure)

  Proof level: Level 4 — the delivery confirmation handler does not
    exist as a construction site for `SupplierAcknowledgedEvent`. The
    handler is constructed only when a `PhysicalReceiptEvent` arrives.
    Distinct event types are Level-2 narrowings; the handler's gating
    by event type is the Level-4 prerequisite.

  Home: The delivery confirmation handler. It only publishes a

    delivery-confirmed event when it receives a physical receipt

    event, not when it receives a supplier acknowledgment event.

  Rationale: Treating supplier acknowledgment as delivery

  confirmation overstates incoming stock and suppresses

  necessary reorders.

PhysicalCountOverridesCalculated: Actual shelf count, when available, overrides

  POS-calculated inventory.

  Governs: Condition 5 (Data mismatch)

  Proof level: derivation — the stock projection composes the most
    recent `PhysicalCount` (when present) with subsequent ledger
    entries; the projection's `@cached_property` for current stock
    uses the physical count as the baseline.

  Home: The stock projection handler. When it receives a

    physical-count event, it publishes an adjustment event

    that resets the projection baseline to the counted value.

  Rationale: The physical world is the source of truth.

  Calculated inventory drifts from reality over time.

ThresholdsReviewedOnCadence: Safety stock thresholds must be reviewed against actual

  demand data on a defined cadence, not set once and assumed valid.

  Governs: Condition 7 (Stale thresholds)

  Proof level: Level 4 + derivation — the threshold review handler
    is gated by the scheduled cadence (Level 4: handler absent
    between scheduled fires). When it fires, `ThresholdReview`
    composes proven demand projections and returns
    `ReviewResult = ThresholdHeld | ThresholdAdjusted(new_value)`.

  Home: The threshold review handler. On a scheduled cadence,

    it projects recent demand from sales events and publishes

    a threshold-adjustment event if the current threshold

    diverges from what the data supports.

  Rationale: Static thresholds become wrong as demand patterns

  change, leading to either stockouts or waste.

---

## 8\. Coverage

The verification step that closes the loop. Every condition must have at least one invariant. Every invariant must trace to at least one condition. Every invariant must name its proof level from section 4. Every configuration parameter from section 6 must be consumed somewhere. Coverage is the artifact that makes the trace explicit — without it, gaps and orphans hide.

**Coverage matrix — conditions to invariants:**

| Condition | Governing Invariants |
|---|---|
| {N} {name} | {invariant names that govern this condition} |

A row with no invariants is a gap. Either the condition does not actually happen in the venue (delete it from section 3) or an invariant is missing.

**Coverage matrix — invariants to conditions and proof level:**

| Invariant | Condition(s) | Proof Level |
|---|---|---|
| {InvariantName} | {N} | {Level 1-4 or derivation} |

An invariant row not traceable to any condition is dead weight — either the condition is missing or the invariant exists for a reason outside the venue.

**Validation checklist:**

- [ ] Every condition has at least one invariant governing it
- [ ] Every invariant traces to at least one condition
- [ ] Every invariant names its proof level from section 4
- [ ] Every Level-3 invariant has been tested for whether it is a Level-1 or Level-2 in disguise, or a decision returning a typed result variant rather than a validator
- [ ] Every Level-4 invariant has been tested for whether the prerequisite is genuinely external state, not a field that was never forged
- [ ] Every invariant names its home: which handler, what input, what output it governs
- [ ] Every invariant is grounded in the premises
- [ ] Every configuration parameter from section 6 is consumed by at least one handler or evaluation model
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

Invariants → Conditions and Proof Level:

| Invariant | Condition | Proof Level |
|---|---|---|
| PosStockBuffered | 1 | derivation (BufferedStockProjection) |
| SupplierUnavailableQueues | 2 | derivation (OrderPlacementResult variant) |
| DepletionUsesFasterVelocity | 3 | derivation (DepletionProjection) |
| DeliveryRequiresPhysicalReceipt | 4 | Level 4 (handler gated by event type) |
| PhysicalCountOverridesCalculated | 5 | derivation (projection baseline) |
| NoDuplicateReorder | 6 | derivation (ReorderResult variant) |
| ThresholdsReviewedOnCadence | 7 | Level 4 + derivation |

Every condition is covered. Every invariant traces to its condition. Every invariant names its proof mechanism. The foundation is closed.

If every row of every matrix has a value and every checkbox is green, downstream implementation work (the type catalog, the domain models, the `.claude/` rule files) has a stable foundation to build on. If any cell is empty or any box fails, the foundation has a crack that will propagate into every decision built on top of it.

