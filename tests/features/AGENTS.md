# Scenarios

Each package keeps its scenarios in `tests/features/*.feature`, one feature per concern, beside the package whose behavior they pin; this folder holds the scenarios for the repository's own tooling. A feature's header names the decision records it pins and the program its scenarios run over, as the classes of the test module that is that program, named for what they are to the framework, never for a business.

A scenario states one behavior as it was observed: the exact classes constructed, the exact `ValidationError` type, `loc` and message, the exact serialized reply. Every value in a scenario was produced by a run of the code at that revision; a scenario is evidence, not an aspiration, and a sentence that was not observed is not written.

When behavior changes, the feature is rewritten so that every scenario is true of the system as it is now, as if it had always been so. A scenario that describes a behavior that no longer exists is deleted; one that describes a changed behavior is restated; nothing is marked deprecated, pending or updated. There is no history in a feature file.

This differs from the usual behavior-driven practice, where scenarios are written first in the customer's language as a specification and the code is made to pass them. Here the page is the specification, construction is the test, and a scenario is the framework's procedure pinned in the framework's own names after a run has shown it. The feature files are not yet bound to pytest; binding them is the first item in `TODO.md`, and until then the tests beside each package are the bound form of the behaviors the scenarios state.
