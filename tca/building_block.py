"""Building block classifier — a recursive Pydantic type tree walker.

================================================================================
WHAT THIS SCRIPT TEACHES
================================================================================

This script demonstrates "programming in the construction semantics of
Pydantic" — an architecture where you declare models (types) and wire them
together, and Pydantic's constructor is the evaluator. One call to
model_validate at the root fires the entire tree of construction. Pydantic
descends the type tree, constructing each inner model as it goes.

The types are not the program alone. The types + Pydantic's evaluator are the
program. The types declare the structure and dispatch. Pydantic's construction
engine — field coercion, discriminated union routing, from_attributes reads,
validator hooks — evaluates them. We are writing programs in a specific
runtime's construction semantics, not claiming mystical type-level computation.

If you come from procedural Python, here's the mental shift:

    PROCEDURAL: Write functions. Call them in order. Pass data between them.
    CONSTRUCTION: Declare models. Wire them as fields. Pydantic evaluates the tree.

The script takes ANY Pydantic BaseModel class and recursively classifies its
entire construction graph — every field, and every field of every record-typed
field, all the way down. It does this with zero domain knowledge. It works on
any BaseModel, anywhere.

================================================================================
THE KEY IDEAS
================================================================================

1. NESTED CONSTRUCTION
   One model_validate at the root fires the entire tree of construction.
   Each model declares its children as field types. Pydantic constructs them
   automatically during the parent's validation. You never manually build
   inner models — the type annotations ARE the construction instructions.

2. DISCRIMINATED UNIONS
   Instead of if/elif chains to handle different cases, you declare a variant
   model for each case. Each variant has a Literal tag field. Pydantic reads
   the tag and routes to the correct variant automatically. The variant's
   fields ARE the answer — no computation needed.

3. from_attributes=True
   This is how models read from other models. When Model B has
   from_attributes=True, you can pass it Model A and Pydantic reads A's
   attributes by name to populate B's fields. The field names ARE the wiring.
   Properties count — Pydantic reads them via getattr.

4. SHAPE OVER PROCEDURE
   A well-shaped model with the right field names, types, and aliases does
   most of the work. Pydantic's default coercion handles the rest. If you're
   reaching for a validator or helper function, ask first: can I add an
   intermediate model that makes the shape fit?

5. SELF-CLASSIFYING WRAPPERS
   A RootModel[object] wrapping a raw value + @property projections = a model
   that knows what it is. TypeAnnotation wraps an annotation and exposes .kind.
   ResolvedType wraps a type and exposes .block_kind. Downstream DUs read the
   tag via from_attributes and route automatically. The object classifies
   itself. No external classifier needed.

   This pattern appears TWICE in this script. See it once on TypeAnnotation,
   see it again on ResolvedType, and you own the pattern.

6. DEMAND-DRIVEN RECURSION
   RecordBlock has a children field. LeafBlock doesn't. When Pydantic
   constructs RecordBlock from a ResolvedType via from_attributes, it reads
   .children — which fires ModelTree.model_validate on the inner type,
   producing more ClassifiedNodes. When Pydantic constructs LeafBlock, it
   never reads .children because the field doesn't exist on the variant.
   Nobody decides whether to recurse. The variant's shape IS the decision.

7. IRREDUCIBLE MINIMUM
   Some boundaries can't be crossed with pure shape — like Python's
   dict.items() producing positional tuples instead of named objects.
   At those boundaries, one small validator bridges the gap. Everything
   else is construction. This script has exactly ONE wrap validator that
   does real work: ModelTree._reshape, which iterates dict.items(), pairs
   keys with values, and guards against cycles via a ContextVar. That's the
   irreducible minimum of procedure.

8. THE CONSTRUCTION LIFECYCLE
   The construction machine has five phases. Each produces or extends the
   proven, self-aware object:
     Phase 1: Boundary Transform — Field(alias=...) or mode="before" validator
     Phase 2: Sealed Boundary — mode="wrap" validator (controls IF construction happens)
     Phase 3: Field Construction — Pydantic parses types, from_attributes reads, DUs route
     Phase 4: Proof Obligation — mode="after" validator (cross-field invariants)
     Phase 5: Derived Projection — @computed_field / @cached_property / @property
   One hook — model_post_init — fires after construction but is not a
   construction phase. It reacts to the object's existence (registration,
   side effects) rather than producing it. Projection extends the object.
   Effect extends the world.
   This script uses Phases 1, 2, 3, and 5. Phase 4 (Proof Obligation) isn't needed here.
   Each class below is annotated with which phase(s) it demonstrates.

================================================================================
SEMANTIC CONTRACT — what Pydantic guarantees we depend on
================================================================================

This architecture works because Pydantic's construction engine provides
specific guarantees. If you port this pattern to another runtime, these are
the contracts that must hold:

    DISCRIMINATOR ROUTING: When a field is typed as a discriminated union
        (Annotated[A | B, Field(discriminator="tag")]), Pydantic reads the
        tag value from the input and selects the matching variant BEFORE
        constructing fields. Routing is total — an unmatched tag is an error,
        not a silent pass-through. This is what makes DU dispatch exhaustive.

    from_attributes READS: When a model has from_attributes=True, Pydantic
        reads the input object's attributes by name (via getattr) to populate
        the model's fields. Properties count. This is evaluated DURING field
        construction (Phase 3), not lazily. Each field is read exactly once.
        This is what makes self-classifying wrappers work — the wrapper's
        @property fires when Pydantic reads it, not before or after.

    CONSTRUCTION ORDER: Pydantic processes validators in a fixed order:
        mode="before" → mode="wrap" → field construction → mode="after" →
        model_post_init. Within field construction, fields are processed in
        declaration order. Parent fields before child fields (inheritance).
        This ordering is what makes the construction lifecycle predictable.

    COERCION: When a field expects type T and receives compatible data,
        Pydantic constructs T from that data automatically. Pass a raw
        annotation where TypeAnnotation is expected — Pydantic wraps it.
        Pass a dict where a BaseModel is expected — Pydantic constructs it.
        This is what makes nested construction work without manual building.

    FROZEN IMMUTABILITY: frozen=True prevents attribute assignment after
        construction. Combined with tuple (not list) for sequences, this
        means a constructed value's fields never change. @cached_property
        is safe because the inputs to the derivation are stable. Derived
        projections are referentially transparent.

    COMPUTED FIELD REALIZATION: @computed_field values are NOT computed at
        construction time. They materialize on first access (via
        @cached_property) and are then cached. They ARE included in
        model_dump() and model_dump_json() — they serialize as if they
        were stored fields. This is what makes projection models serve
        both programmatic access and JSON serialization.

================================================================================
THE CASCADE
================================================================================

One call does everything:

    tree = ModelTree.model_validate(Team)

Here is every step that fires, annotated with WHAT does the work and WHY:

    ModelTree.model_validate(Team)              # YOU call this. One call.
    │
    │  ┌─ WRAP VALIDATOR (_reshape) ─────────────────────────────────────┐
    │  │  WHY: model_fields is a dict. Dict keys aren't attributes.      │
    │  │  This is the ONE irreducible boundary — someone must iterate    │
    │  │  dict.items() and pair keys with values. Also guards against    │
    │  │  cycles: if Team was already seen, return empty fields.         │
    │  │                                                                 │
    │  │  HOW: FieldSlot.model_validate(item) for each (name, FieldInfo) │
    │  │  CYCLE: ContextVar[frozenset[type]] tracks visited types.       │
    │  │  frozenset | {data} creates a new set per level — no mutation.  │
    │  └─────────────────────────────────────────────────────────────────┘
    │
    ├─► FieldSlot.model_validate( ("budget_authority", FieldInfo) )
    │   │
    │   │  ┌─ BEFORE VALIDATOR (_from_tuple) ────────────────────────────┐
    │   │  │  WHY: Tuples have positions, not names. Models need names.  │
    │   │  │  HOW: {"field_name": data[0], "annotation": data[1].ann}    │
    │   │  └─────────────────────────────────────────────────────────────┘
    │   │
    │   ├─ field_name = "budget_authority"        # from dict key
    │   ├─ annotation = TypeAnnotation(RoleName)  # Pydantic coerces raw → TypeAnnotation
    │   └─ resolved_type → ResolvedType(RoleName) # @property wraps inner type (Phase 5)
    │
    ├─► Pydantic coerces FieldSlot → ClassifiedNode  (from_attributes=True)
    │   │
    │   │  ClassifiedNode inherits FieldEntry. FieldEntry declares:
    │   │    field_name: str                      ← reads FieldSlot.field_name ✓
    │   │    shape: AnnotationShape = Field(alias="annotation")
    │   │                                         ← reads FieldSlot.annotation ✓
    │   │
    │   │  ┌─ ANNOTATION SHAPE DU (#1: annotation form) ──────────────────┐
    │   │  │  FieldSlot.annotation is a TypeAnnotation (self-classifying   │
    │   │  │  wrapper #1). Pydantic reads .kind (@property):              │
    │   │  │    get_origin(RoleName) → None → AnnotationKind.DIRECT       │
    │   │  │                                                              │
    │   │  │  DU sees kind="direct" → selects DirectAnnotation:           │
    │   │  │    nullable = Literal[False]     (constant, not computed)    │
    │   │  │    collection = Literal[False]   (constant, not computed)    │
    │   │  │    resolved_type = RoleName      (unwrapped inner type)      │
    │   │  └──────────────────────────────────────────────────────────────┘
    │   │
    │   │  ClassifiedNode also declares:
    │   │    block_shape: BlockShape = Field(alias="resolved_type")
    │   │                                         ← reads FieldSlot.resolved_type ✓
    │   │
    │   │  ┌─ BLOCK SHAPE DU (#2: type classification) ───────────────────┐
    │   │  │  FieldSlot.resolved_type is a ResolvedType (self-classifying  │
    │   │  │  wrapper #2). Pydantic reads .block_kind (@property):        │
    │   │  │    issubclass(RoleName, StrEnum)? No.                        │
    │   │  │    issubclass(RoleName, RootModel)? Yes → Block.NEWTYPE      │
    │   │  │                                                              │
    │   │  │  DU sees block_kind="newtype" → selects LeafBlock:           │
    │   │  │    No children field → ResolvedType.children NEVER FIRES     │
    │   │  │    Recursion doesn't happen. The shape decided.              │
    │   │  └──────────────────────────────────────────────────────────────┘
    │   │
    │   │  For a RECORD field like team: Team (a BaseModel):
    │   │    ResolvedType.block_kind → Block.RECORD → selects RecordBlock
    │   │    RecordBlock HAS children: tuple[ClassifiedNode, ...]
    │   │    Pydantic reads ResolvedType.children → fires:
    │   │      ModelTree.model_validate(Team) → RECURSE (entire cascade again)
    │   │    The children ARE the recursive result. Construction IS descent.
    │   │
    │   └─ Result: ClassifiedNode(
    │        field_name="budget_authority",
    │        shape=DirectAnnotation(nullable=False, collection=False, ...),
    │        block_shape=LeafBlock(block_kind=Block.NEWTYPE)
    │      )
    │
    └─► tree.fields = (ClassifiedNode(...), ClassifiedNode(...), ...)

    For an Optional field like reports_to: RoleName | None:
      TypeAnnotation.kind → OPTIONAL (structural form)
      TypeAnnotation.resolved_type → RoleName (unwrapped — strips the | None)
      DU selects OptionalAnnotation → nullable=Literal[True] ← THE SHAPE IS THE ANSWER

    ┌─ PROJECTION: RENDERING IS RECURSIVE CONSTRUCTION ─────────────────────┐
    │                                                                       │
    │  report = TreeReport.model_validate(tree)   # Another model_validate. │
    │    └─ reports: tuple[FieldReport, ...] = Field(alias="fields")        │
    │         └─ FieldReport reads ClassifiedNode via from_attributes:      │
    │              field_name ← ClassifiedNode.field_name                   │
    │              block ← ClassifiedNode.block (delegates to block_shape)  │
    │              nullable ← ClassifiedNode.nullable (@property)           │
    │              collection ← ClassifiedNode.collection (@property)       │
    │              children ← ClassifiedNode.children → FieldReport(...)    │
    │         └─ line: str ← @computed_field — one field's display string   │
    │         └─ lines: tuple[str, ...] ← recursive flatten of all lines   │
    │    └─ text: str ← @computed_field — indented tree rendering           │
    │                                                                       │
    │  print(report)  →  report.__str__()  →  self.text (cached)            │
    │  TreeReport owns indentation. FieldReport has no knowledge of depth.  │
    └───────────────────────────────────────────────────────────────────────┘

No helper functions. No if-chains. No manual dict building between steps.
The models wire to each other through field declarations and from_attributes.

================================================================================
THE BUILDING BLOCK HIERARCHY
================================================================================

Every type in a Pydantic program is one of these building blocks:

    | Block      | What it is                           | Pydantic construct      |
    |------------|--------------------------------------|-------------------------|
    | ENUM       | Closed vocabulary                    | StrEnum                 |
    | NEWTYPE    | Semantic scalar wrapper              | RootModel[scalar]       |
    | COLLECTION | Immutable sequence wrapper           | RootModel[tuple[T,...]] |
    | RECORD     | Frozen product with named fields     | BaseModel, frozen=True  |
    | ALGEBRA    | Record + derived fields              | Record + @computed_field|
    | EFFECT     | Record + side effects on construction| Record + model_post_init|
    | SCALAR     | Primitive (str, int, bool, etc.)     | bare Python types       |
    | UNION      | Sum type / discriminated union       | Annotated[A|B, Field()] |

Use the simplest construct that does the job. Enum before Newtype before Record.

Note: this taxonomy is pragmatic, not orthogonal. ALGEBRA and EFFECT are
behavioral refinements of RECORD — they differ in what happens during or
after construction, not in data shape. A pure decomposition would separate
data shape (scalar/enum/record/collection/sum) from behavioral refinement
(pure/projected/effectful). We keep a flat taxonomy because the classifier
needs one discriminator axis, and the predicate table in ResolvedType already
encodes the priority ordering (ALGEBRA and EFFECT checked before RECORD).

================================================================================
USAGE
================================================================================

    uv run python .claude/scripts/building_block.py module:ClassName
    uv run python .claude/scripts/building_block.py module:ClassName --json

Examples:
    uv run python .claude/scripts/building_block.py arm_ont.team:Team
    uv run python .claude/scripts/building_block.py arm_ont.team:Team --json
    uv run python .claude/scripts/building_block.py arm_ont.role:Role
    uv run python .claude/scripts/building_block.py pydantic:BaseModel

    --json outputs the full recursive tree as JSON (for bots and tooling).
    Without --json, outputs indented human-readable text.

TWO AUDIENCES, ZERO EXTRA CODE:
    The same TreeReport serves both. For humans, __str__ delegates to .text
    (the indented rendering). For bots, model_dump_json() serializes the
    entire recursive FieldReport tree — including .line and .lines, because
    they're @computed_field. No separate "JSON formatter." The projection
    model IS the API.

================================================================================
SEMANTIC INDEX TYPES AND FIELD DESCRIPTIONS
================================================================================

A semantic index type is a type declaration where natural-language tokens —
field names, descriptions, and enum member names — function as computational
instructions for a consumer that reads them. In a conventional type system, a
field name is just an address: it tells the system WHICH slot. In a semantic
index type, the field name also tells the consumer WHAT to put in that slot.

This matters because Pydantic models are consumed by language models. When an
LLM sees a schema (via model_json_schema(), tool definitions, or structured
output), it reads field names and Field(description=...) values as natural-
language instructions. Changing a field name or description changes what the
model computes. Renaming is refactoring. The description is part of the program.

A type annotation and a field description form a two-channel system:

    STRUCTURAL CHANNEL: The type annotation bounds the space of valid values.
        bool gives 2 values. A 4-member enum gives 4. str gives unbounded.
        This channel is enforced mechanically — the consumer physically
        cannot produce a value outside the type's constraints.

    SEMANTIC CHANNEL: The Field(description=...) guides the consumer's
        selection WITHIN the structurally valid space. It determines which
        valid value the consumer produces. The tighter the structural
        constraint, the less the description needs to do. A bool has 1 bit
        of freedom — the description resolves which bit. A bare str has
        unbounded freedom — the description bears the full burden.

Field descriptions in this file are NOT documentation. Docstrings teach how the
code works. Comments teach the meta-principles. Field descriptions are semantic
indices — they instruct the consumer (human or LLM) about what each field's
value MEANS for the model being analyzed.

OUR STRATEGY IN THIS FILE:

    This tool classifies Pydantic models for developers and agents building
    construction-first programs. Its consumers hold a classification result
    and need to know: what does this value tell me about the model I analyzed?
    Where is modeling incomplete? What should I build next?

    Each Field(description=...) answers that question for its field. It uses
    the vocabulary of the domain (type analysis, field classification, model
    structure) — not the vocabulary of the implementation (validators,
    construction phases, internal wiring). It says only what the type
    annotation doesn't already say. It grounds in what the value tells the
    consumer, not how the program computed it.

    Literal constant fields (like nullable: Literal[False] on DirectAnnotation)
    have ZERO degrees of freedom — the type says everything. No description
    needed. Fields with real degrees of freedom get descriptions calibrated
    to their structural compression: a bool (1 bit) gets a short precise
    description. An 8-member enum gets a description that maps each value
    to its meaning. An unbounded str gets a description that fully specifies
    the expected content.

THE GENERIC PROMPT FOR WRITING FIELD DESCRIPTIONS:

    Gather what the program does, who uses its output, and what they do with
    it specifically. Then walk the construction graph from leaves to roots.
    For each field, write a Field(description=...) that:

    1. Uses the fewest tokens that leave zero ambiguity about what the value
       means in this program's domain
    2. Says only what the type annotation doesn't already say — the type
       handled its part, the description handles the rest
    3. Grounds in what the value tells the consumer about the thing being
       analyzed, not how the program computed it

    Use the vocabulary of the domain, not the vocabulary of the
    implementation.

    Do not explain the codebase. Do not teach concepts. Do not reference
    frameworks or architectural patterns. Each description is an instruction
    that resolves what this field's value means for the consumer holding
    the result.
"""

