# Type Construction Architecture

## Definition

Type Construction Architecture (TCA) is a software design paradigm built on one principle: **meaning lives in the structure of the type, and construction is its proof.** A value's existence is the evidence that its constraints held, so an illegal value cannot be built. Lived to its precise form, the principle is a one-to-one correspondence between the domain's meanings and the program's structures: every meaning has exactly one structural home, and every structure carries exactly one meaning. TCA is the continuous application of that correspondence as a test, a pattern kept wherever it holds the correspondence and broken wherever it breaks it.

Carried to its conclusion, the correspondence makes the program an **executable ontology**. The domain's concepts, relations, constraints, and vocabularies are the program's types, fields, derivations, and the construction graph that joins them, not a model kept in a separate artifact the program consults. The type is the concept, the field is the relation, construction is the inference that proves a fact. There is no second copy of the meaning to hold in agreement, because the correspondence is one-to-one: a meaning that needed a second copy would be a meaning wearing two structures, and that is already the architecture failing.

The principle was already sound when type-driven design first argued it for the machine compiler, the reader that erases names and reads structure to decide what is valid. It binds harder now, because a second reader has arrived. A language model reads the names and descriptions as instructions and decides what is likely, so the same typed declaration is read by both: the structure written to prove correctness to the machine is identically what programs and bounds the model. The correspondence serves both readers at once, since one structure carrying one meaning is a single constraint to the machine and a single named instruction to the model, while a structure that carries several meanings, or a meaning smeared across several structures, dulls both readers together. For software built on a language model the executable ontology stops being good taste and becomes the substrate, because every gap between the meaning and the running program is now paid on every inference.

### The Core Test
Every programming rule faces one question: *does it hold the correspondence, or break it?* Concretely, does each meaning land in exactly one structure, and does each structure mean exactly one thing? Held correctly, a meaning is stated once, in one structure, and proven by construction; broken, it is restated by hand, duplicated, left as noise, or fused with others. This is the logical extreme of type-driven design, and it sorts the whole inherited rulebook into what TCA keeps and what it breaks.

### The Four Breaks
The correspondence fails in exactly four ways, and naming them names everything the architecture forbids. A meaning can have **no structure**, escaped into a comment, a procedure, or a convention the type does not carry. A meaning can have **more than one structure**, a second copy kept in agreement by hand, a stored tag beside the fields that already prove it, one rule restated across layers. A structure can have **no meaning**, a type minted to save repetition or a name that says nothing real, noise the graph carries that no reader can use. A structure can have **more than one meaning**, several axes of the domain fused into one field or one label set, so the type holds them all and tells none of them cleanly. Escaped, duplicated, vacuous, fused. Every forbidden pattern is one of these, and every approved construct is a shape that holds one meaning, once, and proves it by construction.

### Inherited Principles
TCA keeps the rules that build the correspondence, forcing meaning into structure and proving structure by construction.

- **Parse, don't validate.** Construction yields a value whose existence is the proof; the unproven value never moves forward. The structure is the meaning, so nothing is left to check after it.
- **Make illegal states unrepresentable.** The constraint is the edge of what the type admits, not a check run afterward, so a meaning has no illegal value to mishandle.
- **Model the domain, never the primitive.** Every domain meaning gets its own named structure that travels to every reader; a primitive with its meaning in a comment is a meaning with no structure.
- **Immutability.** A proven structure is fixed at construction, so its one meaning cannot drift out from under the proof. This holds for every model except the single active model, the one live node a context allows.

### Broken Rules
TCA breaks the patterns that break the correspondence. Each is one of the four breaks above.

