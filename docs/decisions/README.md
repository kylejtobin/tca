# Decision authority and scope

Only Kyle's designated independent Codex reviewer edits this directory. Read applicable decisions together; none grants an implicit exception to another. These are requirements for implementation and review, not claims that the implementation already meets them.

| Record | Status | Decision it governs |
| --- | --- | --- |
| [0001](0001-durable-program-contract.md) | Historical experiment; resolution claims withdrawn | Original contract experiments, not acceptance authority |
| [0002](0002-demand-admission-and-occurrence.md) | Historical experiment; demand rule rejected | Earlier attempted repairs and their limits |
| [0003](0003-construction-evidence-and-justified-execution.md) | Binding | Architectural laws, justification and required reasoning |
| [0004](0004-review-authority-and-outcome-evidence.md) | Binding | Reviewer authority, contract integrity and outcome evidence |
| [0005](0005-native-construction-is-authoritative.md) | Binding | Pydantic's authoritative value construction and bounded inference |
| [0006](0006-evidence-ownership-and-derivation.md) | Binding | Historical evidence, constructed results, occurrence identity and replay |
| [0007](0007-python-interpreter-engineering.md) | Binding | Python representations, compilation, evaluation and execution boundaries |

The foundations define the product architecture; TODO defines the outcome sequence. These records constrain how those outcomes are achieved. Unresolved choices are not permission to weaken an established obligation, and they do not require unrelated future outcomes to be completed early.

For example, 0005 establishes whether a value constructs; 0003 establishes whether an effect is justified; 0006 establishes what evidence and identity that construction retains. None of those answers supplies the other two. 0007 governs their implementation; 0004 prevents tests or descriptions from changing the obligations to fit that implementation.

Implementers work in code and executable declarations. They provide proposals and evidence when a contract choice is needed; they do not edit records, invert required regression behavior or self-accept outcomes. No new planning document is required merely to use this index.
