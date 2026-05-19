---
name: forge-the-link
description: "When you reach for procedure to bridge two typed shapes, stop. Trace the construction graph. The link is either already there or one `@cached_property` away — never an f-string, never a helper function, never a mapper class."
license: MIT
compatibility: "Any TCA project using Pydantic v2 frozen models"
metadata:
  author: kylejtobin
  version: "1.0.0"
---

# Forge The Link

This skill IS the diagnostic that fires at the moment of procedural reach. The output is one of three answers: (a) the derivation already exists, use it; (b) the link is one `@cached_property` (or smart variant method, or composed model) away, forge it; (c) the shapes don't compose — there's a model missing, design it via `/proof-design` first.

## The Rule

**Before writing any code whose purpose is converting, translating, formatting, or otherwise bridging two typed shapes — trace the construction graph. The link is already there, or it is one derivation away. Procedure to bridge typed shapes is *escaped derivation* or *contract-surface erasure* in disguise.**

## Activation Scope

This skill MUST fire when:

- You are about to write a function whose purpose is converting one typed model into another typed shape (mapper, translator, adapter, normalizer, formatter).
- You are about to write an f-string assembling a structured value — a subject, channel, topic, key prefix, URI, identifier — from typed components.
- You need a value that "feels" like it should be derivable from existing fields, and the obvious move is a helper function or a `getattr` / `dict` access.
- A `Literal` value on one model needs to become a related value on another (e.g. `Literal["foo"]` on a publish model → `"foo.*"` on a stream subscription).
- You are about to write `if x.kind == "...": extract_y(x)` against a discriminated-union variant.
- You're touching the boundary between two contexts (publisher → subscriber, request → response, event → projection) and reaching for translation code.
- The user invokes `/forge-the-link` or says "trace the graph".

The trigger is *felt friction* — the moment the LLM senses "this is going to be a few lines of glue." That friction is the signal. The glue is the smell.

## Protocol

Six diagnostic questions, in order. The first "yes" names the answer; the first procedural drop names the forge target.

### 1. Inventory the graph

Name the models in play. For each: fields, types, unions, enums, Literals, existing derivations. The inventory is the search space, and the search cannot complete without it.

- What models compose what?
- What unions exist? What variants? What discriminator field?
- What `Literal` or `StrEnum` values carry knowledge — closed vocabularies the consumer is meant to dispatch on?
- What `@cached_property` / `@computed_field` derivations already exist?

### 2. Locate the source

Where is the value you start from already typed?

- A field on a frozen model? Name it.
- An enum variant? A `Literal` discriminator?
- A narrowed scalar? Trace its `Field()` constraint.

If the source isn't already typed, the bridge isn't the problem — the type system is. Stop here and forge the source type first.

### 3. Locate the destination

Where does the consumer expect the answer?

- A field on a different model? An external API contract? A method parameter?
- Is the destination type already declared, or are you about to invent it inline as `str` / `dict` / `tuple[str, ...]`?

If the destination isn't a named type, name it. Inventing it inline is contract-surface erasure.

### 4. Trace the path

Walk leaves → root. What composition / derivation chain connects source to destination?

- Is the destination already a `@cached_property` somewhere upstream?
- Is one model already composing the other?
- Does `from_attributes=True` plus `Field(alias=...)` cover the gap?
- Does a smart variant method on the source DU already produce the destination type?

If the chain exists, **use it**. Stop. The answer is already typed; reach for it directly.

### 5. Test for procedural drop

At any step in the trace, does the chain drop into procedure?

- F-string concatenation of typed fields → that step is the smell.
- `isinstance` extraction from a DU variant → smart variant method missing.
- `dict.get()` reads on model fields → field type or alias missing.
- Mapper function copying fields A→B → composed model missing.
- `getattr(x, "...")` on a typed object → the attribute should be a typed field, not a stringly-named lookup.

Each procedural drop is a *forgeable link*. The exact step where procedure intrudes is the exact place to forge.

### 6. Forge the link

The missing step is one of these shapes:

