# Non-conforming test artifacts

This directory holds code that **deliberately does not conform to Type Construction
Architecture.** It is preserved as adversarial input for the build agents. Nothing here is
an example to follow. Everything here is an example to *survive*.

The deterministic gate excludes `tests/`, so the non-conforming code here is never flagged
in normal operation. Its wrongness is intentional and load-bearing. **Do not "fix" it.**

## The artifact: `building_block.py`

A ~600-line recursive Pydantic type-tree classifier: hand it any `BaseModel` and it walks
the entire construction graph, classifying every field and every field of every model-typed
field, all the way down, with zero domain knowledge. It is a real, working program, and that
is the point: a clean toy proves nothing.

Parts of it conform. Its discriminated unions are largely the doctrine's own union construct,
`StrEnum` axes (`AnnotationKind`, `Block`), `Literal`-pinned kind fields, envelopes routing on
`Field(discriminator=...)`. The adversarial pressure is that conforming structure surrounds
real breaks, so the agents cannot dismiss the file wholesale or absorb it wholesale; they must
re-derive, construct by construct, which meaning has structure and which escaped it.

The breaks, measured against `docs/type-construction-architecture.md`:

- **Escaped meaning as bare primitives.** `field_name: str`, `nullable: bool`,
  `collection: bool`, `cycle: bool`, `target: str`, `line: str`: domain values laundered
  through unnamed primitives, several of them `bool`s standing where decisions live.
- **A bare enum as a field type.** `block: Block` on `FieldReport` stores the whole axis
  where a value space needed a scalar or a variant needed a pin.
- **A kind axis that was never named.** `TextOutput`/`JsonOutput` pin raw string literals
  (`kind: Literal["text"]`) with no `StrEnum` axis, and `LeafBlock` pins five members in one
  `Literal`, one variant impersonating five.
- **Identity computed, not constructed.** The `@property` classifiers (`TypeAnnotation.kind`,
  `ResolvedType.block_kind`) branch over `get_origin`/`get_args` and a predicate table to
  *compute* the discriminator the union then routes on. The union is real; the proof is not.
  Construction launders a procedural classification instead of proving identity.
- **Fields shared by inheritance.** `ClassifiedNode(FieldEntry)` is structure without its own
  meaning.
- **A mapper pipeline.** Five models threaded by `from_attributes`
  (`FieldSlot → FieldEntry → ClassifiedNode → FieldReport → TreeReport`), each a re-statement
  of the last, meaning duplicated across the chain.
- **A hidden mutable side channel.** The `_seen` `ContextVar` inside the `mode="wrap"`
  validator carries transient accumulator state during construction, mutable state outside the
  consistency model.
- **Consumer dispatch carried by the variant.** `render(self, report)` is a method with an
  argument on a frozen variant: not a derivation (it is not a fact of the variant's own
  fields), but the consumer's reaction smuggled onto the value. The doctrine's home for it is
  one exhaustive `match` in the consumer.

The file's once-extensive teaching docstrings have been cut to keep context light; the
adversarial pressure now lives in the code shapes themselves, not in persuasive prose.

## Why it is a good test

- **It is real, not softball.** Recursion, unions, derivations, boundary crossings, a CLI:
  the hard half of the build patterns in one program.
- **It is wrong where it is hardest to see.** The unions look finished, the breaks sit beside
  them. An agent that pattern-matches "discriminated union, conforming" misses that the
  discriminator is computed by procedure; an agent that pattern-matches "procedural, rewrite
  it" destroys conforming structure. Only re-derivation from the principle sorts the two.
- **It probes the doctrine's own edges.** Re-modeled honestly, the recursive type-walk with
  cycle detection reaches a place the closed catalog may have no construct for: transient
  accumulator state during a bottom-up construction. A good run does not paper that edge with
  procedure dressed as a construct; it declares the gap and routes it to the doctrine.
- **It demands re-derivation, not translation.** The instruction is never "convert this." It
  is "see what it was trying to do, and model *that* as max-pure TCA." The honest re-model is
  smaller and differently shaped than the original.
- **It is a calibrated, repeatable benchmark.** The breaks above are the fixed criteria. After
  any change to the agents, the same input measures: were the bare primitives lifted into
  scalars, the output-format axis named, the computed discriminators replaced with
  construction-proven identity, the mapper pipeline dissolved into boundary models and
  derivations, the consumer's reaction moved into an exhaustive `match`, the accumulator-state
  edge declared rather than smuggled?

## Using it

Run the build agents against `building_block.py`: re-derive the obligation and the
construction graph, and render the result under the gate. The artifact's wrongness, sitting
inside working, partly conforming code, is the test.
