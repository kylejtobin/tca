# 0007. Python implements a typed interpreter, not a second business program

**Status:** binding reviewer engineering direction, 2026-10-24. Applies as outcomes 1–7 introduce compiler, evaluator, host and interfaces. Requires [0003](0003-construction-evidence-and-justified-execution.md), [0005](0005-native-construction-is-authoritative.md) and [0006](0006-evidence-ownership-and-derivation.md). [0004](0004-review-authority-and-outcome-evidence.md) owns acceptance.

## Problem and decision

Boolean uncertainty and later numerical Control ranks replaced distinct propositions with convenient Python representations. Their ordering then became business scheduling policy. Strong typing and an enum did not make that policy justified.

Model the semantic distinctions first. Use explicit typed variants for evidence, construction outcomes and protocol states, with exhaustive handling where practical. Pydantic belongs at validated declaration and data boundaries. Frozen dataclasses and typed unions are appropriate for internal graph nodes and pure results that require no additional validation boundary. This is an allocation of responsibilities, not a requirement to turn every object into a model.

Compile relationships from the declarations into shared dependency structure and evaluate concrete occurrences. A graph, its indexes and caches are derived representations of the program. Shared dependencies should be reused without collapsing distinct scopes. Cache keys must preserve the occurrence and relevant revision assumptions.

Keep evaluation deterministic and explicit about its inputs. Narrow typed interfaces, such as Python protocols, may separate capability adapters and hosts from business declarations. Async execution, retries, cancellation and resource ownership belong at execution boundaries. A coroutine represents an attempt mechanism, not a durable invocation.

## What this decision does not authorize

- An enum or numerical ordering cannot invent precedence among business decisions. It may encode a relation already justified by declarations; category membership alone supplies no causal edge.
- A static checker, cast or type-ignore is not runtime validation, provenance or permission. Keep strict checking; isolate unavoidable dynamism rather than narrowing business declarations to satisfy the checker.
- A class-only cache or traversal order cannot choose a subject, branch or effect. Repeated tree walking is not evidence that shared dependencies are evaluated as a graph.
- Model reflection cannot discard Annotated metadata, unresolved generics or other relevant native semantics. Use Pydantic's resolved model machinery and standard typing facilities; do not parse annotation strings or match class names for business meaning.
- Infrastructure cannot fill in missing business intent. No host-specific branch logic, manually authored orchestration mirror, scenario-specific engine branch or custom validation DSL substitutes for declarations.
- A new abstraction is justified by a missing semantic responsibility, not by making a patch shorter or concealing special cases.

## Engineering consequences and evidence

Concentrate reflection and version-sensitive introspection at the compiler boundary; carry typed relationships through evaluation. Catch errors at the boundary that owns their meaning. Keep business refutation, malformed construction, programming errors and infrastructure failure distinguishable.

Preserve dependency resolution and the repository's strict typing and checks. The observed baseline is Python 3.14.8 with locked Pydantic dependencies; compatibility with other versions must be exercised, not presumed. Isolate dependency-sensitive behavior without building a broad compatibility framework ahead of need.

Demonstrate that changes in model packaging do not weaken demand, that cache reuse respects scope, and that independent justified work remains concurrent. Compare optimized and unoptimized behavior where an optimization is introduced. Later compare local and durable hosts on the same declarations and evaluator. A passing type check or benchmark does not establish these semantic properties.

This record leaves module layout, internal class names and algorithm selection open. Prefer native language and library mechanisms, but judge them by the invariants they preserve. The smallest implementation that loses a required distinction is not the simplest correct architecture.

## Reference

[Python typing](https://docs.python.org/3.14/library/typing.html) describes the language's static and runtime typing facilities; annotations are not automatically runtime enforcement.
