## Proof Obligations and the Construction Graph

Three practical lenses for designing and auditing construction graphs. They add no doctrine beyond `type-construction-architecture.md`; they are ways of using it. The catalog says construction is the proof and the program is the graph of constructions. These lenses are how you start that graph from what must be true, recover it from code that already runs, and read a shared node without overloading it.

### 1. Design from the obligation, not the shape

Begin with what must be certain for the program to be correct, named in domain language. Then name the construct whose existence is that certainty: the value that cannot be built unless the obligation holds, so its construction is the proof. Compose downward from it through declared fields and derivations until you reach the leaves, the scalars that bound the primitive value spaces.

The discipline is the order. Naming the obligation first, then the construct that discharges it, keeps you from starting at a class shape, a service template, or a transport concern before the proof target is explicit. The shape falls out of the obligation; it is not chosen ahead of it.

The same principle extends to verb chains on the consistency model. A verb body is a path in the construction graph: each statement constructs a value that some later construction depends on, and the statement order is derived from those dependencies exactly as the build order is derived from the type graph. A body has no free ordering to author. If two orderings of a body are semantically equivalent, at least one statement is not performing a real construction, which is a signal to examine what it is doing there.

### 2. Read an existing codebase by its terminals

A procedural system already has a construction graph, smeared across handlers, validators, and schemas, unnamed. You recover it for an audit or a migration by reading from the top down, even though you will rebuild it from the bottom up.

As a heuristic, not a law:

1. Enumerate the construct-bearing domain types.
2. Find which of them are composed as fields by other types.
3. The ones nothing composes are the graph's terminals: the top-level proven facts and the consistency models.
4. Trace each terminal down through its fields and derivations to the leaves.

This turns a large codebase into a finite set of terminals and makes refactor scope explicit graph by graph instead of file by file. Reading top-down recovers the structure; rebuilding it, you still start at the leaves and let proof obligations accumulate upward.

### 3. A shared leaf carries one meaning; the edge carries the role

The same leaf type can sit under two terminals by two different paths. Its intrinsic meaning does not change with position. What changes is the role, and the role is carried by the edge that references it, the field name along the path, never by the leaf.

```text
CatalogEnvironment
└── ProductRegistry        # the catalog's known set
    └── Product

OrderConfirmation
└── reserved_items         # this order's reservation
    └── Product
```

`Product` means a product in both places. "Known to the catalog" is the meaning of `ProductRegistry`; "reserved for this order" is the meaning of `reserved_items`. The leaf is shared because its intrinsic meaning is identical; the path supplies the role through its edges.

The review test follows directly. When a shared leaf feels overloaded, ask whether the edge already carries the role. If it does, the sharing is honest. If the leaf would need different intrinsic structure in the two places, a reservation quantity here, a shelf location there, then it is not one type carrying a role; it is two types, and meaning lives in the type, so you split it.