- **Validation as a step.** A separate check holds the constraint while a validated-but-still-present value moves on untyped, so the meaning has escaped into the step. Construction is the check, and no unproven value survives it.
- **Functions as the unit of logic.** A function computing from a model's own fields is a derivation escaped from the model, its meaning living outside the structure it belongs to. Construction and derivation do the work.
- **Procedural layering.** The validator, mapper, and handler stack is one meaning restated across layers, duplicated and kept in agreement by hand. TCA keeps the structural separation, each layer owning a distinct construct so the meaning lives in exactly one place, and breaks the layering that copies it across them.
- **Unions that need a discriminator.** A stored tag is a second copy of the identity the disjoint fields already carry, the kind duplicated beside the structure that proves it. The variants' disjoint structure carries identity and construction selects the one a value satisfies; the tag's other jobs, telling variants apart at design and giving the model a name to read, are served better by a design-time disjointness test and by the variants' own names.
- **Inert naming.** Treating a rename as a no-op assumes the name carries no meaning, but the name is a structure both readers consume, so a name that says nothing is a vacuous structure and a rename is a behavioral change. Alpha equivalence never held for production types.
- **Predicates returning booleans.** A decision flattened to one bit fuses distinct outcomes, each with its own payload, into true and false and loses them. A decision is a union of typed result variants whose existence carries the answer.
- **Enums as closed labels.** A flat set of labels standing in for a real distinction fuses what should be separate: when its members carry their own structure or behavior, several axes of the domain are crushed into one label set. Factor by dimensionality, not size. A uniform one-axis vocabulary is a single shape and stays a semantic scalar, its closed value set named rather than scattered as bare literals; members that carry distinct structure or behavior are the variants of a union, each holding its own.
- **I/O barred from domain models.** I/O is real and is not banished, it is confined to where the graph meets time: the single unfrozen active model holds the live edge, and every frozen model holds none.

## Frequently Asked Questions

Each answer meets a pull the training corpus exerts and redirects it to the construct that already holds the meaning. The construct sections above are the definitions; these are the definitions read back from the wrong instinct a reader arrives with.

**Q: Where does a closed vocabulary with no per-variant behavior live?**

A scalar, whatever its size. The scalar-versus-union line is dimensionality, not count: a uniform vocabulary varies along one axis with every member the same kind of thing, which suit, which currency, which severity, so it is one shape with a closed value set and stays a semantic scalar. Write that value set as a `StrEnum` and wrap it in the scalar (`RootModel[Suit]`), so the vocabulary is named in one place rather than scattered as bare string literals, and construction proves membership. It becomes a union only when the members stop being uniform, when one carries structure or behavior a sibling lacks. The tell is the bag-feeling: an enum that has started to feel like a bag is members accreting per-member meaning the flat set cannot hold, two or more axes fused into one label list, and the cure is to name the axes until each sorts into a scalar, a union, or a derivation.

**Q: Doesn't a StrEnum bring back the enum the architecture removed?**

No. What is forbidden is a flat label set standing alone as a domain type, or one whose members get branched on, each of which fuses axes or relocates behavior into a label. A `StrEnum` used as the closed value space of a uniform scalar is the opposite: one structure with one meaning, the named set of values the scalar proves membership of, never switched on. The enum is the value space, as `Decimal` is in `RootModel[Decimal]`; the scalar is the domain type that travels and proves, as `gt=0` proves a bound. The moment something branches on a member, the dimensionality test has already fired and it was a union, not a scalar.

**Q: Is smart-union selection a runtime gamble I should guard against?**

No, and the drop-test that proves disjointness is strictly stronger than the discriminator it replaces: it catches every structural overlap, a superset of the duplicate-tag collisions a discriminator could ever detect. Disjointness is proven once at design time and discharged into the structure exactly as a scalar's `gt=0` is, held by construction for the life of the program, so removing the discriminator removes a duplicate, not a guard, and leaves no runtime ambiguity behind.

**Q: Won't the LLM lose its selection anchor without the discriminator?**

No, it gains one. A discriminator is a single tag field; disjoint variants carry whole distinct field sets under their own names, which is more semantic surface to index on, not less. A distinction that lives only in a tag is one model wearing a label, never a union.

**Q: How do I choose behavior by variant without a `match`?**

You don't choose; construction already selected. Each variant carries its own same-named derivation; the consumer reads it off the value. A `match` re-performs the selection the union already made.

**Q: How does the active model emit an effect that depends on which variant a union holds?**

It does not switch to choose. The effect is reified as a typed value, a frozen model describing what should happen, carried by each variant as its own same-named derivation, and the active model reads it off the selected variant and hands it to one uniform emit step. A `match` to pick the effect is the discriminator's procedural twin, banned for the reason a `match` to pick a value is: construction already selected the variant. The emitter stays uniform because it runs the single typed effect it is handed and never inspects it to choose a call, since the moment it does the dispatch has only moved inside the emitter. When the channel itself varies, the variation crosses as a domain event published uniformly, and each consuming context re-selects the variant by construction at its boundary and emits its own one uniform effect. The effect value is no new construct, it is a frozen model carried by a derivation and run at the emit step, the effect-analog of a projection.

