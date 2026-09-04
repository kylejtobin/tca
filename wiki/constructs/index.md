# Constructs

The closed set of legal program shapes. All examples share one domain, venue fills, positions, and orders, and every example is correct to copy verbatim. One page per construct. Naming, construction rules, and substrate claims apply to every page.

## Pages

- [naming](./naming.md): How every structure is named for the domain thing or fact it carries.
- [construction-rules](./construction-rules.md): Construction replaces validation; the dependency graph determines order.
- [semantic-scalar](./semantic-scalar.md): A frozen RootModel over one primitive or one closed value space.
- [value-object](./value-object.md): A frozen BaseModel composing scalars into a small value with no identity.
- [concept-model](./concept-model.md): A frozen BaseModel composing declared types into one full domain thing or fact.
- [collection](./collection.md): A frozen sequence or keyed namespace that is itself a domain thing.
- [union](./union.md): A closed set of two or more frozen variants over one domain axis.
- [ordered-union](./ordered-union.md): Variants in attempt order for foreign data that carries no identity and may fail.
- [derivation](./derivation.md): A fact that is a pure function of a frozen value's already-proven fields.
- [foreign-model](./foreign-model.md): Another system's data shape, named for the other system's thing.
- [contract-model](./contract-model.md): This program's own API request or reply, composed of declared types.
- [consistency-model](./consistency-model.md): The single unfrozen BaseModel of a context, where live clients and mutable state converge.
- [verb](./verb.md): A state-transition method on the consistency model.
- [binding](./binding.md): The class whose connect method binds transport clients to the consistency model.
- [route](./route.md): The function at transport ingress: construct, dispatch, serialize.
- [config](./config.md): A frozen BaseSettings model, the only structure that reads environment values.
- [composition-root](./composition-root.md): The program entrypoint that wires config, clients, bindings, and routes.
- [substrate-claims](./substrate-claims.md): A claim about substrate behavior requires a substrate run.
