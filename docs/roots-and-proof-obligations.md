# Roots and Proof Obligations

A TCA program begins by asking what must be proven for the program to be correct. Each answer becomes a root. The number of roots follows from the domain, not from architecture fashion or service templates.

---

## Start With The Obligation

The first design question is not "what classes do I need?" or "what service do I build?" It is "what must be certain before this program can be correct?"

For a classifier, the answer is: the target's fields are structurally classified. One obligation, one root.

For a context program, the answers are typically: the environment is ready, the action is expressible, and the result is complete. Three obligations, three roots.

For a data pipeline, the answers might be: the source conforms, the transformations are valid, intermediate checkpoints pass, the destination schema holds, the reconciliation report balances. Five or more obligations, five or more roots.

The number is not fixed. It follows from the domain. Name the obligations first. The roots follow.

---

## What Makes A Root

A root is a type whose successful construction discharges one proof obligation. Every non-root type exists because some root needs it — directly or transitively through field annotations.

Roots are not the same as "important types." A `FieldSlot` model may be important, but it is probably not a root. It exists because some larger root such as `ModelTree` or `ClassifierRun` references it. The root is the type whose construction proves something about the whole program's correctness.

Roots are computable. Collect all `BaseModel` subclasses in a codebase, subtract every type that appears in another type's field annotations, and the remainder are the roots. This works in both directions: forward in greenfield development (name the roots, define their fields, everything cascades), and backward in existing code (compute roots, follow annotations, discover the construction graph).

---

## Pattern Families

### One root: a classifier

The [building block classifier](building-block-classifier.md) has one proof obligation: that a model's fields are structurally classified. One root discharges it:

```python
tree = ModelTree.model_validate(Team)
```

`ModelTree` is the root. Its construction proves that every field on `Team` has been classified into a structural building block.

### Three roots: a context program

A context program that takes typed input and produces typed output within a typed context has three proof obligations:

**That the environment is ready.** The program can only act if its context is valid: dependencies are loaded, registries are populated, configuration is parsed. The **Environment** root discharges this:

```python
class CatalogEnvironment(BaseModel, frozen=True, extra="forbid"):
    product_registry: ProductRegistry
    inventory_snapshot: InventorySnapshot
    pricing_rules: PricingRules
```

**That the action is expressible.** The program can only act on requests its vocabulary can represent. The **Action** root discharges this:

```python
class PlaceOrder(BaseModel, frozen=True, extra="forbid"):
    customer_id: CustomerId
    line_items: tuple[OrderLine, ...]
```

**That the result is complete and consistent.** The **Result** root discharges this:

```python
class OrderConfirmation(BaseModel, frozen=True, extra="forbid"):
    order_id: OrderId
    reserved_items: tuple[ReservedItem, ...]
    fulfillment_estimate: FulfillmentEstimate
```

Three roots because three distinct proof obligations. The semantic link between Environment + Action and Result is still the construction-derivation graph: eager field ownership plus lazy projections that extend proof. Only the transport, persistence, triggering, or wake-up mechanics around that graph are plumbing. The better framing is three roots for a context program, not "three roots for a service" — the [service is thin or absent](program-topology.md).

### More roots: a pipeline

A data pipeline may have five or ten proof obligations: source schema, transformation rules, intermediate checkpoints, destination schema, reconciliation report. Each is a root type whose construction discharges that obligation.

---

## Shared Nodes And Positional Meaning

The same type may appear under multiple roots, but its meaning changes with its path.

```
CatalogEnvironment
├── ProductRegistry
│   └── Product            ← "a product known to the running catalog"

OrderConfirmation
├── reserved_items: tuple[ReservedItem, ...]
│   └── Product            ← "the product reserved on behalf of this order"
```

`Product` appears under both roots, but the positional meaning differs. Under `CatalogEnvironment`, a `Product` is part of the live world the program can see. Under `OrderConfirmation`, a `Product` is the item committed to a specific outcome. The field path from root to leaf is a sentence in the domain's language.

Shared nodes are natural and correct. They indicate that different parts of the program need the same proof about the same concept. If the meaning genuinely diverges between contexts, they should be distinct types.

---

## Discovering Roots In Existing Systems

In a mature codebase, roots can be discovered mechanically:

1. Collect all `BaseModel` subclasses
2. Subtract every type that appears in another type's field annotations
3. The remainder are the roots

This gives you the program's proof structure whether or not anyone designed it deliberately.

In a greenfield system, the process is reversed: name the proof obligations, define the root types that discharge them, and build the graph downward. Development proceeds from roots to leaves.

---

## Roots, Graphs, And Demand

Roots anchor eager field graphs — the DAG of what must succeed for the root to construct. But their projections may extend proof lazily into new subgraphs.

In the building block classifier, `ClassifierRun.tree` is a derivation edge from `ClassifierRun` to `ModelTree`. `ClassifierRun.report` is a derivation edge from `ClassifierRun` to `TreeReport`. These edges are lazy: the objects they produce exist only when something demands them. The full proof graph is the union of field edges and derivation edges.

Pydantic generic models (`class Envelope(BaseModel, Generic[T])`) create parametric construction machines. `Envelope[Order]` and `Envelope[Product]` are different nodes in the construction graph generated from the same template. This is parametric polymorphism applied to construction: define the proof structure once, instantiate it for any payload type.