**Q: Why not return a `bool` for a yes-or-no decision?**

Because the outcomes each carry their own payload, and `true`/`false` fuses them into one bit and loses it: the rejection's reason, the approval's terms. A decision is a union of typed result variants whose existence carries the answer, and the consumer reads the variant rather than re-deriving the lost detail from a flag.

**Q: When is a `model_validator(mode="after")` actually allowed?**

Only to assert a cross-field relation no single field carries, and only once reparameterization cannot collapse it into a field constraint and a derivation. It must only raise, never compute or route, and never re-check a field's own bound. The honesty test before one is written: name the two or more fields, say why their composition is structurally impossible rather than a threshold crossing, and name the field-level shape it replaces. A validator measuring one field against a constant is a scalar left unforged; one comparing a proven field against a configured threshold is a decision in disguise, and its home is a union of result variants, not the validator.

**Q: Why not a small function or helper to compute from a model's fields?**

Because a function reading a model's own fields is a derivation that escaped the model, its meaning living outside the structure it belongs to. It belongs on the model as a `@cached_property` returning a constructed type. A `utils.py` of such helpers is a pile of homeless derivations.

**Q: Doesn't something need to orchestrate or sequence the steps?**

No. The dependency between proven facts is the sequence: a value cannot be constructed before the values it composes, so the construction graph's edges already order the work. An orchestrator, pipeline, or step-runner restates that order by hand, a second copy that drifts. The active model drives the graph; nothing sequences above it.

**Q: Why not a base class to share the fields several models have in common?**

Because those fields are already shared, as the leaf each model references. Compose the shared scalar or model as a field. A shared base or subclass mints a structure to factor out repetition, a structure with no meaning of its own, and inheritance is not a domain relation.

**Q: Where does a live client, a socket or a database handle, live?**

On the single active model of the context, the one node exempt from immutability. Never on a boundary model, which lifts foreign data and never holds a live handle, and never as a module-level global. One live convergence point per context; a second means the context is really two.

**Q: Is a tiny mapper between foreign shape and domain acceptable?**

No. The translation is declaration: `Field(alias=...)`, nested boundary models, `model_validate_json`. A surviving mapper is escaped meaning that has not found its declaration.

**Q: Is construction that throws just a validation step?**

No. A validation step leaves a checked value still typed as unchecked. Construction leaves no unproven representation; the type is the proof, holdable only by having constructed it.

## Approved and Forbidden Constructs

The complete, closed set of constructs a TCA program is built from, one shape for each kind of meaning a domain has. Every one is a node or an edge in a single construction graph: scalars and collections are its leaves, frozen models compose them into products, unions branch over them, a derivation implies a model's facts from its own fields, the boundary model lifts foreign data in, and the active model is the one live node where the graph meets time. Typed truth leaves the graph by projection, the `model_dump` exit relation, which is a use of a frozen model and not a construct in its own right. Construction is the proof, so an illegal value cannot be built. The set is closed because the kinds of meaning are: a value on an axis, a sequence as one thing, a product, a choice among structures, a fact implied, a crossing in or out, a live edge. A construct earns its place by holding a real meaning the graph references, never by saving repetition, and whatever is not one of these is meaning escaped, duplicated, left vacuous, or fused. The converse is the discipline this catalog asks in return. Every procedure a reader reaches for, a check to enforce an invariant, a tag to carry a kind, a guard to catch a case, a switch to choose behavior, is work some construct here already does. The felt need for the procedure is not a gap in the catalog but the signal that the construct holding that meaning has not yet been found, and the move is never to add the step: it is to locate the structure that already carries it. In a structural architecture the shape does the work the procedure was reaching for.

### Root atoms (`type.py`)

#### Semantic scalar

