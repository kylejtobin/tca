# 0044. Several of one thing is a child scope per element, placed by the proof as a path of element classes

Status: accepted

## Context

A request holds several elements; each is asked about, valued and concluded on its own; the whole is concluded once from all of them. A party's answer about one element may itself hold several parts, each with its own value. A run holds one instance per class in a scope, and `tuple[E, ...]` on a request or a record names several.

## Rejected

A loop on the page. An engine class for a batch, a mapping or a context. One run holding several instances of one class under one key. A scope map computed before the run that said, per class, which element it exists per, with `None` for once per run. Scope decided at run time by `descends`, a graph walk from each class to the element it reached through fields, hearers, carriers and producers, which supported one level of elements, refused a record heard per element that held a collection, and refused a class that reached two elements without saying where it would live. Occurrence identities of the form `(revision, run, constructor, bound inputs, occurrence)` with explicit bindings elaborated by a compiler: provenance computed and matched instead of inherited.

## Decision

A placement is a path of element classes. `()` is once per run; `(E,)` is once per element `E` of the request or record that declares it; `(E, I)` is once per inner element `I` of each `E`. The proof places an element one level under what declares it, a record where its hearer is, a scalar or value where its carrier is, and every other class at the finest placement its premises name, which every other premise's placement must be a prefix of, and one level above each class it collects, which must be exactly that level; it refuses as `unplaceable` a class whose fields name sibling elements, as `collects` a tuple over a class placed once per run or more than one level down, and as `route` a route placed anywhere but `()`. Nesting is the same rule applied again: a record heard at `(E,)` that declares `I` places `I` at `(E, I)`, a derivation over `I`'s scalars and `E`'s record lives at `(E, I)`, and a sum over it lives at `(E,)`.

A run is a tree of scopes with the same shape. A scope holds its own instances over its ancestors', as a `ChainMap`, and one list of child scopes per element class, in element order. When a request or a record enters a scope, each tuple it holds fans out: one child scope per element, holding the element and what it carries; an element class with no element gets an empty list. A class is asked for in every scope at its placement. A tuple field is supplied once the holder of its elements has arrived and every child holds an instance, in element order, and is the empty tuple when the holder fanned out to nothing, so a sum of nothing is zero and a selection of nothing refuses (0049). Provenance is inheritance: everything built inside an element's scope shares that element by being there, and no join is computed, keyed or matched.

## Evidence

In the engine's test program, `Elements` declares `each: tuple[Element, ...]` and `Heard`, heard per element, declares `parts: tuple[Part, ...]`: the proof placed `Element`, `Name`, `Asked`, `Heard`, `Amount`, `Portions`, `Largest`, `Low`, `Notify`, `Noted` and `Cheap` at `(Element,)`, `Part`, `Share` and `Portion` at `(Element, Part)`, and `Elements`, `Limit`, `Total`, `Concluded` and `Operation` at `()`. Two elements, each with two parts of a half: `Portion` was `1.250` in each part's scope, `Portions` was `2.500` in each element's scope, `Concluded.valued` held two `Cheap` in element order and `Total` was `5.00`; with no element, `valued` was the empty tuple and `Total` was `0`. In the program with the faults, `Twin`, holding an `Element` and a `Second` from two tuples of the request, was refused as `unplaceable`; `Collects`, collecting `Total`, as `collects`; `Misplaced`, whose reply holds `Cheap`, as `route`.

## Consequences

A page writes `tuple[...]` on the request or the record that holds several, and on the fact that collects, and nothing else; depth is free. A fact over two sibling elements is unwritable: a pairing that exists in the business is an element of its own, declared by a request or a record. Refuted by an element that must come from inside a value; then the value fans out too.
