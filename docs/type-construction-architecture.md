# Type Construction Architecture

## Definition

Type Construction Architecture (TCA) is a software design paradigm built on one principle: **meaning lives in the structure of the type, and construction is its proof.** A value's existence is the evidence that its constraints held, so an illegal value cannot be built. Lived to its precise form, the principle is a one-to-one correspondence between the domain's meanings and the program's structures: every meaning has exactly one structural home, and every structure carries exactly one meaning. TCA is the continuous application of that correspondence as a test, a pattern kept wherever it holds the correspondence and broken wherever it breaks it.

Carried to its conclusion, the correspondence makes the program an **executable ontology**. The domain's concepts, relations, constraints, and vocabularies are the program's types, fields, derivations, and the construction graph that joins them, not a model kept in a separate artifact the program consults. The type is the concept, the field is the relation, construction is the inference that proves a fact. There is no second copy of the meaning to hold in agreement, because the correspondence is one-to-one: a meaning that needed a second copy would be a meaning wearing two structures, and that is already the architecture failing.

The principle was already sound when type-driven design first argued it for the machine compiler, the reader that erases names and reads structure to decide what is valid. It binds harder now, because a second reader has arrived. A language model reads the names and descriptions as instructions and decides what is likely, so the same typed declaration is read by both: the structure written to prove correctness to the machine is identically what programs and bounds the model. The correspondence serves both readers at once, since one structure carrying one meaning is a single constraint to the machine and a single named instruction to the model, while a structure that carries several meanings, or a meaning smeared across several structures, dulls both readers together. For software built on a language model the executable ontology stops being good taste and becomes the substrate, because every gap between the meaning and the running program is now paid on every inference.

### The Core Test

Every programming rule faces one question: *does it hold the correspondence, or break it?* Concretely, does each meaning land in exactly one structure, and does each structure mean exactly one thing? Held correctly, a meaning is stated once, in one structure, and proven by construction; broken, it is restated by hand, duplicated, left as noise, or fused with others. This is the logical extreme of type-driven design, and it sorts the whole inherited rulebook into what TCA keeps and what it breaks.

### The Four Breaks

The correspondence is one-to-one, so the ways it can fail are counted by arithmetic, not collected by taxonomy: the mapping runs in two directions, meaning to structure and structure to meaning, and each direction fails by absence or by multiplicity. Two directions, two failures, exactly four breaks. A meaning can have **no structure**, escaped into a comment, a procedure, or a convention the type does not carry. A meaning can have **more than one structure**, a second copy kept in agreement by hand, the same fact stored in two fields, one rule restated across layers. A structure can have **no meaning**, a type minted to save repetition or a name that says nothing real, noise the graph carries that no reader can use. A structure can have **more than one meaning**, several axes of the domain fused into one field or one label set, so the type holds them all and tells none of them cleanly. Escaped, duplicated, vacuous, fused. That every forbidden pattern is one of these four is a consequence of the counting, not a claim to be trusted, and every approved structure is a shape that holds one meaning, once, and proves it by construction.

### Inherited Principles

TCA keeps the rules that build the correspondence, forcing meaning into structure and proving structure by construction.

- **Parse, don't validate.** Construction yields a value whose existence is the proof; the unproven value never moves forward. The structure is the meaning, so nothing is left to check after it.
- **Make illegal states unrepresentable.** The constraint is the edge of what the type admits, not a check run afterward, so a meaning has no illegal value to mishandle.
- **Model the domain, never the primitive.** Every domain meaning gets its own named structure that travels to every reader; a primitive with its meaning in a comment is a meaning with no structure.
- **Immutability.** A proven structure is fixed at construction, so its one meaning cannot drift out from under the proof. This holds for every model except the single consistency model, the one live node a context allows.

### Broken Rules

TCA breaks the inherited methodology that breaks the correspondence. Each entry here is a way of *working*; the code shapes the methodology produces are rejected one by one below, each beside the structure that replaces it.

- **Validation as a step.** A separate check holds the constraint while a validated-but-still-present value moves on untyped, so the meaning has escaped into the step. Construction is the check, and no unproven value survives it.
- **Functions as the unit of logic.** A function computing from a model's own fields is a derivation escaped from the model, its meaning living outside the structure it belongs to. Construction and derivation do the work.
- **Procedural layering.** The validator, mapper, and handler stack is one meaning restated across layers, duplicated and kept in agreement by hand. TCA keeps the structural separation, each layer owning a distinct construct so the meaning lives in exactly one place, and breaks the layering that copies it across them.
- **Inert naming.** Treating a rename as a no-op assumes the name carries no meaning, but the name is a structure both readers consume, so a name that says nothing is a vacuous structure and a rename is a behavioral change. Alpha equivalence never held for production types.
- **I/O barred from domain models.** I/O is real and is not banished, it is confined to where the graph meets time: the single unfrozen consistency model holds the live edge, and every frozen model holds none.