A frozen `RootModel[P]` over a single primitive `P` (`str`, `int`, `float`, `Decimal`, `bool`, `bytes`) or a closed value space named by a `StrEnum` or `Literal`, carrying a `Field(...)` constraint or a domain-meaningful name that does real work, often both. It is a leaf of the graph: it references no other domain type. It is one shape varying along one axis, and that one-dimensionality is what separates it from a union: a scalar is a lone structure whatever its value space, open like a non-empty trimmed string or a positive amount, or a closed set like the suits of a deck, while a union is a closed set of distinct structures. A closed value space is the scalar's constraint, the same role `gt=0` plays, so a `StrEnum` wrapped as `RootModel[Suit]` names a uniform vocabulary in one place and proves membership at construction, never scattered as bare string literals and never branched on; the moment a member needs behavior a sibling lacks, the vocabulary has gained a second axis and is a union. Construction proves the constraint, so a value outside the bound or outside the closed set has no representation. It carries no behavior but its derivations. A `RootModel[str]` with neither a constraint nor a genuine name is primitive laundering, a structure with no meaning, not a scalar.

#### Forbidden Constructs

- **FORBIDDEN:** A bare primitive (`str`, `int`, `Decimal`, `bool`) standing in for a domain value, its meaning held in a variable name or a comment no reader downstream receives. -> Use Semantic scalar.
- **FORBIDDEN:** A closed vocabulary scattered as bare string literals, its value space unnamed and unproven. -> Use a Semantic scalar over a `StrEnum` value space.

### Composition (`value.py`, domain models)

#### Frozen model

A frozen `BaseModel` (`frozen=True`, `extra="forbid"`) composing already-declared types, scalars, collections, other frozen models, and unions, as fields into one proven product, carrying those fields and the derivations they imply. Its existence is the proof that every field's constraint held together, a standing certificate rather than a value someone checked. A relation no single field constrains, an ordering like `best_bid <= best_ask`, is part of that composite proof, not a guard bolted on after it. Its first home is structural: reparameterize so the relation collapses into a single-field constraint and a derivation, hold `best_bid` and a non-negative `Spread` and derive `best_ask`, and the illegal ordering has no representation. When reparameterization would distort the model, or the related fields arrive together at a boundary where a computing before-validator is barred, an asserting `mode="after"` validator that only raises is the home: it runs before the value exists, so it proves the relation rather than checking it afterward. It asserts only a relation the fields do not individually carry, and never re-checks a field's own constraint, which would be validation smuggled back in as a step. Every field is a declared type: never a bare primitive (an unforged scalar), never a bare collection of primitives (an unforged element), never a field derivable from the others (a derivation, not stored state). `extra="forbid"` closes the structure so foreign noise cannot enter. Shared fields are composed by holding a declared type as a field, never by subclassing a domain type, and the fields several models share are already shared as the leaf they each reference, so a model is minted because it is a real thing and never to factor out repetition. The value object in `value.py` and the full domain model above it are this one construct at different depths of composition, not two kinds of thing.

#### Union

A closed set of two or more frozen-model variants, each a distinct structure, and disjoint so that no value satisfies two. Distinct is not yet disjoint: distinct is different fields, disjoint is that no payload builds more than one variant, and the gap between them, variants that differ yet overlap, is where a value lands ambiguously. `extra="forbid"` is the wall, each variant rejecting another's field as foreign, but it walls only fields that are present and cannot reject one that is absent, so variants parted solely by an optional field, or by overlapping ranges on a shared field, are distinct and not disjoint. Disjointness is a structural fact the modeler proves, never a guarantee the substrate grants. Proven once, it is discharged into the structure exactly as a scalar's `gt=0` is, enforced by construction on every value for the life of the program with no residual vigilance: one property at two moments, established at design and held at construction. The variant type is the kind: a `MedicalClaim` is the medical case, never a value carrying `kind="medical"`. Construction selects structurally, building a value as the one variant whose fields it has and whose foreign fields it lacks, and raw input crosses through a frozen `RootModel[A | B | C]` envelope that lands the single matching variant. There is no stored discriminator, no tag, and no routing function: each is a second copy of the identity the structure already carries, or procedure restating what construction already does. The jobs the tag seemed to do survive without it: the disjointness test tells the variants apart, the variants' own names carry the model's salience, and only O(1) dispatch is genuinely lost, restored where a hot path of many variants demands it as a profiled local index, never as the default. The test: drop every optional field and delete every field that names the kind, then read the minimal payload that remains, the one where two variants most easily collide. If construction still lands exactly one variant, the structure is disjoint and any tag was redundant, and the union already holds. If it cannot, one of three different things is wrong, and they call for opposite moves: the variants are not actually distinct, so there is no union and the move is to collapse them into the one model they always were; or the distinction is real but its structure is missing, so the move is to add the fields that make each variant land on its own; or nothing in the program branches on the kind at all, so it was never a union but a uniform vocabulary, a Semantic scalar over a `StrEnum` value space, and stays one until a member needs behavior a sibling lacks. Behavior is read, not switched: each variant carries its own same-named derivation that a consumer reads off the selected variant, and because construction has already chosen the variant, a `match` to choose it again is the discriminator's procedural twin and is banned for the same reason.

