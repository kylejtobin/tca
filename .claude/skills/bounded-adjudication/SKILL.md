---
name: bounded-adjudication
description: "Build constitutional review infrastructure for AI-assisted development. Use when the user wants to constrain agent judgment to closed evidence vocabularies, set up code review gates, create review rubrics, add pre/post edit hooks, or establish bounded adjudication for their project. Triggers include: 'bounded adjudication', 'review gates', 'adjudication rubric', 'constrain judgment', 'evidence shapes', 'code review hooks', or any request to formalize architectural standards into enforceable review infrastructure."
license: MIT
compatibility: "Claude Code or any agent with hooks support (PreToolUse/PostToolUse)"
metadata:
  author: kylejtobin
  version: "1.0.0"
---

# Bounded Adjudication

This skill guides the user through building bounded adjudication infrastructure for their project. The output is a hooks configuration and gate rubric that constrain agent judgment to a closed evidence vocabulary.

You are a collaborative instrument. You make the user's understanding precise. You do not do the work autonomously. You ask targeted questions, form hypotheses for the user to confirm or correct, and accumulate understanding in a worksheet.

## Protocol

On every invocation:

1. Check for a worksheet at `.claude/bounded-adjudication-worksheet.md` in the user's project.
2. If no worksheet exists, create one using the template below. Begin at Project Context.
3. If a worksheet exists, parse section statuses. Resume at the first section not marked `[CONFIRMED]`.
4. Work the current section with the user until they confirm it. Mark it `[CONFIRMED]`.
5. When all six question sections are confirmed, run the quality gate.
6. If quality gate passes, generate the artifacts.

### Working with the user

Ask questions. Listen. When the user describes a module, boundary, or pattern, you may examine it in the codebase to form a specific hypothesis. Present the hypothesis for confirmation. Do not scan the codebase unprompted. Do not treat code reading as a substitute for the conversation.

When working on a software project, consult [structural discovery](references/structural-discovery.md) for what signals to listen for and what they mean. When working on creative, editorial, or intentional work, consult [intentional discovery](references/intentional-discovery.md). Most projects use both strategies on different dimensions. A design system is structural. The brand voice it expresses is intentional.

Translate concepts into the user's context. "Evidence shape" means nothing until you show them one from their own project. "A repository class that imports from the HTTP layer" is an evidence shape. "Don't violate separation of concerns" is not.

### Reopening sections

Later work sometimes reveals that an earlier section was wrong. Working through evidence shapes may reveal a gate was actually two gates combined. An approved mechanism analysis may reveal that an invariant is only usually wrong, not always wrong.

When you observe this, name the conflict explicitly. Propose reopening the affected section. Mark it `[REOPENED]` and work it again with the user. Do not reopen without the user's agreement. Do not second-guess confirmed sections without a specific named conflict.

## Worksheet Template

Create this file at `.claude/bounded-adjudication-worksheet.md` on first invocation:

```markdown
# Bounded Adjudication Worksheet

## Project Context [NOT STARTED]

**Project name:**
**What it builds:**
**Primary language/framework:**
**Key architectural commitments:**
**Where does truth live in this project:**

---

## 1. Structural Invariants [NOT STARTED]

Shapes that are always wrong regardless of context. Not usually wrong. Always wrong.

| # | Invariant shape | Why it is always wrong |
|---|----------------|----------------------|

---

## 2. Axes of Judgment [NOT STARTED]

Each gate asks one question about one independent dimension of the work.

| # | Gate name | Question |
|---|----------|----------|

---

## 3. Evidence Shapes [NOT STARTED]

For each gate, the concrete observable shapes that constitute allowed and disallowed work.

### Gate: [name]

**Allowed shapes:**
-

**Disallowed shapes:**
-

---

## 4. Approved Mechanisms [NOT STARTED]

For each gate, the sanctioned ways to achieve goals that would otherwise appear suspicious.

### Gate: [name]

**Mechanisms:**
-

---

## 5. Genuine Ambiguities [NOT STARTED]

Where evidence matching fails to resolve classification.

| # | Ambiguity | Owner |
|---|-----------|-------|

---

## 6. Authority Topology [NOT STARTED]

What is the declared truth against which work is measured?

**Authority root:**
**Ownership map:**

---

## Quality Gate [NOT RUN]

- [ ] Every invariant is a concrete shape, not a principle
- [ ] Every gate asks exactly one question
- [ ] No gate overlaps with another gate
- [ ] All gates together cover the work's dimensions
- [ ] Every evidence shape is observable in an edit
- [ ] Every approved mechanism is specific enough to match against
- [ ] Every ambiguity names an owner
- [ ] Authority topology is consistent with the gates

---

## Generation [NOT RUN]
```

## Section Protocols

### Project Context

Understand what the project is before asking about invariants. Ask the user:
- What does this project build?
- What are the architectural commitments they've already made?
- Where does truth live? (What is the authoritative source that other things derive from?)

If the user points you at code, read it to form hypotheses. "It looks like your domain models live here and your vendor integrations live here. Is that the ownership boundary?" is better than "tell me about your architecture."

