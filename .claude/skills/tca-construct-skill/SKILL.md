---
name: tca-construct-skill
description: Write or revise TCA construct skills, the cards that classify meanings, declare row grammar, and constrain builders to exact source expansions. MUST be invoked before creating or editing any .claude/skills/tca-construct-*/SKILL.md construct-card file. Replaces generic documentation, tutorial prose, vague examples, and construct advice not tied to row expansion and halt behavior.
---

# TCA construct skill

A TCA construct skill is a closed construction card. It is not documentation about a topic; it is the contract an agent uses to classify a meaning, write a catalog row, expand that row into source, and halt when the construct cannot carry the meaning.

The consumers are fixed:

- `tca-ontology` uses the card to decide whether a meaning belongs to this construct and what row belongs in `<target>/spec/ontology.json`.
- `tca-dev` uses the card to expand a row into source exactly.
- The operator uses the card to judge whether a block is a model error, a builder mismatch, or a missing construct.

## Name

Name the skill for the construct, not the activity.

Use `tca-construct-<construct-name>`, lowercase and hyphenated. Do not use `tca-<construct-name>` for construct cards made with this schema. The name is a dispatch key and should match the construct vocabulary used by agents and catalog rows after the `tca-construct-` prefix.

If one skill covers multiple row constructs, name it for the doctrinal home that owns them.

## Description

The description is the invocation surface. It must contain, in order:

1. What the skill builds.
2. When it MUST be invoked.
3. Which forbidden forms it replaces.

Template:

```yaml
description: Build <construct>, the only legal shape for <meaning>. MUST be invoked before <trigger activity>. Replaces the forbidden forms; if <common procedural smell>, <near miss>, or <wrong abstraction> is about to appear, stop and build <construct> instead.
```

Use trigger words from both sides: the legal construct and the forbidden instincts that should load the card.

## Skill Schema

Write construct-card skills with this exact file shape:

```markdown
---
name: tca-construct-<construct-name>
description: Build <construct>, the only legal shape for <meaning>. MUST be invoked before <trigger activity>. Replaces the forbidden forms; if <common procedural smell>, <near miss>, or <wrong abstraction> is about to appear, stop and build <construct> instead.
---

# <Construct Name>

## Definition

State what the construct is.

## Required Form

State the exact source form the row expands to.

## Sorting Rules

State when this construct applies instead of adjacent constructs.

## Replaced Forms

State the forbidden forms this construct replaces and why each is not this construct.

## Construct-Specific Doctrine (present only when the construct carries one)

State the construct's mechanism that the common sections do not fully capture. Omit this section when the Required Form is the whole doctrine.

## The Row

State the `<target>/spec/ontology.json` row grammar this card expands and show valid row examples.

## Allowed Patterns

List the closed legal rendered forms.

## Forbidden

List forms this construct never permits.

## Halt Rule

State the exact halt condition when a row cannot expand through this card.
```

## Section Rules

`# Construct Name` is the display name of the construct.

`## Definition` pins the construct's domain meaning.

`## Required Form` states the class, field, alias, method, function, config, or file shape the builder may write.

`## Sorting Rules` names adjacent constructs and states the boundary between them.

`## Replaced Forms` names the tempting forbidden forms and states the replacement relation.

`## Construct-Specific Doctrine` is present when the construct carries a mechanism the common sections do not fully capture, such as construction discipline, verb body, capture, wire signal, or failure ordering. It is omitted when the Required Form is the whole doctrine: a section minted with nothing distinct to say is a structure with no meaning, and a section restating the Required Form is one meaning kept in two places.

When a construct needs more than one mechanism, split the slot into multiple named `##` sections between `## Replaced Forms` and `## The Row`, each titled for the mechanism it defines, such as `## Construction Discipline`, `## Verb Body`, `## Capture`, `## Wire Signal`, or `## Failure Ordering`.

Do not use anonymous pre-row prose blocks.

Do not use `###` subsections for construct schema.

Do not use angle-bracket placeholder blocks.

`## The Row` is the boundary between doctrine and catalog grammar. It names every row field the skill owns and shows valid JSON examples.

`## Allowed Patterns` is closed. Do not include preferences, alternatives, or advice whose expansion cannot be judged.

`## Forbidden` contains exact detection cues or denied forms.

`## Halt Rule` states what the builder reports when the row cannot expand through the card.

## Invalid Authoring Forms

- A skill that teaches a style without tying it to catalog rows.
- A description that lacks trigger smells.
- A section that only explains background the agent already knows.
- An example that cannot be filled from a row.
- An allowed pattern that is not enforceable by the card, the gate, or review.
- A construct skill that adds doctrine not derived from the authority, a carried ruling, or a proved substrate behavior.
- Angle-bracket placeholder slots instead of named sections.
- `###` subsections that hide schema content under a generic section.

Build exactly this card shape. If a construct skill needs a section this schema cannot place, report the schema gap instead of adding a new shape.