from __future__ import annotations

import importlib
import types
from collections.abc import Callable
from contextvars import ContextVar
from enum import StrEnum
from typing import (
    Annotated,
    ClassVar,
    Literal,
    TypeAliasType,
    get_args,
    get_origin,
    override,
)

from functools import cached_property

from pydantic import BaseModel, Field, RootModel, computed_field, model_validator
from pydantic.fields import FieldInfo


# =============================================================================
# ENUMS — closed vocabularies that drive dispatch
# =============================================================================
# Enums are the simplest building block. They're exhaustive — every consumer
# must handle every variant. Add a variant, the type checker finds every
# incomplete match. That's why we use them for classification tags.


class Block(StrEnum):
    """The eight structural building blocks of a Pydantic program.

    Every type you encounter in a Pydantic model is one of these. The
    classifier inspects a type and tells you which block it is. This enum
    is CLOSED — no other blocks exist. That's what makes dispatch total.
    """

    ENUM = "enum"  # StrEnum — closed set of string values
    NEWTYPE = "newtype"  # RootModel[scalar] — semantic wrapper (e.g. UserName(str))
    COLLECTION = "collection"  # RootModel[tuple[T, ...]] — immutable sequence
    RECORD = "record"  # BaseModel, frozen=True — product type with named fields
    ALGEBRA = "algebra"  # Record + @computed_field — stored fields in, derived out
    EFFECT = "effect"  # Record + model_post_init — construction triggers action
    SCALAR = "scalar"  # str, int, bool, etc. — Python primitives
    UNION = "union"  # Annotated[A | B, Field(discriminator=...)] — sum type

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class AnnotationKind(StrEnum):
    """The four structural forms a Python type annotation can take.

    Python annotations aren't always plain types. They can be wrapped in
    structural constructs: Optional (X | None), tuple (tuple[X, ...]),
    or TypeAliasType (type X = ...). This enum captures WHICH wrapping
    form an annotation has. The AnnotationShape DU below uses it as its
    discriminator — the kind tag routes to the correct variant.
    """

    DIRECT = "direct"  # Plain type: str, int, MyModel
    OPTIONAL = "optional"  # X | None — nullable
    TUPLE = "tuple"  # tuple[X, ...] — homogeneous collection
    ALIAS = "alias"  # type X = ... — TypeAliasType

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


