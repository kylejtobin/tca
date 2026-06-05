---
name: disjointness
description: The decision made before any closed vocabulary or union is modeled — dimensionality sorts a scalar from a union, and the drop-test proves a union's variants disjoint. Use when modeling a set of "kinds," or the instant you reach for an enum, a tag, a discriminator, or a match over a union.
---

# Disjointness

The shape of a closed set of things is decided before it is written, by two tests run in
order. This is the modeling move the architect makes and the forge renders; the authority
is `docs/type-construction-architecture.md` (the Union and Semantic scalar constructs),
and this is the procedure for the decision, not a second copy of the doctrine.

## 1. Dimensionality decides scalar versus union

A closed vocabulary sorts by dimensionality, not by size or count.

- One axis, every member the same kind of thing (which suit, which currency, which
  severity): it is a **semantic scalar** over a `StrEnum` value space. Named once, proven
  at construction, never branched on.
- Members carrying distinct structure or behavior a sibling lacks (different fields, a
  different derivation): it is a **union** of disjoint variant models.

When a flat vocabulary feels like a bag, it has fused several axes into one label list.
Name the axes: the members that carry their own payload become the variants of a union; a
payload-free axis that cut across them becomes a variant-carried derivation. Two structures
fall out of the bag, and neither is a label.

## 2. The drop-test proves a union disjoint

Distinct is not disjoint. Distinct is different fields; disjoint is that no payload builds
more than one variant. The test:

1. Drop every optional field and delete every field that names the kind.
2. Construct the minimal remaining payload, the one where two variants most easily collide.
3. Run it through the `RootModel[A | B | C]` envelope on the substrate (`uv run`) and see
   how many variants land. Run it; do not reason it.

If exactly one lands, the union is disjoint and any tag was redundant. If not, one of three
things is wrong, each with an opposite move:

- The variants are not actually distinct → there is no union; collapse them into the one
  model they always were.
- The distinction is real but its structure is missing → add the fields that make each
  variant land on its own.
- Nothing in the program branches on the kind → it was never a union but a uniform
  vocabulary, a semantic scalar over a `StrEnum` value space.

Disjointness, once proven, is discharged into the structure exactly as `gt=0` is, held by
construction for the life of the program. There is no stored discriminator and no tag: the
drop-test tells the variants apart, and the variants' own names carry their salience.
