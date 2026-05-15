# Bounded Adjudication

[![Agent Skill](https://skills.sh/b/kylejtobin/bounded-adjudication)](https://skills.sh/kylejtobin/bounded-adjudication)

AI coding agents review your work with full reasoning capability and no constraints on what criteria they apply. They can invent a novel objection on any edit. They can wave something through because the context is long and the pattern looks close enough. Their judgment is unbounded. This is the same problem human reviewers have, except it runs on every single write.

Bounded adjudication is three constraints on a reviewer, human or machine.

You can only reject by citing a specific disallowed shape from a closed rubric. You can only approve a suspicious work product by citing a specific approved mechanism from a closed catalog. You can only defer by escalating to a named authority. The reviewer has full reasoning capability and zero legislative power. It interprets. It does not legislate.

## The Machine

Every time a file is written, two things happen.

A pre-check fires against a small set of structural invariants. Shapes that are always wrong regardless of context. Match any pattern, the write is rejected before reasoning is spent. This is not adjudication. This is cost optimization.

A post-check agent reads what was written and evaluates each gate in the rubric. Each gate asks one question about one dimension of the work. For each gate, the agent classifies the work against the closed evidence catalog: allowed shapes, disallowed shapes, approved mechanisms. It returns pass, fail, or escalate. It cannot introduce criteria that are not in the rubric. It cannot waive failures that are not covered by an approved mechanism. When classification is ambiguous, it names the authority that owns the ambiguity and routes to it.

That is the entire machine. The reference implementation uses Claude Code hooks. The pattern works anywhere an agent's judgment can be bounded at write time.

## Vocabulary

A **gate** is a single question about a single dimension of the work.

A **rubric** is a closed set of observable evidence shapes, allowed and disallowed, organized by gate.

An **approved mechanism catalog** is a closed set of sanctioned ways to achieve goals that would otherwise appear suspicious.

An **escalation authority** is a named entity that owns an ambiguity the reviewer cannot resolve.

## Instantiation

Building bounded adjudication for a specific project is domain analysis. The hard part is not writing hooks or rubrics. The hard part is knowing what they should say. Six questions, answered in order, each depending on the one before it.

**Structural invariants.** What shapes are always wrong? Not usually wrong. Always wrong. These become the pre-check patterns.

**Axes of judgment.** What independent dimensions does the work have? Each becomes a gate. One question per gate. The set must be jointly exhaustive and mutually independent.

**Evidence shapes.** For each gate, what are the concrete observable shapes that constitute allowed and disallowed work? Principles are not shapes. "Don't violate separation of concerns" is a principle. "A world concept placed under a vendor path because the current caller imports from there" is a shape. The translation from principle to shape is where domain expertise lives.

**Approved mechanisms.** For each suspicious shape, what are all the sanctioned ways to do it correctly? This closes the solution space. A missing mechanism blocks legitimate work. A broken mechanism institutionalizes a defect.

**Genuine ambiguities.** Where does evidence matching fail to resolve classification? Name the ambiguity. Name who owns it. A system that never escalates is lying about its certainty.

**Authority topology.** What is the declared truth against which work is measured? A schema. A spec. A story bible. A graph. Wrong authority topology means the entire system adjudicates against the wrong standard.

## The Skill

This repository is an installable [Agent Skill](https://agentskills.io) following the [open specification](https://agentskills.io/specification). It guides you through the six questions, building a worksheet collaboratively as you go. The agent reads your code in service of the conversation, forming hypotheses about your project's structural commitments for you to confirm or correct. You drive what gets examined. The agent makes your understanding precise.

When the worksheet is complete and passes a quality gate, the skill generates your hooks configuration and gate rubric directly into your project's `.claude/` directory.

Two discovery references ship with the skill. **Structural discovery** covers projects where the artifact itself carries structural information: import direction, module boundaries, type signatures, existing linter and CI configurations. **Intentional discovery** covers projects where structural information lives in the author's stated commitments: voice, conventions, rules, genre. Most projects need both.

## Installation

### As a plugin

```
/plugin install bounded-adjudication
```

### As a project skill

```
git clone https://github.com/kylejtobin/bounded-adjudication .claude/skills/bounded-adjudication
```

To ensure continuity across sessions, add a reference in your project's `CLAUDE.md`:

```
Bounded adjudication setup is in progress. Consult .claude/skills/bounded-adjudication/ and check the worksheet for current state.
```

## License

MIT