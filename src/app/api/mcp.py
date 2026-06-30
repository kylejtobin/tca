"""The doctrine MCP surface: every doctrine document served as one tool. Each tool advertises its
card's name and description (the trigger the model reads) and returns the card's markdown body on
call (the payload). One tool per document in the collection, named the same string across the card,
the constant, and the tool."""

from fastmcp import FastMCP

from app.domain.construction.plan import Plan
from app.domain.resource import collection

mcp = FastMCP("tca")


@mcp.tool(
    name="tca_construction_plan",
    description=(
        "Submit a construction worksheet: every construct a build activity will produce, as a graph "
        "of entries that reference one another by name. The input is the Plan worksheet; an entry "
        "that is not a legal construct fails at the boundary. Returns the validated worksheet."
    ),
)
def tca_construction_plan(plan: Plan) -> str:
    # Ingress route: FastMCP constructs the Plan from raw transport, so an off-construct entry never
    # reaches here. Dispatch to a construction verb lands once the construction consistency model exists.
    return plan.model_dump_json()


@mcp.tool(
    name=collection.tca_authorized_construct_binding.name.root,
    description=collection.tca_authorized_construct_binding.description.root,
)
def tca_authorized_construct_binding() -> str:
    return collection.tca_authorized_construct_binding.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_collection.name.root,
    description=collection.tca_authorized_construct_collection.description.root,
)
def tca_authorized_construct_collection() -> str:
    return collection.tca_authorized_construct_collection.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_composition_root.name.root,
    description=collection.tca_authorized_construct_composition_root.description.root,
)
def tca_authorized_construct_composition_root() -> str:
    return collection.tca_authorized_construct_composition_root.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_concept_model.name.root,
    description=collection.tca_authorized_construct_concept_model.description.root,
)
def tca_authorized_construct_concept_model() -> str:
    return collection.tca_authorized_construct_concept_model.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_config.name.root,
    description=collection.tca_authorized_construct_config.description.root,
)
def tca_authorized_construct_config() -> str:
    return collection.tca_authorized_construct_config.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_consistency_model.name.root,
    description=collection.tca_authorized_construct_consistency_model.description.root,
)
def tca_authorized_construct_consistency_model() -> str:
    return collection.tca_authorized_construct_consistency_model.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_contract_model.name.root,
    description=collection.tca_authorized_construct_contract_model.description.root,
)
def tca_authorized_construct_contract_model() -> str:
    return collection.tca_authorized_construct_contract_model.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_derivation.name.root,
    description=collection.tca_authorized_construct_derivation.description.root,
)
def tca_authorized_construct_derivation() -> str:
    return collection.tca_authorized_construct_derivation.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_foreign_model.name.root,
    description=collection.tca_authorized_construct_foreign_model.description.root,
)
def tca_authorized_construct_foreign_model() -> str:
    return collection.tca_authorized_construct_foreign_model.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_ordered_union.name.root,
    description=collection.tca_authorized_construct_ordered_union.description.root,
)
def tca_authorized_construct_ordered_union() -> str:
    return collection.tca_authorized_construct_ordered_union.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_route.name.root,
    description=collection.tca_authorized_construct_route.description.root,
)
def tca_authorized_construct_route() -> str:
    return collection.tca_authorized_construct_route.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_semantic_scalar.name.root,
    description=collection.tca_authorized_construct_semantic_scalar.description.root,
)
def tca_authorized_construct_semantic_scalar() -> str:
    return collection.tca_authorized_construct_semantic_scalar.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_union.name.root,
    description=collection.tca_authorized_construct_union.description.root,
)
def tca_authorized_construct_union() -> str:
    return collection.tca_authorized_construct_union.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_value_object.name.root,
    description=collection.tca_authorized_construct_value_object.description.root,
)
def tca_authorized_construct_value_object() -> str:
    return collection.tca_authorized_construct_value_object.body.root


@mcp.tool(
    name=collection.tca_authorized_construct_verb.name.root,
    description=collection.tca_authorized_construct_verb.description.root,
)
def tca_authorized_construct_verb() -> str:
    return collection.tca_authorized_construct_verb.body.root