## From Meaning to Structure

The definition does not arrive with an inventory. It arrives with a test, and everything below is the test's output: each structure is what remains when one kind of meaning a domain actually has is forced into exactly one structure and proven by construction. None of it is a list to memorize or match against. It is a derivation any reader can rerun from the definition, and rerunning it is this document's standard: a structure stands here because the definition produces it, and a structure the definition cannot produce does not enter, however familiar it looks. The pull toward a familiar shape that is not here is never a gap. It is the signal that the structure carrying that meaning has not been found yet, and the move is to find it, not to add the step. In a structural architecture, the shape does the work the procedure was reaching for.

The document speaks its substrate's vocabulary on purpose. Executable ontology means the substrate's constructor is the evaluator: `RootModel`, `Field`, and the discriminator are not implementation details beneath the doctrine but the structures the obligations land on. They are stated here once and rendered as worked templates in the build patterns and skills, which derive from this document and never the reverse.

Every value can be asked exactly three questions, and the principle assigns each a home. **Is it legal?** Answered by existence: construction is the proof, so the question is settled the moment the value exists, and a check written after it is the validation step the doctrine broke. **Which case is it?** Answered by structure: identity is a meaning like any other, so it lives in a typed field, never in an inference over which fields happen to be present. **What does it imply?** Answered by derivation: a fact the value's own fields entail, written on the value, returning a constructed type. Legality by existence, identity by structure, implication by derivation. Logic that seems to fit none of the three is not a missing fourth question; it is a missing type.

### A single value: the semantic scalar (`type.py`)

A frozen `RootModel[P]` over a single primitive `P` (`str`, `int`, `float`, `Decimal`, `bool`, `bytes`, `date`) or a closed value space named by a `StrEnum` or `Literal`. It carries a `Field(...)` constraint or a domain-meaningful name that does real work, often both. It is a leaf of the graph: it references no other domain type.

A scalar is one shape varying along one axis, and that one-dimensionality is what separates it from a union. A scalar is a lone structure whatever its value space, open, like a non-empty trimmed string or a positive amount, or closed, like the suits of a deck; a union is a closed set of distinct structures. A closed value space is the scalar's constraint, the same role `gt=0` plays: a `StrEnum` wrapped as `RootModel[Suit]` names a uniform vocabulary in one place and proves membership at construction. It is never scattered as bare string literals and never branched on. The moment a member needs behavior a sibling lacks, the vocabulary has gained a second axis and is a union.

Construction proves the constraint, so a value outside the bound or outside the closed set has no representation. A scalar carries no behavior but its derivations. A `RootModel[str]` with neither a constraint nor a genuine name is primitive laundering: a structure with no meaning, not a scalar.

- **FORBIDDEN:** A bare primitive (`str`, `int`, `Decimal`, `bool`) standing in for a domain value, its meaning held in a variable name or a comment no reader downstream receives. -> Use a Semantic scalar.
- **FORBIDDEN:** A closed vocabulary scattered as bare string literals, its value space unnamed and unproven. -> Use a Semantic scalar over a `StrEnum` value space.

### A composite of values: the frozen model (`value.py`, domain models)

A frozen `BaseModel` (`frozen=True`, `extra="forbid"`) composing already-declared types (scalars, collections, other frozen models, unions) as fields into one proven product, carrying those fields and the derivations they imply. Its existence is the proof that every field's constraint held together: a standing certificate, not a value someone checked.

A relation no single field constrains, an ordering like `best_bid <= best_ask`, is part of that composite proof, never a guard bolted on after it. Its home is structural, and structural only: reparameterize so the relation collapses into a single-field constraint and a derivation, hold `best_bid` and a non-negative `Spread` and derive `best_ask`, and the illegal ordering has no representation. A reparameterization that seems to distort the model is not a license for a guard; it is the signal that the related fields are their own concept, not yet factored. There is no asserting validator: a validator that raises is a check riding inside construction, the validation step wearing the proof's clothes.

