"""The markdown paths of each doctrine sub-context, one enum per context. A member's value is the
path its document is lifted from, relative to the `app` package (the content ships inside the wheel),
so a document is named once and read from its member through `importlib.resources`."""

from enum import StrEnum

class ConstructPath(StrEnum):
    """The path of each construct card."""

    BINDING = "domain/resource/content/construct/binding.md"
    COLLECTION = "domain/resource/content/construct/collection.md"
    COMPOSITION_ROOT = "domain/resource/content/construct/composition-root.md"
    CONCEPT_MODEL = "domain/resource/content/construct/concept-model.md"
    CONFIG = "domain/resource/content/construct/config.md"
    CONSISTENCY_MODEL = "domain/resource/content/construct/consistency-model.md"
    CONTRACT_MODEL = "domain/resource/content/construct/contract-model.md"
    DERIVATION = "domain/resource/content/construct/derivation.md"
    FOREIGN_MODEL = "domain/resource/content/construct/foreign-model.md"
    ORDERED_UNION = "domain/resource/content/construct/ordered-union.md"
    ROUTE = "domain/resource/content/construct/route.md"
    SEMANTIC_SCALAR = "domain/resource/content/construct/semantic-scalar.md"
    UNION = "domain/resource/content/construct/union.md"
    VALUE_OBJECT = "domain/resource/content/construct/value-object.md"
    VERB = "domain/resource/content/construct/verb.md"


class ReferencePath(StrEnum):
    """The path of each standalone reference document: the doctrine documents that are not construct
    or violation cards (the construct vocabulary, the program topology, the documentation strategy)."""

    JARGON = "domain/resource/content/jargon.md"
    TOPOLOGY = "domain/resource/content/topology.md"
    DOCUMENTATION = "domain/resource/content/documentation.md"


class ForbiddenPatternPath(StrEnum):
    """The path of each forbidden-pattern card, one per anti-pattern. The slug in the path matches
    the leaf of the card's `tca_forbidden_pattern_<slug>` name."""

    AFTER_VALIDATOR = "domain/resource/content/forbidden/after-validator.md"
    MODULE_LEVEL_FUNCTION = "domain/resource/content/forbidden/module-level-function.md"
    PRE_CONSTRUCTION_MUNGING = "domain/resource/content/forbidden/pre-construction-munging.md"
    NULLABLE_ABSENCE = "domain/resource/content/forbidden/nullable-absence.md"
    MUTABLE_BAG = "domain/resource/content/forbidden/mutable-bag.md"
    BARE_PRIMITIVE = "domain/resource/content/forbidden/bare-primitive.md"
    FREE_FLOATING_VOCABULARY = "domain/resource/content/forbidden/free-floating-vocabulary.md"
    ARBITRARY_TYPE_OFF_THE_EDGE = "domain/resource/content/forbidden/arbitrary-type-off-the-edge.md"
    SCALAR_NOT_PROVEN_BY_CONSTRUCTION = "domain/resource/content/forbidden/scalar-not-proven-by-construction.md"
    COLLECTION_NOT_PROVEN_BY_CONSTRUCTION = "domain/resource/content/forbidden/collection-not-proven-by-construction.md"
    OPEN_PRODUCT = "domain/resource/content/forbidden/open-product.md"
    FIELD_THE_ONTOLOGY_DID_NOT_MODEL = "domain/resource/content/forbidden/field-the-ontology-did-not-model.md"
    FROZEN_LIVE_EDGE = "domain/resource/content/forbidden/frozen-live-edge.md"
    DEAD_HANDLE = "domain/resource/content/forbidden/dead-handle.md"
    UNMODELED_BEHAVIOR = "domain/resource/content/forbidden/unmodeled-behavior.md"
    STUB_VERB = "domain/resource/content/forbidden/stub-verb.md"
    SWALLOWED_FAILURE = "domain/resource/content/forbidden/swallowed-failure.md"
    SERIALIZATION_IN_THE_DOMAIN = "domain/resource/content/forbidden/serialization-in-the-domain.md"
    BARE_ROOT_MID_GRAPH = "domain/resource/content/forbidden/bare-root-mid-graph.md"
    SURFACE_DRIFTED_FROM_THE_VERB_ROW = "domain/resource/content/forbidden/surface-drifted-from-the-verb-row.md"
    BODY_DRIFTED_FROM_THE_CHAIN = "domain/resource/content/forbidden/body-drifted-from-the-chain.md"
    MULTIPLE_CONSTRUCTIONS_IN_ONE_VERB = "domain/resource/content/forbidden/multiple-constructions-in-one-verb.md"
    VERB_ABSENT_FROM_THE_SURFACE = "domain/resource/content/forbidden/verb-absent-from-the-surface.md"
    FREE_METHOD_ON_A_FROZEN_VALUE = "domain/resource/content/forbidden/free-method-on-a-frozen-value.md"
    UNION_AS_A_CLASS = "domain/resource/content/forbidden/union-as-a-class.md"
    UNION_ALIAS_BUILT_WRONG = "domain/resource/content/forbidden/union-alias-built-wrong.md"
    UNCLAIMED_CLASS = "domain/resource/content/forbidden/unclaimed-class.md"
    UNMODELED_OR_DRIFTED_ENUM = "domain/resource/content/forbidden/unmodeled-or-drifted-enum.md"
