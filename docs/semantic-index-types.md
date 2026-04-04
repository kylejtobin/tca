# Semantic Index Types

TCA does not require an LLM consumer. The [building block classifier](building-block-classifier.md) demonstrates a complete TCA program with no LLM anywhere. TCA is valuable whenever programs benefit from construction-as-proof, composition through types, and derivation owned by the objects that hold the data.

But something changes when the consumer of a type schema is a language model. Names cross from the routing plane to the computation plane. Field names become instructions. Descriptions become program text. Renaming becomes refactoring. This is not a side effect of using LLMs with schemas — it is a structural consequence of the compilation target reading natural language.

This document covers what semantic indexing means for TCA programs. The full formal treatment — definition, two-channel formalization, information-theoretic bound, empirical foundations, security implications — lives in the companion **[Semantic Index Types](https://github.com/kylejtobin/sit)** project.

---

## Why SIT Belongs In TCA

Pydantic preserves field names and descriptions through `model_json_schema()` because Samuel Colvin kept them in JSON serialization for APIs. That design decision, made for human-readable APIs, turned Pydantic into the foundation for LLM structured output. And it revealed a phenomenon: the names that programmers write for readability become instructions that the model follows.

This is not an accident that needs a new explanation. It is the direct consequence of TCA's preserved semantic surfaces being compiled for a consumer that reads natural language. Every TCA program already has a semantic surface — field names, enum labels, descriptions, projection names. When that surface is consumed by a neural interpreter, the naming discipline that TCA already prescribes becomes an execution discipline.

---

## The Core Phenomenon

Rename `churn_risk_tier` to `x7` and the construction machine behaves identically, but the LLM produces different, worse output. The type constrains what the model can output structurally. The names guide what it outputs semantically.

> A **Semantic Index Type** is a type declaration in which natural-language tokens (field names, docstrings, enum member names) function as computational indices that constrain the semantic content of generated values, because the consumer of the type interprets those tokens as natural-language instructions rather than as structurally inert identifiers.

In a conventional type system, a field name is an address: it indexes into a structure to locate a slot. In a semantic index type, the field name is simultaneously a semantic key: it indexes into the consumer's learned language associations to locate a meaning. `churn_risk_tier` addresses a slot in a product type AND instructs the consumer to assess voluntary customer departure risk.

Alpha equivalence breaks at the consumer level: renaming changes the output because the compilation target reads names.

---

## Two Channels, One Declaration

A semantic index type operates through two reinforcing channels:

The **structural channel** (type annotations, validators, constrained decoding) bounds the space of valid outputs. These provide hard guarantees: the consumer cannot produce values that violate the schema. Enforced mechanically.

The **semantic channel** (field names, descriptions, enum labels) determines the conditional probabilities within that bounded space. Which valid value the consumer selects depends on the linguistic content. Compliance depends on the precision of the language, the capability of the consumer, and the degree to which structural constraints have already narrowed the space.

Structure defines admissibility. Semantics defines salience. The schema is one declaration with split operational semantics — not "prompt plus validation."

---

## Structural Compression And Semantic Bandwidth

The information bound makes the relationship precise:

> `I(N; Yf) <= H(Yf) <= log2|Vf|`

Tighter types (smaller |Vf|) leave less room for the name to matter. A 4-member enum has at most ~2 bits of semantic influence. A bare `str` field has unbounded entropy — the name must do all the work.

| Type constraint | Valid outputs | Max semantic influence |
|:---|---:|---:|
| `bool` | 2 | 1 bit |
| 4-member enum | 4 | 2 bits |
| unconstrained `str` | unbounded | unbounded |

Every TCA principle that tightens the type — domain-typed fields, enum-first classification, constrained primitives — simultaneously tightens the information bound on the LLM. The structural discipline and the semantic discipline converge.

---

## Compilation Surfaces

How the schema reaches the consumer matters. These are different compilation regimes with different properties for each channel:

**Schema-as-text.** The schema is serialized as natural language in the prompt. Maximum semantic indexing, maximum attack surface.

**Schema-as-tool-definition.** The schema is passed via a structured API channel (function calling, tool use). Linguistic content remains available but structurally separated from conversational context.

**Schema-as-hard-constraint.** The schema is compiled into a decoding grammar that mechanically constrains token generation. Structure enforced during generation; semantic channel still operates.

**Post-generation validation.** The model generates output, `model_validate` attempts construction, and failures retry. Structural guarantees are eventual, not generative.

Choosing the wrong surface is compiling the program incorrectly for the neural interpreter. A context that should be carried as a structured tool definition but is instead pasted as prompt text changes the compilation regime and therefore the execution behavior. This is a design error, not a prompting inconvenience.

---

## The Whole Program As Semantic Surface

In an agentic system, semantic indexing extends far beyond output schemas. The neural consumer reads everything it is given as natural language:

- **Tool names** tell the model which capability to invoke
- **Parameter names** tell the model what each argument means
- **Skill names and descriptions** frame what the agent can do
- **Prompt sections** structure the model's reasoning
- **Context reinjection paths** determine how prior knowledge reaches the model
- **Command choices** affect what information surfaces next

All of these are semantic index surfaces consumed by a neural interpreter. A poorly named tool, an imprecise parameter description, or context reinjected through the wrong channel is a weak program — structurally valid, semantically wrong.

The implication is that TCA's modeling discipline applies to the entire exposure surface, not just to Pydantic schemas. Precise names, precise contracts, tighter types, and carefully chosen compilation surfaces are architectural requirements for any system where a neural consumer is part of the execution.

---

## Design Consequences For TCA Programs

If names are computation and the whole program is a semantic surface, then:

- **Naming is programming.** Choosing `churn_risk_tier` over `attrition_risk_tier` is choosing between analytical framings. The field name is an instruction.
- **Descriptions are program text.** A `Field(description=...)` that says "Projected total revenue across the full customer relationship, not historical sum" narrows the consumer from a broad concept to a specific calculation. Removing it changes the output distribution.
- **Renaming is refactoring.** In conventional programming, renaming is safe and mechanical. With neural consumers, renaming changes what the consumer computes.
- **Progressive hardening applies to semantic surfaces too.** Start with precise names. Observe where the model fails. Harden those failures into structural guarantees — tighter types, constrained primitives, enums.

Type declarations generate the schema via `model_json_schema()`. The schema instructs the LLM. The LLM's output feeds `model_validate`. Construction proves the result. The proven object can trigger further construction (orchestration), which may involve another LLM call with a more focused type. Build the box out of types. Narrow it until only valid outputs remain. Field names and descriptions are the gravity inside that box.

---

## Handoff To The Formal Treatment

This document covers the architectural consequences of semantic indexing for TCA programs. The full formal treatment lives in the **[Semantic Index Types](https://github.com/kylejtobin/sit)** project: the definition, the two-channel formalization, the information-theoretic bound, empirical foundations from three research communities, compilation regimes, security implications (adversarial indexing), and the companion experiment design.
