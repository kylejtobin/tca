# Principles

These principles are not style preferences. They are the disciplines that fall out of taking construction as proof seriously. They reinforce one another: structural shape makes proof precise, ownership keeps semantics in the right place, naming makes surfaces executable, and development discipline keeps procedure from sneaking back in.

---

## Structural Discipline

**Types at the entry.** Types constrain computation from the start. Raw data enters a construction machine at the boundary and emerges as proven objects. There is no untyped staging area.

**Focused types.** Each type represents one coherent domain concept in one context. A customer as-analyzed is a different type from a customer as-indexed. Fields that belong together in every context share a type. Fields that don't, don't.

**Domain-typed fields.** Every field carries domain meaning through its type. Closed vocabularies are enums. Bounded values are constrained types. Structured formats are pattern-validated. A bare primitive must justify why it has no domain type.

Types compose through composition (field annotations require the child to construct before the parent), inheritance (a child's machine includes the parent's fields, validators, and projections), and structural matching (`from_attributes` reads any object whose attributes match field names). The choice follows from the domain: does this type contain another, share construction with another, or read another's surface?

---

## Program Ownership

**The context owns the program.** The domain context model is where construction, derivation, and program semantics live. Service layers wire plumbing. API layers expose projections. Neither contains domain logic. If domain logic lives outside the types, it is in the wrong place.

**Intrinsic derivation belongs on the machine.** A derivation is intrinsic when it depends only on the object's own proven fields. Intrinsic derivations are projections — they belong on the machine. If calling code computes one externally, that is a wiring defect.

**Contextual derivation stays external.** A derivation is contextual when it depends on external state: user locale, request time, feature flags, another model's fields. Contextual derivations do not belong on the type. They are computations in a larger environment. Forcing them onto the machine creates god models with ambient context leaks.

**Route contracts belong to the context.** Request types, response projections, and error envelopes are domain knowledge. They belong in the context that understands them, not in the route handler.

---

## Development Discipline

**Shapes first.** Define the types before writing any procedural code. The types are the specification. If you cannot express the domain as types, you do not yet understand the domain. Development proceeds: domain types, then vocabularies (enums), then the thinnest possible plumbing.

**Validators exist only at irreducible boundaries.** If you are reaching for a validator, ask first: can a better shape solve it? An intermediate model, a smarter alias, a constrained type, or a discriminated union almost always can. Validators exist only for cross-field constraints that types cannot express, or for translation seams where foreign structure must be reshaped. See [Irreducible Seams](irreducible-seams.md).

---

## Naming And Semantic Precision

**Field names are the interface between domain knowledge and computation.** Use domain vocabulary, not programmer vocabulary: `churn_risk_tier`, not `risk_level`. Disambiguate with docstrings: if two terms could be confused, the docstring resolves it. Enum members are a closed vocabulary, and each member carries meaning. Treat renames as you would changing a function's logic, because that is what they are.

**When the consumer is a language model, names are part of the computation.** Field names, descriptions, and enum labels become executable guidance for neural consumers. The structural channel bounds what can be output; the semantic channel guides which valid output becomes likely. Every TCA principle that tightens the type simultaneously tightens the information bound on the LLM. See [Semantic Index Types](semantic-index-types.md).

---

## Progressive Hardening

Start with the clearest model and the most precise language you can justify: field names, docstrings, focused types. Observe where soft compliance is insufficient — where consumers (human or LLM) produce wrong or ambiguous results. Promote those specific contracts to structural guarantees: tighter types, constrained primitives, enums, discriminated unions.

The construction pipeline grows by observation, not by speculation. Do not over-constrain prematurely. The discipline is empirical: watch what fails, then harden that specific boundary.

---

## Translation Minimization

Every layer between domain knowledge and executable code is a source of information loss. In TCA, the domain expert names the fields, the docstrings are the specification, the construction pipeline is the logic, and construction is validation. The number of translation steps between "what the domain means" and "what the code does" is the primary metric of architectural quality.

TCA drives it toward one.