Every field is a declared type: never a bare primitive (an unforged scalar), never a bare collection of primitives (an unforged element), never a field derivable from the others (a derivation, not stored state). `extra="forbid"` closes the structure so foreign noise cannot enter. Shared fields are composed by holding a declared type as a field, never by subclassing a domain type; the fields several models share are already shared as the leaf each references, so a model is minted because it is a real thing, never to factor out repetition. The value object in `value.py` and the full domain model above it are this one construct at different depths of composition, not two kinds of thing.

- **FORBIDDEN:** A type minted because fields recur, a shared base or a subclass to factor out fields several models share, which are already shared as the leaf each references. -> Use a Frozen model composing the shared leaf as a field.
- **FORBIDDEN:** An unfrozen model that is not the single consistency model of a context. -> Use a Frozen model.

### A choice among structures: the union

A closed set of two or more frozen-model variants over one domain axis, each a distinct structure carrying its own fields. The axis's vocabulary is named once as a `StrEnum`, and each variant pins exactly one member as its typed identity: `kind: Literal[OrderEventKind.FILLED]`. A union is the structured form of a vocabulary: a uniform one-axis vocabulary is a semantic scalar over a `StrEnum` value space, and when members grow payloads or behavior a sibling lacks, the same `StrEnum` becomes the kind axis of a union and each member grows into a variant.

Variant identity is a real domain meaning, *which fact this is*, and it gets the home every meaning gets: a field of its own. Identity inferred from which fields happen to be present is meaning living between shapes rather than in one, and it is unprovable exactly where the domain is densest. Two variants with identical payloads (every reversible operation, every state-transition pair, every symmetric outcome the `bool` ban produces) differ in nothing but identity, so identity is a field or it is nowhere. The kind field copies nothing: an account number means the account number, never "this is a bank account"; a tag is a duplicate only of another tag. The duplicated break here is a second representation of the kind: a raw string beside the typed field, or the kind persisted apart from the value it identifies. The field matters most where the value travels: a fact serialized to a bus or a store and re-proven later must carry its identity in the data, because shape inference across a process boundary is identity held in the program's memory of which fields the payload had.

Behavior divides by where its meaning lives. A fact a variant implies from its own fields is the variant's: a same-named derivation on each variant, exhaustive because the checker requires every variant to define it. What a consumer does about a variant is the consumer's: a single exhaustive `match` over the narrowed union, in the consumer's own home, proven total by the checker. An `if`/`elif` chain or `isinstance` ladder over variants re-implements that dispatch without the exhaustiveness proof and is forbidden.

A decision is this construct. A yes-or-no with consequences is a two-variant union, never a `bool`: the outcomes each carry their own payload (the rejection's reason, the approval's terms), and one bit fuses them and loses both. In the graph the union is a type like any other: a field's declared type, the choice a derivation returns, the decision a consumer matches on, narrowed by the checker directly with no machinery between. What it needs when raw data must construct it is its own crossing form, the discriminated union.

- **FORBIDDEN:** A flat label set standing alone as a domain type, or branched on to choose behavior, fusing axes or relocating meaning into a label. -> Factor by dimensionality: a uniform one-axis vocabulary is a Semantic scalar over a `StrEnum` value space; members carrying distinct structure or behavior are a Union.
- **FORBIDDEN:** An untagged union selected by shape inference, the variant's identity left with no structure of its own. -> Name the axis as a `StrEnum` and pin each variant's `kind` as a `Literal` member.
- **FORBIDDEN:** A second representation of the kind, a raw string beside the typed kind field, or the kind stored apart from the value it identifies. -> The typed kind field is identity's one home.
- **FORBIDDEN:** An `if`/`elif` chain or `isinstance` ladder dispatching over union variants, the discrimination re-implemented without an exhaustiveness proof. -> Read the variant's derivation when the fact is the variant's own; one exhaustive `match` over the narrowed union when the behavior is the consumer's.
- **FORBIDDEN:** A `bool` returned as a decision, an answer flattened to a single bit. -> Use a Union of typed result variants.

### The choice meeting raw data: the discriminated union

The discriminated union is the union's constructing form: the shape the choice takes where identity-carrying data crosses into it. It is a frozen `RootModel[A | B | C]` whose root discriminates on the kind field (`root: A | B | C = Field(discriminator="kind")`). Construction proves identity and selects the variant in one O(1) step with exact per-variant errors; the checker narrows on the kind field; the model reads a named identity in the payload's own language. It is not a second kind of meaning: the choice is the union's, and the envelope is where that choice meets raw data. It stands wherever such data enters: a transport payload, a stored fact read back, a published fact re-entering through the consuming context's boundary.