#### Collection

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, naming a homogeneous immutable sequence that is itself a domain thing. As a plain field it is `tuple[T, ...]` on a frozen model; when the sequence is a domain thing in its own right, carrying its own constraints such as non-emptiness, order, or a bounded length, or a derivation it implies as a whole, it is the named `RootModel`. The element is always a declared type, a scalar or a model, never a bare primitive, because a collection of primitives is the element left unforged.

#### Derivation

A fact a frozen model implies from its own already-proven fields, the only behavior a frozen value has, since it cannot change, only imply. It is written `@cached_property`, or `@computed_field` over `@cached_property` when the fact must also cross the wire, or a bare `@property` for a trivial read; the choice among the three is only about caching and serialization, never about what it returns. It takes only `self` and returns a declared type, union, or proven model, never a bare `bool`, `str`, or `int` (a `bool` that gates is an unforged union, a bare primitive an unforged scalar). It composes that object from the typed fields and never flattens them into a hand-formatted string or unwraps them to primitives for presentation. A format convention is meaning escaped into a string, and typed truth becomes data only by projection. Its body is a single returned expression: no statement before the return, no nested helper, no ternary or `and`/`or` selection, no `match`, no private-method call. When the implied fact differs by which variant a union holds, each variant carries its own same-named derivation and the expression reads it off the variant, since construction already selected the variant and a `match` would only re-perform that dispatch. It is an edge, derived output from the fields it reads, and it stores nothing.

#### Forbidden Constructs

- **FORBIDDEN:** A flat label set standing alone as a domain type, or branched on to choose behavior, fusing axes or relocating meaning into a label. -> Factor by dimensionality: a uniform one-axis vocabulary is a Semantic scalar over a `StrEnum` value space; members carrying distinct structure or behavior are a Union.
- **FORBIDDEN:** A stored discriminator or `kind` tag to choose a variant, a second copy of the identity the structure already carries. -> Use Union, where the variants' disjoint structure is the selection.
- **FORBIDDEN:** A routing function, an `if`/`elif`, or a `match`/`case` over a union to choose a value or behavior, a second dispatch restating what construction already selected. -> Use variant-carried derivations: each variant implies its own fact under a shared name, read off the selected variant.
- **FORBIDDEN:** A type minted because fields recur, a shared base or a subclass to factor out fields several models share, which are already shared as the leaf each references. -> Use Frozen model composing the shared leaf as a field.
- **FORBIDDEN:** A standalone function computing from a model's fields, or a stored field derivable from the others, a derivation that escaped the model. -> Use Derivation.
- **FORBIDDEN:** A `bool` returned as a decision, an answer flattened to a single bit. -> Use Union of typed result variants.
- **FORBIDDEN:** A collection whose elements are bare primitives, the element left unforged. -> Use Collection of a declared element type.
- **FORBIDDEN:** An unfrozen model that is not the single active model of a context. -> Use Frozen model.

### Boundary and crossing

#### Boundary model

A frozen model that takes foreign-shaped data and produces domain truth in a single construction. It crosses the shape gap declaratively: `Field(alias="foreign_name")` for renames, nested declared models for nested foreign structure, `from_attributes=True` or `model_validate_json` for objects and serialized payloads. The constructed value is the proof the foreign data conformed, parse rather than validate. It lifts foreign structure into declared domain types and never retains a foreign handle as a field: no `arbitrary_types_allowed`, no `RootModel[<foreign>]`. The only procedural crossing it may hold is a `mode="before"` validator that indexes into a transport wrapper to reach the payload; a before-validator that renames or computes, or a routing `mode="after"` validator that selects a variant or transforms the shape, is procedure and is out. An asserting `mode="after"` validator that only raises to prove a cross-field invariant is part of construction, not a post-proof guard, and is allowed, under the same narrow terms as on any frozen model. The same model facing outward is the API contract, the shape allowed to cross the surface.

#### Domain event

