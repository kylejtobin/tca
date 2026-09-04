---
type: Reference
description: How to design from a proof obligation and recover a construction graph from existing code.
---

# Proof Obligations and the Construction Graph

This is a practice guide. It adds no doctrine beyond the [construct pages](../constructs/index.md); it teaches ways to use that doctrine when a model is still forming, when an existing codebase needs to be audited, or when a shared type feels suspicious.

The core rule is simple: construction is the proof, and the program is the graph of constructions. A good graph starts from what must be true, names the value whose existence proves it, and lets the required dependencies become visible.

## 1. Design From The Obligation

Begin with what must be certain for the program to be correct, named in domain language. Then name the construct whose existence is that certainty: the value that cannot be built unless the obligation holds.

That order matters. If you start with a class shape, service template, handler, or transport concern, the proof target is already displaced. Starting with the obligation keeps the question sharp: what object must exist for this fact to be proven?

Once the proof target is named, compose downward through declared fields and derivations until you reach semantic scalars. The leaves bound primitive value spaces; the composites name the facts those leaves make possible; the terminal values are the facts the application acts on.

State transitions obey the same discipline, but they do not become free-form chains. Current verb doctrine allows at most one construction statement in a consistency-model verb; constituents construct inside that one call. If a transition seems to need staged constructions, the model is saying a composite, derivation, ordered union, route, or boundary model is missing from the graph. Do not turn that need into steps. Name the missing structure.

## 2. Read Existing Code By Its Terminals

A procedural system already has a construction graph, smeared across handlers, validators, schemas, mappers, and services. The graph is real, but unnamed. You recover it for an audit or migration by reading from the top down, even though a clean TCA build starts from the leaves.

As a heuristic, not a law:

1. Enumerate the domain values, facts, choices, collections, and live state holders that already exist.
2. Find which types are composed as fields by other types.
3. Treat the types nothing else composes as likely terminals: top-level proven facts, route replies, persisted state facts, and consistency models.
4. Trace each terminal down through fields, variants, and derivations until you reach leaf values.
5. Mark every place meaning escaped into a validator, mapper, service method, comment, or convention.

This turns a large codebase into a finite set of graph slices. Refactor scope becomes explicit graph by graph instead of file by file. Reading top-down recovers the obligations; rebuilding still starts at the leaves and lets proof obligations accumulate upward.

## 3. Let Edges Carry Roles

The same leaf type can sit under two terminals by two different paths. Its intrinsic meaning does not change with position. What changes is the role, and the role is carried by the edge that references it, usually the field name along the path, never by the leaf.

```text
CatalogEnvironment
└── ProductRegistry        # the catalog's known set
    └── Product

OrderConfirmation
└── reserved_items         # this order's reservation
    └── Product
```

`Product` means a product in both places. "Known to the catalog" is the meaning of `ProductRegistry`; "reserved for this order" is the meaning of `reserved_items`. The leaf is shared because its intrinsic meaning is identical; the path supplies the role through its edges.

The review test follows directly. When a shared leaf feels overloaded, ask whether the edge already carries the role. If it does, the sharing is honest. If the leaf would need different intrinsic structure in the two places, a reservation quantity here, a shelf location there, then it is not one type carrying a role. It is two types, and meaning lives in the type, so you split it.

## The Working Question

For any proposed shape, ask: what proof obligation does this construction discharge, and where is that obligation carried in the graph?

If the answer is "in the next step," the meaning has escaped into procedure. If the answer is "in two places," the meaning is duplicated. If the answer is "nowhere," the structure is vacuous. If the answer names two obligations at once, the structure is fused. The four breaks from [`definition.md`](../doctrine/definition.md) become practical because the graph gives you somewhere to point.
