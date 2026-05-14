# Foundational Program Design Specification

A planning artifact for establishing shared understanding before implementation. This document defines the logical foundation of a system: what it does, why, what can go wrong, and what rules govern all downstream decisions. Nothing in this document addresses infrastructure, frameworks, languages, or deployment. Those are implementation concerns that derive from this foundation. They do not shape it.

## How to use this document

Each layer derives from the one above it. If a domain invariant doesn't trace to a condition, it shouldn't exist. If a condition doesn't have at least one invariant governing it, you have a gap. Work top-down to build it. Validate bottom-up to verify it.

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

## 4\. Premises

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

## 5\. Domain Invariants

The rules that govern the system's behavior. Each invariant is a proposition that must always be true. Each one must trace to at least one condition it governs. If an invariant doesn't connect to a condition, it's either protecting against something that can't happen in your venue (dead weight) or you're missing a condition (gap in your analysis).

Invariants are not implementation instructions. They don't say HOW to enforce the rule. They state WHAT must be true. But each invariant must be grounded in the premises. It must have a home: a specific handler, a specific input, a specific output it governs. If an invariant can't name where it lives, it's a wish, not a rule.

**Template:**

INV-{N}: {Statement of what must always be true}

  Governs: {Condition number(s)}

  Home: {Which handler enforces this, on what input, 

    by refusing to produce what output}

  Rationale: {Why this rule exists, what goes wrong if violated}

**Example (inventory management):**

INV-1: Never use POS-reported stock as ground truth without

  applying the maximum reporting delay as a buffer.

  Governs: Condition 1 (POS delay)

  Home: The stock projection handler. When computing current

    stock from ledger entries, it subtracts a buffer equal to

    the maximum POS reporting delay times recent sales velocity

    before publishing the projected stock event.

  Rationale: Acting on overstated stock leads to missed reorders

  and stockouts.

INV-2: Never place a reorder for a SKU while a confirmed but

  undelivered order for that SKU exists.

  Governs: Condition 6 (Duplicate orders)

  Home: The reorder handler. When it receives a reorder signal

    event, it projects pending orders from the ledger. If a

    pending order exists for that SKU, it does not publish

    a reorder event.

  Rationale: Duplicate orders create overstock and wasted capital.

INV-3: A reorder that cannot be placed due to supplier

  unavailability must be queued, not dropped.

  Governs: Condition 2 (Supplier unavailability)

  Home: The order placement handler. When it attempts to place

    an order and the supplier API is unavailable, it publishes

    a queued-reorder event instead of discarding the intent.

  Rationale: Dropping a valid reorder because the API is down

  means the stockout the system detected goes unaddressed.

INV-4: Projected depletion rate must use the faster of

  the trailing 24-hour velocity and the trailing 7-day velocity.

  Governs: Condition 3 (Demand spikes)

  Home: The depletion projection handler. When computing

    projected depletion from sales events, it calculates both

    windows and uses the higher rate in the published projection.

  Rationale: Using only 7-day average masks sudden acceleration

  in sales, leading to stockouts during spikes.

INV-5: A delivery is not confirmed until physical receipt is

  recorded, not when the supplier API acknowledges the order.

  Governs: Condition 4 (Delivery failure)

  Home: The delivery confirmation handler. It only publishes a

    delivery-confirmed event when it receives a physical receipt

    event, not when it receives a supplier acknowledgment event.

  Rationale: Treating supplier acknowledgment as delivery

  confirmation overstates incoming stock and suppresses

  necessary reorders.

INV-6: Actual shelf count, when available, overrides

  POS-calculated inventory.

  Governs: Condition 5 (Data mismatch)

  Home: The stock projection handler. When it receives a

    physical-count event, it publishes an adjustment event

    that resets the projection baseline to the counted value.

  Rationale: The physical world is the source of truth.

  Calculated inventory drifts from reality over time.

INV-7: Safety stock thresholds must be reviewed against actual

  demand data on a defined cadence, not set once and assumed valid.

  Governs: Condition 7 (Stale thresholds)

  Home: The threshold review handler. On a scheduled cadence,

    it projects recent demand from sales events and publishes

    a threshold-adjustment event if the current threshold

    diverges from what the data supports.

  Rationale: Static thresholds become wrong as demand patterns

  change, leading to either stockouts or waste.

---

## Validation checklist

After completing all five sections, verify:

- [ ] Every invariant traces to at least one condition  
- [ ] Every condition has at least one invariant governing it  
- [ ] Every invariant names its home: which handler, what input, what output it governs  
- [ ] Every invariant is grounded in the premises  
- [ ] No invariant references a constraint that doesn't exist in your venue  
- [ ] No invariant prescribes implementation (HOW) rather than stating a rule (WHAT)  
- [ ] Premises are structural axioms, not domain rules disguised as premises  
- [ ] The scope explicitly excludes things that participants might assume  
- [ ] The strategy is explainable without referencing technology  
- [ ] The conditions list includes things that WILL happen, not hypotheticals

If all boxes check, the downstream implementation work (architecture, models, infrastructure, deployment) has a stable foundation to build on. If any box fails, the foundation has a crack that will propagate into every decision built on top of it.

