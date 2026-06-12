---
name: tca-projection
description: Project typed truth out of the graph, the only legal exit. MUST be consulted before any serialization, response body, published event, or stored write. Replaces the forbidden forms; if a hand-formatted string, an f-string assembling fields, a manual dict build, or a custom serializer is about to appear, stop and project the model instead.
---

# projection

Projection is how typed truth leaves the graph: `model_dump` and `model_dump_json`,
the exit relation, and nothing more. It is a use of a frozen model, never a structure
of its own, and it carries no judgment: no field selection, no renaming, no reshaping
on the way out. `model_dump()` takes no `include`/`exclude`/`by_alias` arguments here;
a selective or reshaped dump is meaning relocated into serialization options, the
escape hatch this card exists to close. When the wire needs a different shape than the
fact, that shape is its own model, the outward-facing boundary contract
(`tca-boundary`), constructed from the fact and then dumped whole. The work is always
construction; the exit is always bare.

    event_json = AnalysisSucceededEvent(
        file_path=file_context.file_path,
        smell_count=smells.smell_count,
    ).model_dump_json()

A projected fact carries its identity (the defaulted kind pin projects into every
dump), so the far side re-proves it by discriminated construction at its own boundary;
projection and re-proof are the two halves of one crossing:

    self.bus.publish(outcome.subject.root, outcome.model_dump_json())     # this side
    outcome = OrderOutcome.model_validate_json(message.data)              # far side

A derivation that must appear in the dump is `@computed_field` over `@cached_property`
(`tca-derivation`); nothing else changes about it. Scalars project as their primitives
and enums as their plain strings; `.root` unwrapping by hand is legal only at a foreign
seam whose API takes the primitive (a client call, a meter attribute), never to build
output the model can project itself.

The contrast that fails the test: `f"{order.side.root}:{order.price.root}"` is meaning
escaped into a format convention; the reader on the far side now parses what was
already structure. Project the model; the fields stay labeled.

## The row

Projection has no row: it is the exit edge of rows that already exist. A verb's `emits`
cells (`tca-consistency-model`) name the facts whose projections leave through clients;
a boundary model facing outward (`tca-boundary`) is the shape a reply projects through.

## Allowed patterns

- `model_dump_json()` / `model_dump()` on a constructed fact, at an emit or a reply
- the far side re-proving by discriminated construction at its own boundary
- `@computed_field` for a derivation that must ride the dump
- `.root` unwrap only at a foreign seam whose API takes the primitive

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