A frozen model representing an established fact, projected to the wire by `model_dump_json` and emitted onto a transport to cross a process boundary. It is not the API contract: that contract is a boundary model replying to a caller, while a domain event is a fact announced after proof to whoever consumes it, and though both are frozen models projected out, one answers and the other announces. In process it is proven truth; on the far side it re-enters through a boundary model that proves it again. The type is the contract, so there is no request to version, no client to generate, and no mesh to make reliable. It is the construct-then-derive loop at process scale: services publish facts after proof, they do not call each other.

#### Forbidden Constructs

- **FORBIDDEN:** A mapper, adapter, translator, or DTO copying fields between a foreign shape and the domain. -> Use Boundary model.
- **FORBIDDEN:** A `json.loads` and the untyped dict it leaves behind for the program to carry. -> Use Boundary model with `model_validate_json`.
- **FORBIDDEN:** A foreign handle held as a field on a boundary model, which lifts data and never live objects. -> Use Active model for the live client.
- **FORBIDDEN:** A versioned request-and-response contract with a generated client for work between services. -> Use Domain event.

### Live edge and wiring

#### Active model

The single unfrozen `BaseModel` of a context, the one node where mutable live state converges and the graph meets time. It holds transport clients, a database, a message bus, a model client, as fields. It is exempt only from the immutability-derived rules: it may hold those clients, receive live input, reassign fields, and carry `-> None` methods that evolve state. It is bound by every other rule: its fields are declared types, no bare primitives, no `bool` gates, and it never branches on a value, no `if`/`elif`, no `match`; when behavior differs by variant it reads that variant's own derivation. A mutation method's body is a sequence, its one privilege as the node that meets time, in which each statement is a single legal operation: construct a frozen fact, assign a constructed value, read a derivation, or emit an effect, with no value-branching, no `match`, and no assembling of an untyped dict where a constructed type belongs. It receives live input, constructs frozen facts as proof, and emits effects only after proof. When which effect to emit depends on which variant a union holds, the effect is itself read off the variant: each variant carries it as a same-named derivation returning a typed effect description, a frozen model, and the one emit step runs that value uniformly, never a `match` selecting the effect. An effect whose channel varies crosses as a domain event and is re-selected by construction at the consuming boundary. There is one per context; a second unfrozen node is illegal.

#### Service

A connection shim, glue and not a value construct: a small class whose `connect` binds a transport client to the active model so the active model has its client field. It holds no domain logic, owns no domain types, and makes no domain decision; it is plumbing. When a service becomes interesting, domain meaning has escaped into it and belongs back on the active model.

#### Route

The ingress membrane at the transport edge. It imports domain-owned contracts, hands a raw request to a boundary model for construction, dispatches the constructed value to the active model, and projects the result back onto the transport. It defines no types and computes nothing; it only turns transport into typed construction and back. When a route grows interesting, meaning has escaped into the edge.

#### Config

A frozen `BaseSettings` model that constructs typed fields from the environment, so configuration is proven the moment the program starts. Each field is a declared type, never a bare primitive where a scalar belongs. The config root is constructed once, frozen, and injected.

#### Composition root

`main.py`, the single top of the wiring graph. It instantiates the concrete clients, hands them to the services, constructs the active model, and registers the routes. It is the only place wiring is assembled and holds no domain logic, no model definitions, and no computation: the imperative shell that builds the typed core and then steps back.

#### Forbidden Constructs

- **FORBIDDEN:** Domain logic, classification, or derivation inside a service, which only binds transport. -> Use Active model.
- **FORBIDDEN:** A second unfrozen model in one context, a second live convergence point. -> Use Active model, one per context.
- **FORBIDDEN:** Computation or transformation inside a route, which turns transport into a construction and back and nothing more. -> Use Active model behind the route.
- **FORBIDDEN:** An orchestrator, pipeline, or step-runner sequencing the work, when the dependency between proven facts is the sequence. -> Use Active model driving the construction graph.
- **FORBIDDEN:** An `os.environ` read or a settings dict scattered through the program. -> Use Config.
- **FORBIDDEN:** An `if`/`elif` or a `match` on a value inside the active model, a re-dispatch of what construction already selected. -> Read the selected variant's own derivation; the variant carries the behavior.
- **FORBIDDEN:** An effect emitted before proof. -> Use Active model: construct the fact, then emit.