Each variant's pinned kind is a defaulted `Literal`: supplied at minting, projected into every dump, present in the data wherever the fact travels, so re-proof by discriminated construction is always possible on the far side. A fact every variant implies under the same name is forwarded by the envelope in one expression (`return self.root.<name>`), so the variant-carried derivation reads the same off the envelope as off the variant. A choice that never meets raw data needs no envelope: the checker already selects in the graph, and an envelope minted there is structure without meaning. Foreign data that carries no identity at all cannot be discriminated; its crossing is the ordered union of the failure doctrine below, which mints the identity the wire lacked.

- **FORBIDDEN:** An envelope wrapped around a choice that never meets raw data, machinery minted where the checker already selects. -> Use the bare Union in the graph; the envelope stands only at the crossings.

### A choice misspelled as a field: absence

"There may be no value here" is one of the most common meanings in any domain, and `T | None` is the fused way to say it: the absence question is crushed into the field. The type says a value might be missing while saying nothing about why, so every consumer re-derives the why at the site of an `is None` check. Absence that means something is a choice, and a choice is a union: a customer with no payment method on file is not a customer whose `payment_method` is `None`; it is one of two states with names, and the state carrying no method needs no field at all. When that factoring is heavier than the domain warrants, the same move one size down is a two-variant union, but the axis must name the domain fact, what it means *here* for the thing to be absent, never presence itself. A generic `Present`/`Absent` wrapper is `Optional` in a costume, a structure whose name says nothing the `None` did not say, and it fails the test as a vacuous structure. At a boundary the rule has a complement: a foreign shape that merely omits a key is resolved at lifting, either by a default that names what omission means or by a variant when omission means a different fact, so absence never crosses into the domain as a bare `None`. An `Optional` field left on a domain model is the absence question asked of every reader forever instead of answered once in structure.

- **FORBIDDEN:** An `Optional` (`T | None`) field on a domain model, the absence question fused into the field with its why unstated. -> Factor the states: a Union over a named axis, or separate models when absence is its own state.

### A sequence as one thing: the collection

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, naming a homogeneous immutable sequence that is itself a domain thing. As a plain field it is `tuple[T, ...]` on a frozen model. When the sequence is a domain thing in its own right, carrying its own constraints such as non-emptiness, order, or a bounded length, or a derivation it implies as a whole, it is the named `RootModel`. The element is always a declared type, a scalar or a model, never a bare primitive: a collection of primitives is the element left unforged.

- **FORBIDDEN:** A collection whose elements are bare primitives, the element left unforged. -> Use a Collection of a declared element type.

### What a value implies: the derivation

A fact a frozen model implies from its own already-proven fields: the only behavior a frozen value has, since it cannot change, only imply. It is written `@cached_property`, or `@computed_field` over `@cached_property` when the fact must also cross the wire, or a bare `@property` for a trivial read; the choice among the three is only about caching and serialization, never about what it returns. It takes only `self` and returns a declared type, union, or proven model, never a bare `bool`, `str`, or `int` (a `bool` that gates is an unforged union; a bare primitive, an unforged scalar). It composes its result from the typed fields and never flattens them into a hand-formatted string or unwraps them to primitives for presentation: a format convention is meaning escaped into a string, and typed truth becomes data only by projection. Its body is a single returned expression: no statement before the return, no nested helper, no ternary or `and`/`or` selection, no `match`, no private-method call. When the implied fact differs by which variant a union holds, the fact is each variant's own meaning: each variant carries its own same-named derivation and the envelope's expression forwards to the selected variant, so the dispatch lives in the structure and the checker forces the set exhaustive. A `match` inside a derivation body is a consumer's dispatch smuggled into a value's fact; the consumer's `match` belongs in the consumer. A derivation is an edge, derived output from the fields it reads, and it stores nothing.

A question with a free variable seems to demand what no derivation provides, and that felt need is the signal, not a gap: the question is itself a composite fact. Compose the free variable and the value it interrogates as the two fields of a frozen query model, and the answer is that model's derivation, taking only `self`, one expression, returning a constructed type. Every parameterized helper a builder reaches for is a query model not yet named.

- **FORBIDDEN:** A standalone function computing from a model's fields, or a stored field derivable from the others, a derivation that escaped the model. -> Use a Derivation.

### A mapping with a key: the association

