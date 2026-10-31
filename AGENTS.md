# AGENTS.md

TCA is a declarative, event-driven application framework. Developers name,
specialize, and compose typed constructs with defined semantics. Their
relationships determine native execution and organize its explanations.
Framework constructs follow the same modeling discipline as applications.

## Establish the intended result

Read the complete [product definition](docs/product.md) and
[architecture](docs/architecture/DESIGN.md), then the assigned outcome,
relevant decisions, previous corrections, and actual code.

Establish what developers author, what selected constructs already supply,
and what remains to be implemented. Reassess earlier instructions and
existing machinery against that meaning; preserve demonstrated improvements.

## Derive the implementation

For each component, identify the declaration expressing its meaning, the
native facility realizing it, and the remaining obligation requiring custom
code. Establish necessity before evaluating implementation correctness.

Pydantic constructs values. Pydantic Settings constructs configuration.
FastStream provides typed receiving, invocation, publishing, and resource
lifecycle. NATS/JetStream supplies routing, retained history, and delivery.
TCA derives their bindings from modeled relationships.

Types define contracts, names identify placements, and composition establishes
relationships. Derive what these already determine; declare additional meaning
only where needed. Application choices remain explicit; supplied execution
semantics require no second workflow or independently maintained topology.

## Implement and verify the complete relationship

Preserve the permitted vocabulary through composition. Resolve implementation
limitations without silently narrowing declarations or weakening requirements.
Verify uncertain native mechanics against pinned versions.

Trace declarations through receiving, construction, authority, publication,
interruption, and subsequent observations. Inspect producers and consumers
together. Keep validity, authority, identity, provenance, outcome knowledge,
and permission distinct; failed judgments preserve independently established facts.

Use strict typing and focused tests with independently derived expectations.
Verify TCA-specific composition through real native integrations. Pair prevented
behavior with legitimate progress, and correct the governing model across
affected paths rather than patching only the example.

## Authority and reporting

Proceed with routine implementation. Resolve concrete conflicts with evidence
and reviewer involvement; requirement changes need Kyle's authorization.

Report the commit, executed checks, demonstrated behavior, failures, and
verification limits. Distinguish inspection, isolated experiments, and integrated
execution. The designated reviewer grants acceptance.

## Repository checks

Use the existing recipes:

- `just check`: lint, formatting, strict typing, security checks and tests.
- `just audit`: lockfile, dependency audit, code scanning and image pins.
- `just build`: development image.
- `just lock`: lockfile regeneration.
- `just shell`: development shell.

Targeted tests may use `uv run pytest <test-path> -q`. Run git, just, uv and
docker as bare commands. Follow [.gitmessage](.gitmessage) for commit, PR,
and squash messages. Do not add routine documentation approval steps.
