"""Every doctrine document, each lifted whole into its own named constant under its group: a
`tca_authorized_construct_*` per construct card, a `tca_required_reference_*` per standalone
reference, a `tca_forbidden_pattern_*` per forbidden-pattern card. Each constant's name is the
document's `name`, the tool name it is served under, and the same string in all three places. A
document is named once here by constructing it from its path: the construction is the proof its file's
format held. The named documents are gathered into one frozen `DocumentCollection`, the doctrine
corpus the program serves."""

from pydantic import Field, RootModel

from app.domain.resource.document import Document
from app.domain.resource.type import ConstructPath, ForbiddenPatternPath, ReferencePath

tca_authorized_construct_binding = Document.model_validate_context(ConstructPath.BINDING)
tca_authorized_construct_collection = Document.model_validate_context(ConstructPath.COLLECTION)
tca_authorized_construct_composition_root = Document.model_validate_context(ConstructPath.COMPOSITION_ROOT)
tca_authorized_construct_concept_model = Document.model_validate_context(ConstructPath.CONCEPT_MODEL)
tca_authorized_construct_config = Document.model_validate_context(ConstructPath.CONFIG)
tca_authorized_construct_consistency_model = Document.model_validate_context(ConstructPath.CONSISTENCY_MODEL)
tca_authorized_construct_contract_model = Document.model_validate_context(ConstructPath.CONTRACT_MODEL)
tca_authorized_construct_derivation = Document.model_validate_context(ConstructPath.DERIVATION)
tca_authorized_construct_foreign_model = Document.model_validate_context(ConstructPath.FOREIGN_MODEL)
tca_authorized_construct_ordered_union = Document.model_validate_context(ConstructPath.ORDERED_UNION)
tca_authorized_construct_route = Document.model_validate_context(ConstructPath.ROUTE)
tca_authorized_construct_semantic_scalar = Document.model_validate_context(ConstructPath.SEMANTIC_SCALAR)
tca_authorized_construct_union = Document.model_validate_context(ConstructPath.UNION)
tca_authorized_construct_value_object = Document.model_validate_context(ConstructPath.VALUE_OBJECT)
tca_authorized_construct_verb = Document.model_validate_context(ConstructPath.VERB)

tca_required_reference_jargon = Document.model_validate_context(ReferencePath.JARGON)
tca_required_reference_topology = Document.model_validate_context(ReferencePath.TOPOLOGY)
tca_required_reference_documentation = Document.model_validate_context(ReferencePath.DOCUMENTATION)

tca_forbidden_pattern_after_validator = Document.model_validate_context(ForbiddenPatternPath.AFTER_VALIDATOR)
tca_forbidden_pattern_module_level_function = Document.model_validate_context(ForbiddenPatternPath.MODULE_LEVEL_FUNCTION)
tca_forbidden_pattern_pre_construction_munging = Document.model_validate_context(ForbiddenPatternPath.PRE_CONSTRUCTION_MUNGING)
tca_forbidden_pattern_nullable_absence = Document.model_validate_context(ForbiddenPatternPath.NULLABLE_ABSENCE)
tca_forbidden_pattern_mutable_bag = Document.model_validate_context(ForbiddenPatternPath.MUTABLE_BAG)
tca_forbidden_pattern_bare_primitive = Document.model_validate_context(ForbiddenPatternPath.BARE_PRIMITIVE)
tca_forbidden_pattern_free_floating_vocabulary = Document.model_validate_context(ForbiddenPatternPath.FREE_FLOATING_VOCABULARY)
tca_forbidden_pattern_arbitrary_type_off_the_edge = Document.model_validate_context(ForbiddenPatternPath.ARBITRARY_TYPE_OFF_THE_EDGE)
tca_forbidden_pattern_scalar_not_proven_by_construction = Document.model_validate_context(ForbiddenPatternPath.SCALAR_NOT_PROVEN_BY_CONSTRUCTION)
tca_forbidden_pattern_collection_not_proven_by_construction = Document.model_validate_context(ForbiddenPatternPath.COLLECTION_NOT_PROVEN_BY_CONSTRUCTION)
tca_forbidden_pattern_open_product = Document.model_validate_context(ForbiddenPatternPath.OPEN_PRODUCT)
tca_forbidden_pattern_field_the_ontology_did_not_model = Document.model_validate_context(ForbiddenPatternPath.FIELD_THE_ONTOLOGY_DID_NOT_MODEL)
tca_forbidden_pattern_frozen_live_edge = Document.model_validate_context(ForbiddenPatternPath.FROZEN_LIVE_EDGE)
tca_forbidden_pattern_dead_handle = Document.model_validate_context(ForbiddenPatternPath.DEAD_HANDLE)
tca_forbidden_pattern_unmodeled_behavior = Document.model_validate_context(ForbiddenPatternPath.UNMODELED_BEHAVIOR)
tca_forbidden_pattern_stub_verb = Document.model_validate_context(ForbiddenPatternPath.STUB_VERB)
tca_forbidden_pattern_swallowed_failure = Document.model_validate_context(ForbiddenPatternPath.SWALLOWED_FAILURE)
tca_forbidden_pattern_serialization_in_the_domain = Document.model_validate_context(ForbiddenPatternPath.SERIALIZATION_IN_THE_DOMAIN)
tca_forbidden_pattern_bare_root_mid_graph = Document.model_validate_context(ForbiddenPatternPath.BARE_ROOT_MID_GRAPH)
tca_forbidden_pattern_surface_drifted_from_the_verb_row = Document.model_validate_context(ForbiddenPatternPath.SURFACE_DRIFTED_FROM_THE_VERB_ROW)
tca_forbidden_pattern_body_drifted_from_the_chain = Document.model_validate_context(ForbiddenPatternPath.BODY_DRIFTED_FROM_THE_CHAIN)
tca_forbidden_pattern_multiple_constructions_in_one_verb = Document.model_validate_context(ForbiddenPatternPath.MULTIPLE_CONSTRUCTIONS_IN_ONE_VERB)
tca_forbidden_pattern_verb_absent_from_the_surface = Document.model_validate_context(ForbiddenPatternPath.VERB_ABSENT_FROM_THE_SURFACE)
tca_forbidden_pattern_free_method_on_a_frozen_value = Document.model_validate_context(ForbiddenPatternPath.FREE_METHOD_ON_A_FROZEN_VALUE)
tca_forbidden_pattern_union_as_a_class = Document.model_validate_context(ForbiddenPatternPath.UNION_AS_A_CLASS)
tca_forbidden_pattern_union_alias_built_wrong = Document.model_validate_context(ForbiddenPatternPath.UNION_ALIAS_BUILT_WRONG)
tca_forbidden_pattern_unclaimed_class = Document.model_validate_context(ForbiddenPatternPath.UNCLAIMED_CLASS)
tca_forbidden_pattern_unmodeled_or_drifted_enum = Document.model_validate_context(ForbiddenPatternPath.UNMODELED_OR_DRIFTED_ENUM)