### 1. Structural Invariants

These are fast-fail patterns. The pre-check fires them before reasoning is spent. Every invariant must be a shape that is always wrong. Test each candidate: can you name a legitimate case where this shape is correct? If yes, it is not an invariant. It may be a disallowed evidence shape for a gate instead.

### 2. Axes of Judgment

Each gate is one question about one dimension. Test independence: could gate A pass while gate B fails, and vice versa? If not, they are the same gate or one subsumes the other. Test exhaustiveness: is there a dimension of work quality that no gate covers? If yes, a gate is missing.

### 3. Evidence Shapes

For each gate, enumerate what allowed and disallowed work looks like as concrete observable shapes. Not principles. Not aspirations. Shapes an adjudicator can match against an edit.

Test each shape: could a reviewer unambiguously determine whether an edit matches this shape? If the shape requires subjective interpretation, it is too abstract. Sharpen it or split it.

### 4. Approved Mechanisms

For each gate, what are all the ways a suspicious-looking edit can be correct? This closes the solution space. The adjudicator can only pass a suspicious edit by citing one of these.

Test completeness: for each disallowed shape, is there a legitimate way to achieve the same goal? If yes, that way must be an approved mechanism. Test soundness: is every approved mechanism actually correct? An approved mechanism that is itself broken institutionalizes a defect.

### 5. Genuine Ambiguities

Where does evidence matching fail? Where are there legitimate classification disputes? Name each ambiguity and name who or what resolves it. The escalation authority can be a human role, a document, a design decision that hasn't been made yet, or a future conversation.

A system with no ambiguities is lying about its certainty. Push the user to find the edges.

### 6. Authority Topology

What is the declared truth? Everything in the rubric is measured against something. Name it. If multiple authority sources exist, map which gate adjudicates against which authority.

Test consistency: does every gate's evidence reference the authority topology? If a gate's allowed/disallowed shapes don't relate to the declared truth, either the gate or the topology is wrong.

## Quality Gate

Before generating artifacts, review the complete worksheet against these criteria:

1. Every invariant is a concrete shape, not a principle restated as a shape.
2. Every gate asks exactly one question about exactly one dimension.
3. Gates are mutually independent and jointly exhaustive.
4. Every evidence shape is observable: a reviewer can match it against an edit without subjective interpretation.
5. Every approved mechanism is specific enough to cite as justification.
6. Every ambiguity names an owner.
7. Authority topology is consistent with all gates.

If any criterion fails, name the failure, propose reopening the affected section, and work it again with the user. Do not generate artifacts until all criteria pass. Mark the quality gate `[PASSED]` with notes on what was checked.

## Generation

### Hooks Configuration

Generate a hooks configuration to merge into the user's `.claude/settings.json`. If the file already exists, merge the hooks into the existing structure. Do not overwrite other settings.

Structure:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Pre-edit invariant check. DENY if the proposed edit matches any fast-fail pattern below. Otherwise PASS.\n\nFast-fail patterns:\n[numbered list of confirmed invariants from worksheet]\n\nReturn PASS or DENY. On DENY, cite the pattern number and the exact shape that triggered it."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "agent",
            "prompt": "Post-edit gate adjudication. For each gate, consult the rubric at `.claude/rules/gate-rubrics.md`. For each gate:\n\n1. Answer the gate's Question against the edit.\n2. Classify the edit against Allowed and Disallowed evidence shapes.\n3. If the edit matches an Approved Mechanism, the gate PASSES unless a specific Disallowed shape also applies.\n4. FAIL only when you can cite a specific Disallowed shape.\n5. If classification is ambiguous, ESCALATE to the named authority.\n\nGates: [list of gate names from worksheet]\n\nFor each gate return PASS, FAIL, or ESCALATE. On FAIL cite the gate, the disallowed shape, and the approved mechanism alternative if one exists. Overall FAIL if any gate is FAIL."
          }
        ]
      }
    ]
  }
}
```

### Gate Rubric

Generate `.claude/rules/gate-rubrics.md` with this structure:

```markdown
---
paths:
  - "**/*"
---

# Gate Rubrics

## Reading Order

1. Classify mode: [project-specific classification guidance from authority topology]
2. For each gate, answer the stated Question against the edit.
3. Classify against Allowed and Disallowed evidence.
4. If the edit matches an Approved Mechanism, the gate passes unless a specific Disallowed shape also applies.
5. If classification is ambiguous, emit the gate's Escalation Trigger.

## [Gate Name] Gate

**Question**: [from worksheet]

**Allowed evidence**:
[from worksheet]

**Disallowed evidence**:
[from worksheet]

**Approved mechanisms**:
[from worksheet, inline if small catalog]

**Escalation trigger**: [from worksheet ambiguities]
```

If a gate's approved mechanism catalog is substantial (more than five mechanisms), generate a separate file at `.claude/rules/[gate-name]-mechanisms.md` and reference it from the rubric.

Mark the Generation section `[COMPLETE]` when artifacts are written. Tell the user what was generated and where.