"Price by product" is a real kind of meaning, the association, and the dict field is its escaped form: an untyped mapping whose key semantics, uniqueness rule, and miss behavior all live in the consumer's head. Each association is itself a fact with a name (a quotation, an assignment, an enrollment), so it is a frozen entry model composing the key and the value as declared types. The set of associations is a collection of those entries. Lookup is a query model: the key composed with the collection, the answer its derivation, returning a choice, found carrying the entry or missing carrying the key, so the miss is a constructed variant the consumer must handle rather than a `KeyError` escaping at runtime. Whether a key repeats is itself a question with an answer, and it gets the home every question gets: a query model whose derivation reads the multiplicity off the entries and returns a typed fact the consumer reacts to, never a guard that refuses after the fields already held. Everything the dict promised is still there, the key semantics in the entry's field names, the lookup and its miss in the query model's result union, each meaning in one home instead of none.

- **FORBIDDEN:** A `dict` field carrying an association, its key semantics and miss behavior unstated. -> A frozen entry model, a Collection of entries, and a query model whose derivation returns a found-or-not union.

### The crossing in: the boundary model

A frozen model that takes foreign-shaped data and produces domain truth in a single construction. It crosses the shape gap declaratively: `Field(alias="foreign_name")` for renames, nested declared models for nested foreign structure, `from_attributes=True` or `model_validate_json` for objects and serialized payloads. The constructed value is the proof the foreign data conformed: parse, don't validate. A foreign key that may be omitted is resolved here, at lifting, per the absence doctrine: a default that names what omission means, or a variant when omission means a different fact, so a bare `None` never crosses into the domain. It lifts foreign structure into declared domain types and never retains a foreign handle as a field: no `arbitrary_types_allowed`, no `RootModel[<foreign>]`. The only procedural crossing it may hold is a `mode="before"` validator that indexes into a transport wrapper to reach the payload; a before-validator that renames or computes, and any `mode="after"` validator whatsoever, routing or asserting, is procedure and is out. The same model facing outward is the API contract, the shape allowed to cross the surface.

- **FORBIDDEN:** A mapper, adapter, translator, or DTO copying fields between a foreign shape and the domain. -> Use a Boundary model.
- **FORBIDDEN:** A `json.loads` and the untyped dict it leaves behind for the program to carry. -> Use a Boundary model with `model_validate_json`.
- **FORBIDDEN:** A foreign handle held as a field on a boundary model, which lifts data and never live objects. -> Use the Consistency model for the live client.

### What failure is

There are two kinds of failure, and they could not be more different. The **proof's refusal** is construction throwing: no value exists, nothing was proven, and the refusal is not a domain meaning, so it is never modeled and never converted into a value. A `try`/`except` that catches a refusal and substitutes a default, a flag, or a partially-filled object manufactures exactly the unproven value the architecture exists to make unrepresentable. The refusal propagates, with the substrate's per-variant errors as its diagnostic, and the program does not continue past it. The **domain's negative outcome** is the opposite in every respect: a rejection with its reason, a request that was denied, an operation that did not take, each a fact the domain itself asserts. A negative outcome is a meaning, so it is a union variant, constructed and proven like any other fact, and the consumer reads it rather than re-deriving it from a flag. The test is one question: did the domain say no, or did the proof fail?

When a crossing is *expected* to fail sometimes (a stream that sometimes carries garbage, an import of legacy records that sometimes do not conform), the failure has become a domain case with a constructible home. The crossing's result is a union whose last variant is the failure, composed from the payload itself, the one fact that cannot fail to exist. The union is ordered (`union_mode="left_to_right"`): the stronger construction is attempted first and the failure variant catches what refuses it, so the conversion from refusal to fact is declared, never caught. Ordered selection is legal exactly here and nowhere else, because foreign data carries no identity to discriminate on. Each lifted variant pins its kind as a defaulted `Literal`, so identity exists from the first moment the domain holds the value; everywhere the value travels after that, the discriminated union rules. Refusal is then reserved for what is genuinely exceptional, which is what it was for all along.

There is a third arrival, and the test sorts it without a new structure. A foreign client may speak its negative outcome in refusal's vocabulary: it raises where it means no, or hands back a marker where it means a boundary fact. The domain said no, in an idiom the program does not own, and both of the wire's shapes are known, because a declared client answers in declared types and raises declared signals. Known foreign shapes get what known foreign shapes always get: a boundary model each, riding the ordered union exactly as above. The answering shape is attempted first and lifts its payload declaratively; fed the signal instead, it refuses, and the refusal falls through to the no-variant, which composes from its pinned identity. Construction is the router and the shapes are the parser: no function inspects the reply to decide its case. What Python will not do is hand a raise to a constructor, so the verb owns the capture, three lines and nothing more: the call assigned, each declared signal reassigned as the arrived value, the crossing constructed from whatever arrived. The capture converts nothing, decides nothing, defaults nothing; it makes the raise a value, once, narrowly, and an undeclared raise propagates as the refusal it is. We do not raise outcomes; we refuse proofs.

