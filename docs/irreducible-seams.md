# Irreducible Seams

Some boundaries cannot be crossed with pure construction. At those boundaries, one small validator or connector bridges the gap. Everywhere else, the type tree owns the logic. Identifying the irreducible procedural minimum is a core TCA discipline and one of the primary architectural tests of whether a program is well-shaped.

---

## The Governing Test

If code is procedural, the question is not "does this feel procedural?" or "can I remove it?" It is:

> Is this boundary truly inexpressible through field declarations, aliases, discriminated unions, `from_attributes`, or projections?

Every piece of procedure in a TCA program must justify itself against this test. If it cannot, it is not a seam — it is a modeling failure. The distinction matters because a seam gets one tiny validator and stays small, while a modeling failure gets a better type and disappears entirely.

---

## Seam Or Modeling Failure?

Many things that look irreducible are actually missing models, missing intermediary shapes, or missing dispatch. Before blessing a piece of procedure as a necessary seam, check:

- **Can an intermediate model make the shape fit?** If two models don't wire directly, a bridging model with the right field names and aliases may collapse the adapter code.
- **Can a discriminated union absorb the branching?** If the procedure selects behavior based on a tag or type, a DU can dispatch during construction instead.
- **Can `from_attributes` and aliases replace the mapping?** If the procedure translates names between two objects, the translation may belong on the target model's field declarations.
- **Can a `@property` bridge the gap?** If the procedure computes something from a model's own fields to feed downstream construction, it is an intrinsic derivation that belongs on the model.

If the answer to all four is no, the boundary is real.

---

## Legitimate Seam Classes

Some seams resist pure construction:

**Live input capture.** Websocket frames, stream chunks, and callback payloads arrive through effectful runtime surfaces. Someone must catch the raw message and hand it to construction. The key is that capture is not where business meaning lives. It is a tiny outer seam that moves unstable transport reality into a typed entry point.

**Payload normalization.** A third-party payload may wrap the actual fields one layer deeper, or mix transport metadata with domain-bearing content. A small before-validator can unwrap or normalize the payload once so the construction graph can resume. This is legitimate only when the reshaping truly belongs to the boundary and remains terminal.

**Positional-to-named bridging.** Python's `dict.items()` produces `(key, value)` tuples where the key is positional, not an attribute on the value. Someone must pair them into named fields. The [building block classifier](building-block-classifier.md) has exactly one such seam: the wrap validator on `ModelTree` that iterates `model_fields.items()` and constructs `FieldSlot` instances.

**Dynamic imports and resolution.** `importlib.import_module` and `getattr` are inherently dynamic. When the input is a string that names a module and class, the boundary between string and resolved type is irreducible.

**Untyped runtime surfaces.** Some frameworks and libraries expose untyped interfaces: raw dicts, generic `Any`-typed callbacks, or stringly-typed configuration. The seam is the boundary where untyped external surface meets typed internal world.

**Effectful integrations.** Streaming, websockets, database connections, and external API calls involve I/O that cannot be expressed as pure construction. These are [effect seams](#effects-as-the-outermost-seam).

---

## Seam Hygiene

A real seam should be:

- **Tiny.** One small validator. One short connector function. A few lines, not a method with branching logic.
- **Explicit.** Visibly located at the boundary it bridges. Not buried inside a helper module.
- **Locally owned.** Owned by the model or context that needs the bridge, not by a shared utility.
- **Non-accumulating.** It does exactly one thing: bridge the boundary. It does not grow additional responsibilities over time.

The anti-pattern is a seam that starts as one validator and gradually absorbs mapping logic, enrichment, branching, and error handling until it becomes a service method in disguise. Seam hygiene means resisting that growth. If a seam is growing, it is exerting design pressure — the answer is usually a better model, not a bigger seam.

---

## Pressure Toward Better Modeling

Every seam exerts design pressure. A seam that persists across iterations may indicate:

- A missing intermediary model that would make the shape fit
- A smarter alias that would collapse the translation
- A discriminated union not yet declared that would absorb the branching
- A `from_attributes` wiring not yet discovered that would eliminate the adapter

The discipline is to treat seams as temporary pressure points unless proven otherwise. Each iteration, ask whether better modeling can absorb the seam. When it truly cannot, the seam is irreducible — accept it, keep it tiny, and move on.

---

## Effects As The Outermost Seam

Effects are a special class of irreducible seam. Construction must remain pure; effects belong after proof.

`model_post_init` is one legitimate post-proof hook for effects that must fire immediately upon construction — registration, indexing, notification. The model is frozen by the time `model_post_init` fires; it may change the world, but it must not change the object.

Many effects belong outside the model lifecycle entirely. Service orchestration, I/O, external commands are plumbing that runs after the proven object is returned. The principle is: proof first, then effect.

When a program genuinely needs ongoing operational behavior — catching streaming content, managing websocket state, coordinating long-running I/O — an active model or thin operational shell may be justified. But this is the outermost seam in a well-shaped TCA program. The interior remains certain modeled context. The active shell wraps the construction graph, receives proven objects, and does what must be done in the world.

This is the practical architectural test: capture live input, normalize it if necessary, get back to construction immediately, and keep the effectful shell outside the semantic center of the program.