@mcp.tool(
    name=collection.tca_required_reference_jargon.name.root,
    description=collection.tca_required_reference_jargon.description.root,
)
def tca_required_reference_jargon() -> str:
    return collection.tca_required_reference_jargon.body.root


@mcp.tool(
    name=collection.tca_required_reference_topology.name.root,
    description=collection.tca_required_reference_topology.description.root,
)
def tca_required_reference_topology() -> str:
    return collection.tca_required_reference_topology.body.root


@mcp.tool(
    name=collection.tca_required_reference_documentation.name.root,
    description=collection.tca_required_reference_documentation.description.root,
)
def tca_required_reference_documentation() -> str:
    return collection.tca_required_reference_documentation.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_after_validator.name.root,
    description=collection.tca_forbidden_pattern_after_validator.description.root,
)
def tca_forbidden_pattern_after_validator() -> str:
    return collection.tca_forbidden_pattern_after_validator.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_module_level_function.name.root,
    description=collection.tca_forbidden_pattern_module_level_function.description.root,
)
def tca_forbidden_pattern_module_level_function() -> str:
    return collection.tca_forbidden_pattern_module_level_function.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_pre_construction_munging.name.root,
    description=collection.tca_forbidden_pattern_pre_construction_munging.description.root,
)
def tca_forbidden_pattern_pre_construction_munging() -> str:
    return collection.tca_forbidden_pattern_pre_construction_munging.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_nullable_absence.name.root,
    description=collection.tca_forbidden_pattern_nullable_absence.description.root,
)
def tca_forbidden_pattern_nullable_absence() -> str:
    return collection.tca_forbidden_pattern_nullable_absence.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_mutable_bag.name.root,
    description=collection.tca_forbidden_pattern_mutable_bag.description.root,
)
def tca_forbidden_pattern_mutable_bag() -> str:
    return collection.tca_forbidden_pattern_mutable_bag.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_bare_primitive.name.root,
    description=collection.tca_forbidden_pattern_bare_primitive.description.root,
)
def tca_forbidden_pattern_bare_primitive() -> str:
    return collection.tca_forbidden_pattern_bare_primitive.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_free_floating_vocabulary.name.root,
    description=collection.tca_forbidden_pattern_free_floating_vocabulary.description.root,
)
def tca_forbidden_pattern_free_floating_vocabulary() -> str:
    return collection.tca_forbidden_pattern_free_floating_vocabulary.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_arbitrary_type_off_the_edge.name.root,
    description=collection.tca_forbidden_pattern_arbitrary_type_off_the_edge.description.root,
)
def tca_forbidden_pattern_arbitrary_type_off_the_edge() -> str:
    return collection.tca_forbidden_pattern_arbitrary_type_off_the_edge.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_scalar_not_proven_by_construction.name.root,
    description=collection.tca_forbidden_pattern_scalar_not_proven_by_construction.description.root,
)
def tca_forbidden_pattern_scalar_not_proven_by_construction() -> str:
    return collection.tca_forbidden_pattern_scalar_not_proven_by_construction.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_collection_not_proven_by_construction.name.root,
    description=collection.tca_forbidden_pattern_collection_not_proven_by_construction.description.root,
)
def tca_forbidden_pattern_collection_not_proven_by_construction() -> str:
    return collection.tca_forbidden_pattern_collection_not_proven_by_construction.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_open_product.name.root,
    description=collection.tca_forbidden_pattern_open_product.description.root,
)
def tca_forbidden_pattern_open_product() -> str:
    return collection.tca_forbidden_pattern_open_product.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_field_the_ontology_did_not_model.name.root,
    description=collection.tca_forbidden_pattern_field_the_ontology_did_not_model.description.root,
)
def tca_forbidden_pattern_field_the_ontology_did_not_model() -> str:
    return collection.tca_forbidden_pattern_field_the_ontology_did_not_model.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_frozen_live_edge.name.root,
    description=collection.tca_forbidden_pattern_frozen_live_edge.description.root,
)
def tca_forbidden_pattern_frozen_live_edge() -> str:
    return collection.tca_forbidden_pattern_frozen_live_edge.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_dead_handle.name.root,
    description=collection.tca_forbidden_pattern_dead_handle.description.root,
)
def tca_forbidden_pattern_dead_handle() -> str:
    return collection.tca_forbidden_pattern_dead_handle.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_unmodeled_behavior.name.root,
    description=collection.tca_forbidden_pattern_unmodeled_behavior.description.root,
)
def tca_forbidden_pattern_unmodeled_behavior() -> str:
    return collection.tca_forbidden_pattern_unmodeled_behavior.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_stub_verb.name.root,
    description=collection.tca_forbidden_pattern_stub_verb.description.root,
)
def tca_forbidden_pattern_stub_verb() -> str:
    return collection.tca_forbidden_pattern_stub_verb.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_swallowed_failure.name.root,
    description=collection.tca_forbidden_pattern_swallowed_failure.description.root,
)
def tca_forbidden_pattern_swallowed_failure() -> str:
    return collection.tca_forbidden_pattern_swallowed_failure.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_serialization_in_the_domain.name.root,
    description=collection.tca_forbidden_pattern_serialization_in_the_domain.description.root,
)
def tca_forbidden_pattern_serialization_in_the_domain() -> str:
    return collection.tca_forbidden_pattern_serialization_in_the_domain.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_bare_root_mid_graph.name.root,
    description=collection.tca_forbidden_pattern_bare_root_mid_graph.description.root,
)
def tca_forbidden_pattern_bare_root_mid_graph() -> str:
    return collection.tca_forbidden_pattern_bare_root_mid_graph.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_surface_drifted_from_the_verb_row.name.root,
    description=collection.tca_forbidden_pattern_surface_drifted_from_the_verb_row.description.root,
)
def tca_forbidden_pattern_surface_drifted_from_the_verb_row() -> str:
    return collection.tca_forbidden_pattern_surface_drifted_from_the_verb_row.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_body_drifted_from_the_chain.name.root,
    description=collection.tca_forbidden_pattern_body_drifted_from_the_chain.description.root,
)
def tca_forbidden_pattern_body_drifted_from_the_chain() -> str:
    return collection.tca_forbidden_pattern_body_drifted_from_the_chain.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_multiple_constructions_in_one_verb.name.root,
    description=collection.tca_forbidden_pattern_multiple_constructions_in_one_verb.description.root,
)
def tca_forbidden_pattern_multiple_constructions_in_one_verb() -> str:
    return collection.tca_forbidden_pattern_multiple_constructions_in_one_verb.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_verb_absent_from_the_surface.name.root,
    description=collection.tca_forbidden_pattern_verb_absent_from_the_surface.description.root,
)
def tca_forbidden_pattern_verb_absent_from_the_surface() -> str:
    return collection.tca_forbidden_pattern_verb_absent_from_the_surface.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_free_method_on_a_frozen_value.name.root,
    description=collection.tca_forbidden_pattern_free_method_on_a_frozen_value.description.root,
)
def tca_forbidden_pattern_free_method_on_a_frozen_value() -> str:
    return collection.tca_forbidden_pattern_free_method_on_a_frozen_value.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_union_as_a_class.name.root,
    description=collection.tca_forbidden_pattern_union_as_a_class.description.root,
)
def tca_forbidden_pattern_union_as_a_class() -> str:
    return collection.tca_forbidden_pattern_union_as_a_class.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_union_alias_built_wrong.name.root,
    description=collection.tca_forbidden_pattern_union_alias_built_wrong.description.root,
)
def tca_forbidden_pattern_union_alias_built_wrong() -> str:
    return collection.tca_forbidden_pattern_union_alias_built_wrong.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_unclaimed_class.name.root,
    description=collection.tca_forbidden_pattern_unclaimed_class.description.root,
)
def tca_forbidden_pattern_unclaimed_class() -> str:
    return collection.tca_forbidden_pattern_unclaimed_class.body.root


@mcp.tool(
    name=collection.tca_forbidden_pattern_unmodeled_or_drifted_enum.name.root,
    description=collection.tca_forbidden_pattern_unmodeled_or_drifted_enum.description.root,
)
def tca_forbidden_pattern_unmodeled_or_drifted_enum() -> str:
    return collection.tca_forbidden_pattern_unmodeled_or_drifted_enum.body.root