- **FORBIDDEN:** A `try`/`except` that converts a construction refusal into a default, a flag, or a partial object, manufacturing the unproven value construction refused to make. -> Let the refusal propagate; when failure is a domain case the program reacts to, the crossing's result is an ordered Union whose last variant composes the failure from the payload itself.
- **FORBIDDEN:** A foreign reply parsed by hand: a function inspecting the reply to decide its case, a handler layer, or a catch arm constructing the domain's answer inline. -> Model both wire shapes; the ordered Union selects by construction, and the capture only makes the raise a value.
- **FORBIDDEN:** A capture that does more than capture: a broad `except`, a caught `ValidationError`, a substituted default, a second statement in an arm. -> The capture is three lines; everything undeclared propagates.

### The crossing out: projection

Typed truth leaves the graph by projection: `model_dump` and `model_dump_json`, the exit relation. Projection is a use of a frozen model, not a structure of its own: the fact is the frozen model, leaving is projection, and announcing it to another process adds nothing structural. The consistency model projects the proven fact onto a transport; on the far side it is foreign data again, re-entering through that context's own boundary model and re-proven by discriminated construction, because its kind traveled in the data. The type is the contract, so there is no request to version, no client to generate, and no mesh to make reliable: contexts publish facts after proof, they do not call each other. The published fact is not the API contract: the contract is a boundary model replying to a caller, while a published fact is announced to whoever consumes it. One answers, the other announces, and both are frozen models projected out.

- **FORBIDDEN:** A versioned request-and-response contract with a generated client for work between services. -> Project the proven fact onto the transport and re-prove it through a Boundary model at the consuming edge.

### The present: the consistency model

The context's present is a domain meaning like any other, and the consistency model is its one structural home: the single unfrozen `BaseModel` of a context, the one node where mutable live state converges and the graph meets time. Its obligation is its name: every state it holds is a proven fact, held consistent through change. Every frozen value is timeless, and the program's one relation to *now* is this node, so state evolution is the present re-pointing from one proven fact to a newer one, reassignment of proofs, never mutation of their contents, and even the one mutable node never holds an unproven value. It holds transport clients (a database, a message bus, a model client) as fields, because the live edge is part of the present.

It is exempt only from the immutability-derived rules: it may hold those clients, receive live input, reassign fields, and carry `-> None` methods that evolve state. It is bound by every other rule: its fields are declared types, no bare primitives, no `bool` gates, and it never branches on a bare value: no `if`/`elif`, no `isinstance`. The one dispatch it owns is a single exhaustive `match` over a union's narrowed root, proven total by the checker, because what to do about a variant is the consumer's meaning and the consistency model is the consumer. A mutation method's body is a sequence, its one privilege as the node that meets time, in which each statement is a single legal operation: construct a frozen fact, assign a constructed value, read a derivation, emit an effect, capture a foreign reply (the licensed three lines: one call assigned, each declared signal reassigned as the arrived value, feeding a crossing's construction and nothing else), or `match` exhaustively on a narrowed union with each arm a sequence of these same operations, and no assembling of an untyped dict where a constructed type belongs. It receives live input, constructs frozen facts as proof, and emits effects only after proof. A variant's own facts (the payload an outcome carries, content derived from its fields) stay on the variant as derivations and are read off the arm. An effect whose channel varies crosses as a projected fact and is re-selected by discriminated construction at the consuming boundary. There is one per context; a second unfrozen node is illegal.

A verb is the unit of the obligation: a transition from one proven state to the next. Its body is the expansion of its declared chain, what it consumes, constructs, emits, returns, or yields, and statement order is the construction graph's dependency order, determined by the chain, never chosen by the writer. The consistency model consumes proven declarations and emits proven objects, and the body is the path between them the graph already determines. A verb that constructs nothing, emits nothing, and yields nothing declares no transition, and the grammar refuses the row.

A verb that yields is the present extended over time. It yields proven facts one per fact, each constructed before it is emitted, and is otherwise bound by every rule a returning verb is bound by.

### The bindings: service and route