# =============================================================================
# ANNOTATION SHAPE — discriminated union (Phase 3: Field Construction)
# =============================================================================
# This is the core teaching example of a discriminated union (DU) and of
# Phase 3: Field Construction. When Pydantic constructs an AnnotationShape
# field, it reads the "kind" tag and selects the matching variant. This
# happens automatically during field construction — no code triggers it.
#
# In procedural code you'd write:
#     if is_optional(ann): nullable = True
#     elif is_tuple(ann): collection = True
#     ...
#
# Instead, we declare a VARIANT MODEL for each case. Each variant has:
#   - A Literal tag (kind) that identifies it
#   - Fields whose VALUES are baked into the type (Literal[True], Literal[False])
#
# Pydantic reads the tag, selects the variant, and the variant's fields
# ARE the answer. No computation. The shape IS the program.
#
# Notice: nullable and collection are Literal[True] or Literal[False] on
# three of the four variants. They're not computed — they're CONSTANTS
# determined by which variant was selected. That's the power of DUs:
# dispatch replaces computation.


class DirectAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A plain type annotation — not wrapped in Optional, tuple, or alias.

    Examples: str, int, TeamName, BaseModel subclasses.
    Always nullable=False, collection=False — a direct type is neither.
    """

    kind: Literal[AnnotationKind.DIRECT] = AnnotationKind.DIRECT
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[False] = False  # Direct types aren't nullable
    collection: Literal[False] = False  # Direct types aren't collections


class OptionalAnnotation(BaseModel, frozen=True, from_attributes=True):
    """An X | None annotation — the field can be absent.

    Examples: RoleName | None, str | None.
    Always nullable=True — that's what Optional MEANS.
    """

    kind: Literal[AnnotationKind.OPTIONAL] = AnnotationKind.OPTIONAL
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[True] = True  # Optional is ALWAYS nullable
    collection: Literal[False] = False


class TupleAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A tuple[X, ...] annotation — a homogeneous immutable sequence.

    Examples: tuple[str, ...], tuple[TeamName, ...].
    Always collection=True — that's what tuple[X, ...] MEANS.
    """

    kind: Literal[AnnotationKind.TUPLE] = AnnotationKind.TUPLE
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[False] = False
    collection: Literal[True] = True  # Tuple IS a collection


class AliasAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A TypeAliasType annotation — created by 'type X = ...' syntax.

    Examples: type Authority = LimitedAuthority | UnlimitedAuthority | NoAuthority
    nullable and collection depend on what the alias resolves to, so they're
    plain bool here, not Literal constants.
    """

    kind: Literal[AnnotationKind.ALIAS] = AnnotationKind.ALIAS
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: bool = Field(
        default=False, description="True when the alias target is an Optional type"
    )
    collection: bool = Field(
        default=False, description="True when the alias target is a tuple type"
    )


# The discriminated union itself. Pydantic reads the "kind" field from the
# input data and routes to the matching variant. This is the type-level
# equivalent of a match/case statement — but it fires DURING CONSTRUCTION,
# not in calling code. The consumer never switches on kind. They just
# read .nullable and .collection from whatever variant was selected.
AnnotationShape = Annotated[
    DirectAnnotation | OptionalAnnotation | TupleAnnotation | AliasAnnotation,
    Field(discriminator="kind"),
]


# =============================================================================
# TYPE ANNOTATION — self-classifying wrapper #1 (Phase 5: Derived Projection)
# =============================================================================
# This is self-classifying wrapper #1 of two. (ResolvedType is #2.)
#
# THE PATTERN: RootModel[object] wraps a raw value. Properties expose
# derived attributes. Downstream DUs read those properties via
# from_attributes=True and auto-route to the correct variant. The object
# classifies itself — no external classifier needed.
#
# Here, TypeAnnotation wraps a raw Python annotation and exposes:
#   .kind → AnnotationKind tag (drives AnnotationShape DU routing)
#   .resolved_type → the inner type after unwrapping structural wrappers
#
# The key insight: from_attributes reads PROPERTIES, not just stored fields.
# So a RootModel with the right properties IS a self-classifying object.
# Pydantic reads .kind, routes the DU, and the variant's Literal fields
# ARE the answer. No one manually determines the kind. The type does it.
#
# .kind and .resolved_type are Phase 5: Derived Projection. Pure functions
# of the frozen root value. Bare @property (not @computed_field) because
# they don't need caching or serialization — trivial derivations read
# once during Phase 3 field construction on downstream models.


class TypeAnnotation(RootModel[object], frozen=True):
    """Self-classifying wrapper #1: raw annotation → structural form.

    Wraps any annotation (type, generic alias, TypeAliasType, etc.) and
    exposes .kind and .resolved_type as properties. Downstream models read
    these via from_attributes=True — enabling automatic DU routing.

    .kind classifies the STRUCTURAL FORM: is this a plain type, an Optional,
    a tuple, or a type alias? The AnnotationShape DU reads .kind and routes.

    .resolved_type UNWRAPS the structure: RoleName | None → RoleName.
    tuple[Team, ...] → Team. type X = Y → Y. The wrapper is captured by
    .kind — resolved_type is what's inside. This unwrapping is what makes
    recursive descent work: a field typed tuple[Team, ...] resolves to Team,
    which classifies as RECORD, which triggers descent into Team's fields.
    """

    @property
    def kind(self) -> AnnotationKind:
        """Detect which structural form this annotation has.

        Uses get_origin() for generic aliases (tuple[X,...], X | None)
        and isinstance() for TypeAliasType. Falls back to DIRECT.
        """
        # get_origin() returns the "base" of a generic alias:
        #   get_origin(str | None) → types.UnionType
        #   get_origin(tuple[str, ...]) → tuple
        #   get_origin(str) → None (not generic)
        o = get_origin(self.root)
        if o is types.UnionType:
            return AnnotationKind.OPTIONAL
        if o is tuple:
            return AnnotationKind.TUPLE
        # TypeAliasType isn't a generic alias — it's a special class
        # created by 'type X = ...' syntax. isinstance detects it.
        if isinstance(self.root, TypeAliasType):
            return AnnotationKind.ALIAS
        return AnnotationKind.DIRECT

    @property
    def resolved_type(self) -> object:
        """The inner type after structural unwrapping.

        The structural wrapper is already captured by .kind — resolved_type
        is what's inside:
          X | None → X (the non-None member)
          tuple[X, ...] → X (the element type)
          type X = Y → Y (the alias target)
          plain type → itself
        """
        o = get_origin(self.root)
        if o is types.UnionType:
            return next(a for a in get_args(self.root) if a is not type(None))  # pyright: ignore[reportAny]

        if o is tuple:
            return get_args(self.root)[0]  # pyright: ignore[reportAny]
        if isinstance(self.root, TypeAliasType):
            return self.root.__value__  # pyright: ignore[reportAny]
        return self.root


# =============================================================================
# FIELD SLOT — bridging the dict boundary (Phases 1, 3, and 5)
# =============================================================================
# Python's model_fields is a dict[str, FieldInfo]. The field NAME is the
# dict KEY, not an attribute on the FieldInfo value. This is the one place
# where pure from_attributes construction can't work — dict keys aren't
# attributes.
#
# FieldSlot is the bridge model. Its Phase 1 before validator takes a
# (key, value) tuple from dict.items() and produces a dict with named
# fields. This is the IRREDUCIBLE MINIMUM of procedure in the entire
# cascade — one small validator that pairs positional data into named data.
# Everything else is pure construction.
#
# Phase 3: The annotation field is typed as TypeAnnotation — Pydantic
# automatically coerces the raw annotation into a TypeAnnotation wrapper.
# The type declaration IS the instruction.
#
# Phase 5: The .resolved_type property wraps the unwrapped inner type in a
# ResolvedType (self-classifying wrapper #2). ClassifiedNode reads this
# during construction via from_attributes, triggering BlockShape DU routing.
# This is the bridge between annotation-level classification (AnnotationShape)
# and type-level classification (BlockShape).


class FieldSlot(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    """A single entry from model_fields: field name + its type annotation.

    Constructed from dict.items() tuples via the before validator.
    populate_by_name=True allows both "name" (alias) and "field_name" to work.

    Two attributes feed downstream construction:
      .annotation (stored field) — TypeAnnotation, coerced during Phase 3.
        ClassifiedNode reads this via alias to construct AnnotationShape DU.
      .resolved_type (property) — ResolvedType, derived during Phase 5.
        ClassifiedNode reads this via alias to construct BlockShape DU.

    The two self-classifying wrappers (TypeAnnotation, ResolvedType) both
    originate here. FieldSlot is the source of truth for everything
    ClassifiedNode needs to classify a field.
    """

    field_name: str = Field(
        alias="name", description="Name of the field on the model being classified"
    )
    annotation: TypeAnnotation = Field(
        description="The field's type annotation as declared in source"
    )

    @model_validator(mode="before")
    @classmethod
    def _from_tuple(cls, data: tuple[str, FieldInfo]) -> dict[str, object]:
        """The irreducible minimum: pair a dict key with its value's annotation.

        dict.items() produces (str, FieldInfo) tuples. Tuples have positions,
        not names. This validator bridges position → name so Pydantic can
        construct the model's named fields. This is the ONE place in the
        entire cascade where we write procedural mapping code.
        """
        return {"field_name": data[0], "annotation": data[1].annotation}

    @property
    def resolved_type(self) -> ResolvedType:
        return ResolvedType(self.annotation.resolved_type)


# =============================================================================
# FIELD ENTRY — alias + DU + properties (Phases 1, 3, and 5 together)
# =============================================================================
# This model demonstrates three phases firing in sequence on one class:
#
# Phase 1 (Boundary Transform): Field(alias="annotation") — Pydantic reads
#   .annotation from the FieldSlot. Pure declaration, no validator needed.
#   This is the cleanest form of Phase 1: an alias, not a before validator.
#
# Phase 3 (Field Construction): Pydantic constructs AnnotationShape (the DU)
#   from the TypeAnnotation it just read. TypeAnnotation.kind drives the DU
#   routing. The DU selects the variant. The variant's Literal fields set
#   nullable/collection. All automatic — no code triggers it.
#
# Phase 5 (Derived Projection): Properties delegate to self.shape, exposing
#   resolved_type, nullable, collection as flat attributes. from_attributes
#   on ClassifiedNode reads these properties. The flattening IS the projection.


class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    """A field with its annotation resolved into an AnnotationShape.

    The shape field is aliased from "annotation" — when Pydantic constructs
    a FieldEntry from a FieldSlot (via from_attributes), it reads
    FieldSlot.annotation (a TypeAnnotation), and constructs the AnnotationShape
    DU from it. TypeAnnotation.kind drives the DU routing. TypeAnnotation.resolved_type
    provides the inner type.

    Properties flatten the nested shape for ClassifiedNode to read:
      ClassifiedNode.from_attributes → reads .resolved_type, .nullable, .collection
      These are properties on FieldEntry, delegating to self.shape.
    """

    field_name: str = Field(
        description="Name of the field on the model being classified"
    )
    shape: AnnotationShape = Field(
        alias="annotation",
        description="Structural form of the annotation — direct, optional, tuple, or alias — with nullable and collection flags",
    )

    @property
    def resolved_type(self) -> object:
        """Delegate to shape — ClassifiedNode reads this via from_attributes."""
        return self.shape.resolved_type

    @property
    def nullable(self) -> bool:
        """Delegate to shape — True if the annotation was X | None."""
        return self.shape.nullable

    @property
    def collection(self) -> bool:
        """Delegate to shape — True if the annotation was tuple[X, ...]."""
        return self.shape.collection


# =============================================================================
# CLASSIFIED NODE — two DUs, full classification (Phase 3 + Phase 5)
# =============================================================================
# ClassifiedNode inherits from FieldEntry. Inheritance in Pydantic means
# "I am a FieldEntry, plus more." Phase 3 fires the parent's fields first
# (field_name, shape via AnnotationShape DU), then ClassifiedNode's own
# field: block_shape via the BlockShape DU.
#
# Two DUs fire during one ClassifiedNode construction:
#   1. AnnotationShape — classifies the annotation form (nullable? collection?)
#      Fed by TypeAnnotation (self-classifying wrapper #1)
#   2. BlockShape — classifies the type itself (record? enum? scalar?)
#      Fed by ResolvedType (self-classifying wrapper #2)
#
# The BlockShape DU is where recursion happens — or doesn't. RecordBlock
# has a children field, so Pydantic reads ResolvedType.children, which
# fires ModelTree.model_validate on the inner type. LeafBlock has no
# children field, so the property never fires. The variant's shape IS
# the recursion decision. Nobody writes "if record: descend."
#
# .block and .children are Phase 5 delegation properties — they forward
# to block_shape so downstream models (FieldReport) see a flat interface.


class ClassifiedNode(FieldEntry, frozen=True, from_attributes=True):
    """One field fully classified: its building block type, structural flags, and children.

    Inherits from FieldEntry — gets field_name, shape, and the flattening
    properties for free. Adds block classification via BlockShape DU routed
    from ResolvedType.block_kind. For recursive variants (RecordBlock,
    AlgebraBlock, EffectBlock), ResolvedType.children fires → recursion.
    """

    block_shape: BlockShape = Field(
        alias="resolved_type",
        description="Building block classification with recursive children for record-like types",
    )

    @property
    def block(self) -> Block:
        return self.block_shape.block_kind

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return self.block_shape.children


# =============================================================================
# RESOLVED TYPE — self-classifying wrapper #2 (Phase 5: Derived Projection)
# =============================================================================
# This is self-classifying wrapper #2 of two. (TypeAnnotation is #1.)
#
# Same pattern, different domain:
#   TypeAnnotation wraps an annotation → .kind classifies the FORM
#   ResolvedType wraps a type         → .block_kind classifies the TYPE
#
# Two properties:
#   .block_kind — walks a predicate table (_BLOCK_MAP) in priority order.
#     The table evolved from the original (type, Block) pairs to
#     (Callable[[type], bool], Block) predicates. The walk is the same
#     one-liner — next() with a default. The table got wider (predicates
#     instead of bare types) so it can express ALGEBRA and EFFECT as
#     refinements of RECORD. Data-driven dispatch scales by widening rows,
#     not adding branches.
#
#   .children — unconditionally calls ModelTree.model_validate(self.root).
#     No guard. No isinstance check. This property is ONLY ever read when
#     a BlockShape DU variant with a children field constructs via
#     from_attributes (RecordBlock, AlgebraBlock, EffectBlock). Leaf
#     variants have no children field, so this property never fires for
#     them. The DU variant's shape IS the guard.


class ResolvedType(RootModel[object], frozen=True):
    """Self-classifying wrapper #2: raw type → building block classification.

    Parallels TypeAnnotation: RootModel[object] wrapping a value, exposing
    derived properties downstream DUs read via from_attributes.

    TypeAnnotation classifies the ANNOTATION FORM (Optional, tuple, alias, direct).
    ResolvedType classifies the TYPE ITSELF (enum, newtype, record, scalar, ...).

    .block_kind drives BlockShape DU variant routing.
    .children provides recursive descent — only ever read when a variant
    with a children field constructs. Leaf variants never request it.
    """

    _BLOCK_MAP: ClassVar[tuple[tuple[Callable[[type], bool], Block], ...]] = (
        (lambda t: issubclass(t, StrEnum), Block.ENUM),
        (lambda t: issubclass(t, RootModel), Block.NEWTYPE),
        (
            lambda t: issubclass(t, BaseModel) and bool(t.model_computed_fields),
            Block.ALGEBRA,
        ),
        (
            lambda t: issubclass(t, BaseModel) and "model_post_init" in vars(t),
            Block.EFFECT,
        ),
        (lambda t: issubclass(t, BaseModel), Block.RECORD),
    )

    @property
    def block_kind(self) -> Block:
        return next(
            (
                b
                for pred, b in self._BLOCK_MAP
                if isinstance(self.root, type) and pred(self.root)
            ),
            Block.SCALAR,
        )

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return ModelTree.model_validate(self.root).fields


# =============================================================================
# BLOCK SHAPE — discriminated union #2 (Phase 3 + demand-driven recursion)
# =============================================================================
# This is the second DU in the cascade. AnnotationShape (#1) classifies the
# annotation FORM (nullable? collection?). BlockShape (#2) classifies the
# TYPE ITSELF (record? enum? scalar?) and controls whether recursion happens.
#
# THE KEY INSIGHT: Recursion is driven by VARIANT SHAPE, not by branching.
#   - RecordBlock, AlgebraBlock, EffectBlock have a children field.
#     When Pydantic constructs them from a ResolvedType (via from_attributes),
#     it reads .children — which fires ModelTree.model_validate(inner_type).
#     That's how recursion starts. Nobody writes "if record: recurse."
#   - LeafBlock has NO children field. It has a .children @property that
#     returns (). Pydantic never reads it during construction (no field
#     demands it). It exists so downstream delegation (ClassifiedNode.children)
#     works uniformly on any variant.
#
# MULTI-VALUE LITERAL: LeafBlock uses Literal[Block.ENUM, Block.NEWTYPE, ...].
# Pydantic supports multiple values in a single Literal for DU discriminators.
# One variant catches all five leaf cases. Without this, you'd need five
# identical leaf variants — shape duplication for no semantic gain.
#
# INVARIANT: Leaf variants must NEVER define a stored field named "children."
# The entire demand-driven recursion pattern depends on Pydantic reading
# ResolvedType.children ONLY when a variant has a children field. If a leaf
# variant gained a children field, Pydantic would read ResolvedType.children
# during construction, triggering recursive descent on non-record types.
# LeafBlock's .children @property (returning ()) exists solely for uniform
# delegation from ClassifiedNode — it is trivial, non-recursive, and must
# remain so.


class RecordBlock(BaseModel, frozen=True, from_attributes=True):
    """A plain BaseModel — frozen product type with named fields.

    Has children: Pydantic reads ResolvedType.children during construction,
    triggering recursive descent into the record's own fields.
    """

    block_kind: Literal[Block.RECORD] = Block.RECORD
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class AlgebraBlock(BaseModel, frozen=True, from_attributes=True):
    """A BaseModel with @computed_field — stored fields in, derived knowledge out.

    Has children: same recursive descent as RecordBlock. The distinction from
    RecordBlock is semantic — the type has derived projections, not just stored
    fields. Detected by checking model_computed_fields.
    """

    block_kind: Literal[Block.ALGEBRA] = Block.ALGEBRA
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class EffectBlock(BaseModel, frozen=True, from_attributes=True):
    """A BaseModel with model_post_init — construction triggers a side effect.

    Has children: same recursive descent. The distinction is semantic — this
    type does something when constructed (registers itself, emits events).
    Detected by checking for model_post_init in the class's own vars().
    """

    block_kind: Literal[Block.EFFECT] = Block.EFFECT
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class LeafBlock(BaseModel, frozen=True, from_attributes=True):
    """A non-record type — enum, newtype, collection, scalar, or union.

    No children field: Pydantic never reads ResolvedType.children when
    constructing a LeafBlock, so recursive descent never fires. The variant's
    shape IS the decision not to recurse.

    The .children property returns () for uniform delegation — ClassifiedNode
    can call self.block_shape.children on any variant without checking type.

    Multi-value Literal: one variant catches all five leaf block kinds.
    Pydantic matches any of them during DU routing.
    """

    block_kind: Literal[
        Block.ENUM, Block.NEWTYPE, Block.COLLECTION, Block.SCALAR, Block.UNION
    ] = Field(
        description="Which leaf building block — enum, newtype, collection, scalar, or union"
    )

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return ()


# The discriminated union itself. Pydantic reads block_kind from the
# ResolvedType (via from_attributes) and routes to the matching variant.
# RecordBlock/AlgebraBlock/EffectBlock → children field fires recursion.
# LeafBlock → no children field, recursion stops.
BlockShape = Annotated[
    RecordBlock | AlgebraBlock | EffectBlock | LeafBlock,
    Field(discriminator="block_kind"),
]


# =============================================================================
# FIELD REPORT + TREE REPORT — recursive rendering (Phase 3 + Phase 5)
# =============================================================================
# In procedural code, rendering means writing a format_output() function that
# loops over results and builds strings. In construction-first code, rendering
# is ANOTHER model_validate (Phase 3: Field Construction) followed by
# @computed_field derivation (Phase 5: Derived Projection).
#
# RECURSIVE STRUCTURE: FieldReport has a children field typed as
# tuple[FieldReport, ...]. When Pydantic constructs a FieldReport from a
# ClassifiedNode, it reads .children (which are ClassifiedNodes) and coerces
# each one into a FieldReport — recursively. The SAME from_attributes
# construction that works at the top level works at every depth. No special
# recursion code. The type annotation IS the recursion instruction.
#
# Phase 3: TreeReport.model_validate(tree) reads .fields from ModelTree via
# from_attributes. Pydantic coerces each ClassifiedNode → FieldReport by
# reading ClassifiedNode's properties (field_name, block, nullable, collection,
# children). Children coerce recursively into more FieldReports.
#
# Phase 5: Three @computed_field projections derive the display:
#   .line — one field's display string, derived from stored fields
#   .lines — recursive flatten of this report + all descendant lines
#   .text (on TreeReport) — indented tree rendering with depth tracking
# All cached on first access, included in model_dump()/JSON.
#
# OWNERSHIP OF DEPTH: TreeReport owns indentation. FieldReport has no
# knowledge of its position in the tree — it just stores its data and its
# children. TreeReport._indent walks the recursive structure and derives
# the visual depth. This separation means FieldReport is reusable in any
# context (flat list, JSON, table), while TreeReport specializes for
# indented text output.
#
# __str__ delegates to .text — Python's display protocol uses the cached
# Phase 5 projection. print(report) fires the entire rendering pipeline.
#
# The cascade: ClassifiedNode → FieldReport → TreeReport → print().
# Each step is model_validate + from_attributes. No string formatting functions.


class FieldReport(BaseModel, frozen=True, from_attributes=True):
    """One classified field projected for display.

    Phase 3: Constructs from ClassifiedNode via from_attributes — reads
    field_name, block, nullable, collection, children.
    Phase 5: line derives the display string, lines recursively flattens
    the tree. Derived once, cached, serializable.
    """

    field_name: str = Field(description="Name of the field on the analyzed model")
    block: Block = Field(
        description="Structural role: record (named fields), enum (closed vocabulary), newtype (typed wrapper), scalar (primitive), algebra (record + derived), effect (record + side effects), collection (sequence wrapper), union (sum type)"
    )
    nullable: bool = Field(
        description="True when the field's type was X | None — the field accepts absence"
    )
    collection: bool = Field(
        description="True when the field's type was tuple[X, ...] — the field holds a sequence"
    )
    children: tuple[FieldReport, ...] = Field(
        default=(),
        description="Classified children of the inner type, present for record/algebra/effect, empty for leaves",
    )

    @computed_field(
        description="Single-line summary: name, block type, nullable, and collection"
    )
    @cached_property
    def line(self) -> str:
        return f"{self.field_name}: {self.block.value} (nullable={self.nullable}, collection={self.collection})"

    @computed_field(
        description="This field's line plus all descendant lines, flattened in tree order"
    )
    @cached_property
    def lines(self) -> tuple[str, ...]:
        return (self.line, *(line for child in self.children for line in child.lines))


# =============================================================================
# MODEL TREE — the root (Phase 2: Sealed Boundary + cycle detection)
# =============================================================================
# The entry point. ModelTree.model_validate(SomeBaseModelClass) fires the
# entire cascade. The wrap validator is Phase 2: Sealed Boundary — it
# controls HOW construction happens by reshaping input and calling handler().
#
# Why wrap, not before? Phase 2 gives you the handler. You reshape the data,
# call handler() exactly once, and Pydantic does normal Phase 3 validation.
# A Phase 1 before validator would return data that Pydantic re-validates —
# but returning a ModelTree instance re-triggers the before validator.
# Infinite recursion. Phase 2 (wrap) avoids this because YOU control when
# the handler fires.
#
# CYCLE DETECTION: Resource graphs can have cycles (Team references Role,
# Role references Team). Without detection, ModelTree.model_validate would
# recurse forever. The _seen ContextVar tracks which types are currently
# being walked. Each recursive call sees the parent's frozenset plus the
# current type. If a type was already seen, construction short-circuits
# with empty fields. frozenset | {data} creates a NEW set per level —
# no mutation, no shared state, natural cleanup via ContextVar.reset().
#
# The full cascade, with phases labeled:
#
#   Phase 2: _reshape wrap validator iterates model_fields.items()
#            + cycle guard: skip if type already in _seen frozenset
#   Phase 1: Each (name, FieldInfo) → FieldSlot._from_tuple (before validator)
#   Phase 3: Pydantic coerces FieldSlots → ClassifiedNodes (from_attributes)
#            FieldEntry alias reads .annotation → constructs AnnotationShape DU
#            TypeAnnotation.kind drives DU routing (Phase 5 property)
#            Variant's Literal fields set nullable/collection
#   Phase 3: ClassifiedNode.block_shape reads FieldSlot.resolved_type
#            → ResolvedType.block_kind drives BlockShape DU routing
#            → RecordBlock.children fires recursive ModelTree.model_validate
#   Phase 5: FieldReport.line / TreeReport.text derive display strings
#
# One wrap validator. Everything else is Phases 1 (alias), 3 (field types +
# from_attributes + DU routing), and 5 (properties + computed_fields).


class ModelTree(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    """Root of the cascade — one model_validate classifies every field on a BaseModel.

    Usage:
        tree = ModelTree.model_validate(Team)
        report = TreeReport.model_validate(tree)
        print(report)

    Cycle detection via _seen ContextVar: each recursive call sees the parent's
    visited set plus the current type. Already-seen types produce empty fields.
    """

    _seen: ClassVar[ContextVar[frozenset[type]]] = ContextVar("_seen")

    fields: tuple[ClassifiedNode, ...] = Field(
        alias="fields",
        description="Every field on the model, fully classified with block type, flags, and recursive children",
    )

    @model_validator(mode="wrap")
    @classmethod
    def _reshape(
        cls, data: type[BaseModel], handler: Callable[..., ModelTree]
    ) -> ModelTree:
        seen = cls._seen.get(frozenset())
        if data in seen:
            return handler({"fields": ()})
        token = cls._seen.set(seen | {data})
        result = handler(
            {
                "fields": tuple(
                    FieldSlot.model_validate(item) for item in data.model_fields.items()
                )
            }
        )
        cls._seen.reset(token)
        return result


class TreeReport(BaseModel, frozen=True, from_attributes=True):
    """Human-readable projection of a ModelTree. The last cascade step.

    Constructs from ModelTree via from_attributes. The alias on reports
    reads .fields from ModelTree — Pydantic coerces each ClassifiedNode
    into a FieldReport (from_attributes reads the properties).

    TreeReport owns indentation — the final projection that flattens
    nested structure into display text. FieldReport has no knowledge of
    its position. TreeReport walks the recursive structure and derives
    the visual depth.
    """

    reports: tuple[FieldReport, ...] = Field(
        alias="fields",
        description="One report per field, each carrying classification results and recursive children",
    )

    @computed_field(
        description="Complete indented tree — each nesting level indented two spaces"
    )
    @cached_property
    def text(self) -> str:
        def _indent(report: FieldReport, depth: int) -> tuple[str, ...]:
            prefix = "  " * depth
            return (
                f"{prefix}{report.line}",
                *(
                    line
                    for child in report.children
                    for line in _indent(child, depth + 1)
                ),
            )

        return "\n".join(line for r in self.reports for line in _indent(r, 0))

    @override
    def __str__(self) -> str:
        return self.text


# =============================================================================
# CLASSIFIER RUN — the CLI as a construction machine (Environment)
# =============================================================================
# The CLI invocation is an Environment in the Program Triad. The stored fields
# are what the program KNOWS before acting: the target string and the output
# format. Everything else is a derived projection chain:
#
#   target (stored) → model_class (resolve) → tree (classify) → report (render)
#
# Each @cached_property is a Phase 5 derivation from frozen fields. The chain
# fires lazily on first access. __str__ is the terminal projection — it reads
# .report (which reads .tree, which reads .model_class, which reads .target).
# One stored field. Four derivations. Zero procedure.
#
# The boundary crossing (importlib + getattr) lives INSIDE the model as a
# projection. The untyped dynamic lookup is contained at the boundary where
# it belongs — not loose in a procedural __main__ block.


class ClassifierRun(BaseModel, frozen=True):
    """The entire CLI as a frozen product type.

    Stored fields: target (module:ClassName string) and json (output format).
    Everything else is derived. Construction IS the program.

    Usage:
        print(ClassifierRun(target="arm_ont.team:Team"))
        print(ClassifierRun(target="arm_ont.team:Team", json_output=True))
    """

    target: str = Field(
        description="Module and class to classify in module:ClassName format, e.g. myapp.models:Order"
    )
    json_output: bool = Field(
        default=False,
        description="True for full JSON tree output, False for indented human-readable text",
    )

    @cached_property
    def model_class(self) -> type[BaseModel]:
        """Phase 5: resolve the target string to a BaseModel class.

        The boundary crossing — string → module → class. importlib and
        getattr are inherently dynamic. This projection contains that
        dynamism inside the model, at the boundary where it belongs.
        """
        module_path, class_name = self.target.rsplit(":", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)  # pyright: ignore[reportAny]

    @cached_property
    def tree(self) -> ModelTree:
        """Phase 5: classify every field on the resolved class."""
        return ModelTree.model_validate(self.model_class)

    @cached_property
    def report(self) -> TreeReport:
        """Phase 5: project the classified tree into a renderable report."""
        return TreeReport.model_validate(self.tree)

    @override
    def __str__(self) -> str:
        """Terminal projection — human text or bot JSON from the same model."""
        if self.json_output:
            return self.report.model_dump_json(indent=2)
        return self.report.text


if __name__ == "__main__":
    import sys

    run = ClassifierRun(
        target=sys.argv[1],
        json_output="--json" in sys.argv,
    )
    print(run)
