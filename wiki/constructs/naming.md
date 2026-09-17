---
type: Reference
description: How every structure is named for the domain thing or fact it carries.
---

# Naming

Name every structure for the domain thing or fact it carries, never a pipeline stage, a data direction, or a processing step. A domain expert must recognize the thing without describing the data flow. Domain filenames follow the same rule in [program topology](../topology/program-topology.md).

Banned names and generic suffixes: `Record`, `Item`, `Data`, `Payload`, `Result`, `Entry`, `Info`, `Handler`, `Manager`, `Processor`, `Incoming`, `Outgoing`, `Processed`, `Enriched`, and the `Event` suffix. Each of these describes what the program did to the data rather than what the thing is, so a structure carrying one has a name that says nothing about the world and both readers, checker and model, get no meaning from it. `Result` on a transformation is the proof that its fact was never identified: the author knew a computation happened and did not know what it produced.

The name is where the [world is decided](../doctrine/definition.md) or shown not to be. "Found" is the program's act of looking; nobody in a venue finds a price. "Filled" and "Refused" are facts, because the venue fills and refuses orders. A name that describes the program's act is evidence that the thing was never located in the world, which is the escaped break at the point where it is cheapest to see.

Role suffixes are banned on domain declarations because an implementation role does not identify a domain thing. Exactly two edge suffixes are admitted, `Route` and `Interpreter`: those declarations own crossings, not additional domain meanings. Keep the domain prefix, `FillRoute` and `PersistPositionInterpreter`, and do not apply these suffixes to domain models or generalize the exception to other roles.