The typed core homes the domain's meanings; the service and the route are the licensed exceptions, structures whose entire meaning is the binding they perform. The moment one carries more, meaning has escaped into the shell.

A **service** is a connection shim, glue and not a value construct: a small class whose `connect` binds a transport client to the consistency model so the consistency model has its client field. It holds no domain logic, owns no domain types, and makes no domain decision. When a service becomes interesting, domain meaning has escaped into it and belongs back on the consistency model.

A **route** is the ingress membrane at the transport edge. It imports domain-owned contracts, hands a raw request to a boundary model for construction, dispatches the constructed value to the consistency model, and projects the result back onto the transport. It defines no types and computes nothing. When a route grows interesting, meaning has escaped into the edge.

### The environment: config

A frozen `BaseSettings` model that constructs typed fields from the environment, so configuration is proven the moment the program starts. Each field is a declared type, never a bare primitive where a scalar belongs. The config root is constructed once, frozen, and injected.

### The top: the composition root

`main.py`, the single top of the wiring graph. It instantiates the concrete clients, hands them to the services, constructs the consistency model, and registers the routes. It is the only place wiring is assembled, and it holds no domain logic, no model definitions, and no computation: the imperative shell that builds the typed core and then steps back.

- **FORBIDDEN:** Domain logic, classification, or derivation inside a service, which only binds transport. -> Use the Consistency model.
- **FORBIDDEN:** A second unfrozen model in one context, a second live convergence point. -> Use the Consistency model, one per context.
- **FORBIDDEN:** Computation or transformation inside a route, which turns transport into a construction and back and nothing more. -> Use the Consistency model behind the route.
- **FORBIDDEN:** An orchestrator, pipeline, or step-runner sequencing the work, when the dependency between proven facts is the sequence. -> Use the Consistency model driving the construction graph.
- **FORBIDDEN:** An `os.environ` read or a settings dict scattered through the program. -> Use Config.
- **FORBIDDEN:** An `if`/`elif` chain or `isinstance` ladder inside the consistency model, or branching on anything that is not a union's narrowed root. -> One exhaustive `match` over the narrowed root for consumer behavior; the variant's own derivation for the variant's own facts; a missing type for everything else.
- **FORBIDDEN:** An effect emitted before proof. -> Use the Consistency model: construct the fact, then emit.
- **FORBIDDEN:** A stub body (`raise NotImplementedError`, a bare `...`, a `pass`) standing where a declared chain belongs, a surface declared but not built. -> Expand the declared chain; a verb with no chain to expand is a model not finished declaring.

## Frequently Asked Questions

Each question below is an objection in the builder's own voice, the exact form the pull toward procedure takes in the middle of a build. They are answered here, once, so they are not negotiated in the moment: an objection that arises mid-build and matches one of these is already settled, and continuing to argue it is not reasoning, it is the corpus buying time. An objection that is genuinely new is settled the same way these were: by derivation from the definition or by a run of the substrate, never by what feels pragmatic on the current token.

**Q: "I'm not sure we can trust Pydantic here, so I'll add a check to be safe."**

**A:** The check un-proves the value it guards. The substrate is the execution model, not a dependency to hedge against; doubting construction while running on it is doubting the interpreter's arithmetic and adding an `if` after every addition. Uncertainty about what construction does is settled by a ten-line run. Run it.

**Q: "These are just type declarations; nothing here actually does anything. Where does the work happen?"**

**A:** Inside the constructor. One `model_validate` at the root fires the entire tree: every field coerced, every nested model constructed, every union discriminated, every constraint proven, one call. Code written beside the types to "do the work" restates work the machine is already doing.

**Q: "The plan models this as types, but for this piece a procedural approach is more pragmatic."**

**A:** "Pragmatic" is the corpus speaking. The plan derives from the principle; the pull toward procedure derives from a corpus that is overwhelmingly procedural and generates fluent justification on demand, which is why it feels like reasoning. Fluency is not construction. The plan falls only to a derivation or a substrate run.

**Q: "I'll get it working procedurally first and type it properly later."**

**A:** There is no later. The procedural draft is a different program whose meanings live in steps, and the refactor inherits the steps. Model first; the program is what falls out of the model.

**Q: "This logic doesn't feel like it belongs on a model; a helper function would be cleaner."**

**A:** The feeling is the training distribution, not the domain. A fact computed from a model's own fields is that model's derivation. A question with a free variable is a query model. There is no third place; a utils file is a pile of homeless meanings.

**Q: "Models are data; behavior belongs in a service layer."**