- **`@cached_property` on the source model** — derives the destination value from the source's own fields. Source's existence proves the derivation.
- **`@computed_field` + `@cached_property`** — same, but the derivation serializes to wire shape.
- **Smart variant method (B.3)** — when the source is a DU variant, the method lives on each variant and produces the destination. F-test governs.
- **Smart enum method (B.2)** — when the source is an enum value, the method takes the enum self plus proven inputs. F-test governs.
- **Composed model with `from_attributes=True`** — when the destination is a new model that reads attributes from the source.
- **`Field(alias="source_name")`** — when the gap is a pure field rename across a boundary.

Forge exactly one link. If forging one link still leaves a procedural step in the chain, recurse on the remaining step. The construction cascade composes; each forged link unlocks the next.

## Examples

**Literal → wildcard subject:**
```python
# WRONG: procedural glue
stream_subject = f"{publish.kind}.*"

# RIGHT: forged derivation
class Subject(BaseModel, frozen=True):
    base: SubjectBase  # narrowed scalar — the publish discriminator lifted

    @computed_field
    @cached_property
    def wildcard(self) -> str:
        return f"{self.base.root}.*"

# Caller reads publish.subject.wildcard — the derivation produces the value,
# the type system holds the knowledge end to end.
```

**DU variant → extracted payload:**
```python
# WRONG: re-branching on .kind
if event.kind == "created":
    target = event.target_path

# RIGHT: smart variant method (B.3)
class CreatedEvent(BaseModel, frozen=True):
    kind: Literal["created"] = "created"
    target_path: FilePath

    def affected_paths(self) -> tuple[FilePath, ...]:
        return (self.target_path,)

# Caller: result.affected_paths() — the variant dispatches itself,
# Pydantic's discriminator has already narrowed the type.
```

**Cross-model rename:**
```python
# WRONG: mapper function
def to_request(edit: Edit) -> EditRequest:
    return EditRequest(edit_id=edit.id, target=edit.path)

# RIGHT: from_attributes + alias
class EditRequest(BaseModel, frozen=True, from_attributes=True):
    edit_id: EditId = Field(alias="id")
    target: FilePath = Field(alias="path")

# Caller: EditRequest.model_validate(edit) — Pydantic constructs it,
# the rename is a declaration, not procedure.
```

**Helper function that should be a derivation:**
```python
# WRONG: free function reading model state
def render_summary(node: ClassifiedNode) -> str:
    return f"{node.field_name}: {node.block.value}"

# RIGHT: derivation on the model
class ClassifiedNode(BaseModel, frozen=True):
    field_name: FieldName
    block: Block

    @cached_property
    def summary(self) -> str:
        return f"{self.field_name.root}: {self.block.value}"

# The summary is intrinsic — its home is the model.
```

## What This Prevents

- F-string assembly of structured values that should be typed derivations.
- Mapper / translator / adapter / normalizer functions that should be `model_validate(other, from_attributes=True)` or composed models with aliases.
- Helper functions reading model fields to compute "intrinsic" values — escaped `@cached_property` derivations.
- `isinstance` extraction from DU variants — the smart variant method already exists or needs forging.
- `if x.kind == "...":` re-branching against a discriminator Pydantic has already narrowed.
- "It's just a string concat" — the moment of greatest procedural temptation, when the link is most forgeable.
- `getattr` / `dict.get()` reads on model fields where `Field(alias=...)` or a composed model would carry the value structurally.
- **Knowledge narrowing or loss between leaves and root** — when a `Literal` at the leaf carries `"foo"` and the consumer at the root receives `str`, the type system silently lost the knowledge somewhere in between. The trace finds where. The forge restores it.

## Reference

- CLAUDE.md — Proof Hierarchies (B), F-Test, Two Smart-Method Patterns, Wrong → Right.
- `.claude/rules/evaluation-model.md` — derivation home for composed-input decisions.
- `.claude/skills/proof-design/SKILL.md` — classify before forging.
- `.claude/skills/shape-match/SKILL.md` — the file's shape determines the forge target.