class DocumentCollection(RootModel[tuple[Document, ...]], frozen=True):
    """The doctrine corpus: every Claude-Code markdown document the program serves."""

    root: tuple[Document, ...] = Field(min_length=1)


documents = DocumentCollection(
    (
        tca_authorized_construct_binding,
        tca_authorized_construct_collection,
        tca_authorized_construct_composition_root,
        tca_authorized_construct_concept_model,
        tca_authorized_construct_config,
        tca_authorized_construct_consistency_model,
        tca_authorized_construct_contract_model,
        tca_authorized_construct_derivation,
        tca_authorized_construct_foreign_model,
        tca_authorized_construct_ordered_union,
        tca_authorized_construct_route,
        tca_authorized_construct_semantic_scalar,
        tca_authorized_construct_union,
        tca_authorized_construct_value_object,
        tca_authorized_construct_verb,
        tca_required_reference_jargon,
        tca_required_reference_topology,
        tca_required_reference_documentation,
        tca_forbidden_pattern_after_validator,
        tca_forbidden_pattern_module_level_function,
        tca_forbidden_pattern_pre_construction_munging,
        tca_forbidden_pattern_nullable_absence,
        tca_forbidden_pattern_mutable_bag,
        tca_forbidden_pattern_bare_primitive,
        tca_forbidden_pattern_free_floating_vocabulary,
        tca_forbidden_pattern_arbitrary_type_off_the_edge,
        tca_forbidden_pattern_scalar_not_proven_by_construction,
        tca_forbidden_pattern_collection_not_proven_by_construction,
        tca_forbidden_pattern_open_product,
        tca_forbidden_pattern_field_the_ontology_did_not_model,
        tca_forbidden_pattern_frozen_live_edge,
        tca_forbidden_pattern_dead_handle,
        tca_forbidden_pattern_unmodeled_behavior,
        tca_forbidden_pattern_stub_verb,
        tca_forbidden_pattern_swallowed_failure,
        tca_forbidden_pattern_serialization_in_the_domain,
        tca_forbidden_pattern_bare_root_mid_graph,
        tca_forbidden_pattern_surface_drifted_from_the_verb_row,
        tca_forbidden_pattern_body_drifted_from_the_chain,
        tca_forbidden_pattern_multiple_constructions_in_one_verb,
        tca_forbidden_pattern_verb_absent_from_the_surface,
        tca_forbidden_pattern_free_method_on_a_frozen_value,
        tca_forbidden_pattern_union_as_a_class,
        tca_forbidden_pattern_union_alias_built_wrong,
        tca_forbidden_pattern_unclaimed_class,
        tca_forbidden_pattern_unmodeled_or_drifted_enum,
    )
)