**A:** The model is not a container for the concept; it is the concept. A frozen value's behavior is what it implies, and implication lives on the value as derivation. A service that gets interesting is a model's meaning escaped.

**Q: "It really is just yes or no; a `bool` is the honest type."**

**A:** One bit fuses both outcomes and drops both payloads: the rejection's reason, the approval's terms. A yes-or-no with consequences is a two-variant union whose existence carries the answer. If truly nothing reacts and nothing is carried, there was no decision to model.

**Q: "The kind field is redundant; the variant's fields already tell you which case it is."**

**A:** Correlation is not copy. A routing number means the routing number, never "this is a bank account." Shape inference cannot prove identity exactly where domains are densest: variants with identical payloads. Identity is a field or it is nowhere.

**Q: "An `isinstance` check is more direct than restructuring into a `match`."**

**A:** It is the same dispatch with the proof deleted. The exhaustive `match` fails the build at every consumer when next month's variant lands. The `isinstance` ladder compiles forever and misses it silently.

**Q: "`T | None` is the natural way to say the value might be missing."**

**A:** `None` refuses to say why, so every consumer re-derives the why at an `is None` check, forever. Absence that means something is a choice with a name: a union over an axis that says what absence means here, or a model that does not carry the field at all.

**Q: "A dict keyed by id is the obvious shape for this mapping."**

**A:** Obvious and untyped are the same property here. The dict holds every meaning in the consumer's head: what the key is, what a miss means, whether keys repeat. The entry model's fields, the query model's found-or-missing union, and the multiplicity query's typed answer state all three in structure.

**Q: "I should catch the `ValidationError` so the program degrades gracefully."**

**A:** Did the domain say no, or did the proof fail? Domain-no is a variant, constructed and handled like any fact. Proof-failure means nothing was proven, and catching it manufactures the unproven value the architecture exists to forbid. Expected failure is a domain case the ordered union constructs declaratively. Graceful is structural, never caught.

**Q: "The client raises when it means no; I'll catch it and convert it to the right variant."**

**A:** Catch it and feed it, never convert it. Both of the wire's shapes are known, so both are modeled, and the ordered union selects by construction: the answering shape refuses the signal, and the no-variant catches what refuses. The `except` is capture, not conversion: it makes the raise a value and nothing else. The moment an arm computes, names a variant, or defaults, the parser you refused to model is back, wearing an except clause.

**Q: "I can't construct the whole object yet, so I'll build it partial and fill it in."**

**A:** A partial object is an unproven value with a long lifetime. A value that cannot be constructed yet is a different meaning wearing the finished value's name: the facts in hand are their own complete model, proven now, and the full fact constructs the moment its inputs exist.

**Q: "I need a loop to build this collection up."**

**A:** Accumulation is construction in disguise, the unproven intermediate exposed at every iteration. The collection is constructed whole, one expression producing the tuple the `RootModel` proves. Work the elements need is each element's own construction.

**Q: "A validator can compute and normalize this field."**

**A:** A validator that computes is procedure inside the proof; a validator that "only asserts" is the same procedure wearing the proof's clothes. Derivable values are derivations, never stored. Foreign reshaping is the boundary's declarative crossing. A cross-field relation reparameterizes into single-field constraints and derivations. Computing a stored value in a validator hides the duplicated break inside construction.

**Q: "This invariant spans two fields; an asserting after-validator is the only way to prove it."**

**A:** No relation needs one. Hold one bound and the constrained difference, derive the other, and the illegal pair has no representation. A relation that resists that factoring is two fields belonging to a concept nobody named yet: name it. "It spans two fields" is every check's excuse for existing. Reparameterize or factor. There is no third home.

**Q: "Something has to orchestrate these steps in the right order."**

**A:** The order already exists. A value cannot construct before the values it composes; the graph's edges are the sequence. An orchestrator is a second copy of that order, kept by hand, drifting. The consistency model drives the graph; nothing sequences above it.

**Q: "This is over-engineering; that's a lot of classes for what a few lines could do."**

**A:** Count meanings, not lines. Every class is a meaning the few lines also contain, escaped into steps and conventions. The procedural version is not smaller; it is the same ontology with its structure deleted, and both readers pay it back on every read.

**Q: "I'll stub the verbs now and implement the bodies later."**

**A:** There is no later. A stub is an unproven program wearing a finished surface. The body is the expansion of the verb's declared chain, and a verb whose chain cannot be declared yet is a model that is not finished, not a body to defer.
