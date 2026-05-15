# Structural Discovery

Bottom-up discovery for projects where the artifact itself carries structural information. Code, infrastructure, schemas, data models, configuration systems. The structure tells you what the project's commitments are if you know what to listen for.

This reference teaches what signals mean. It does not instruct autonomous analysis. Read code when the user points you at it. Form hypotheses for the user to confirm or correct.

## Import Direction Reveals Authority Topology

Imports flow toward authority. If module A imports from module B but B never imports from A, B is closer to the authority root. Map the direction of imports across the major module boundaries the user identifies. The module that everything imports from and that imports from nothing external is the authority root.

When the user names a module, ask: what does this import? What imports from it? The answers sketch the authority topology without scanning the whole tree.

## Dependencies Reveal Ownership

If two modules both depend on a third, that third module owns truth they share. If a concept is defined in one place and imported everywhere, the place of definition owns it. If a concept is defined in multiple places, ownership is ambiguous and probably a gate candidate.

Duplication is a signal. When the same idea appears in two modules, ask the user: which one is authoritative? The answer reveals an ownership boundary.

## Type Signatures Reveal Variation Expression

Where the project uses union types, discriminated unions, generics, or type parameters, the project is expressing structural variation. These are places where the adjudication system needs to understand what shapes are allowed.

When the user discusses a polymorphic boundary, look at how variation is expressed. Is it declared in the type system or routed by external procedure? Declared variation is structural. Externally routed variation is often a gate candidate for disallowed evidence.

## Module Boundaries Are Ownership Claims

A module boundary is a claim: everything inside this boundary is one concern. When the user names their module structure, each boundary is a hypothesis about ownership. Test it: is there anything inside this module that belongs to a different concern? Is there anything outside that belongs inside?

Cross-boundary imports that seem unnecessary are signals that ownership is misaligned. These are often the source of evidence shapes: "concept X placed in module Y because the current caller lives there rather than because Y owns X."

## Existing Linter Rules Are Acknowledged Invariants

If the project already has linter rules, those are invariants the team has already identified and formalized. They are prior art. Review them with the user. Some may map directly to fast-fail patterns. Some may reveal the team's intuitions about quality dimensions that haven't been formalized into gates yet.

Ask: which of these rules catch things that are always wrong? Which catch things that are sometimes wrong depending on context? The first set are invariant candidates. The second set are gate candidates.

## CI Checks Are Prior Art on Fast-Fails

Existing CI checks (test suites, build validations, security scans, format checks) are things the team has already decided must pass before work lands. They reveal what the team considers structurally non-negotiable. Some may overlap with or inform invariant candidates.

## Code Review History Reveals Unstated Gates

If the project has accessible code review history, recurring review comments reveal quality dimensions the team enforces through taste because they haven't been formalized. "We always push back on X" is an unstated gate. The same objection raised by different reviewers at different times on different code is strong evidence of a shared but unwritten quality criterion.

Ask the user: what do you always catch in review? What do you always push back on? What's the feedback that gets repeated? These are gate candidates. The evidence shapes are the specific things reviewers flag. The approved mechanisms are what reviewers suggest instead.