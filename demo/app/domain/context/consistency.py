"""The consistency model: the single unfrozen node of the context, where live clients
and mutable state converge. Verbs are its only methods, each a transition that
constructs the next proven fact and re-points a field to it. Every other domain
structure is frozen. A build overwrites this file.
(docs/construct.md: consistency model, verb)"""
