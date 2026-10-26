# TCA Product Definition

**Status:** Target product definition  
**Owner:** Kyle Tobin  
**Date:** October 26, 2026

## 1. Product definition

TCA is a declarative backend application framework for developers building business applications with rules, decisions, and external interactions. Developers describe business values, their relationships, the evidence required for action, and the outcomes they want to produce. TCA derives execution from those declarations.

Its central promise is that **the business model is the executable program**. Developers do not maintain a separate procedural workflow to restate dependencies and decisions already expressed in that model.

Today, business meaning is often distributed across validation models, service methods, integration code, transport schemas, and documentation. A change requires developers to find and reconcile those representations. Types describe the inputs and outputs, while much of the behavior connecting them remains separately authored.

TCA brings that behavior into the declared model. The same application can perform immediate work, await external evidence, and continue across interruptions. Developers retain responsibility for the accuracy of their business model; the framework takes responsibility for interpreting and executing its declared relationships.

The primary customer is a developer building and maintaining business applications. Operators, integrators, reviewers, and coding agents benefit from the same explicit model and explanations of its behavior.

## 2. Goals and success measures

| Goal | How success is evaluated |
|---|---|
| **Reduce duplicated business logic** | Representative applications express rules and dependencies without maintaining equivalent orchestration or transport-specific business logic. |
| **Make business changes easier** | Developers can add or change a rule, outcome, or integration without tracing the same meaning through multiple application layers. |
| **Make execution trustworthy** | Observable operations follow declared demand and prerequisites; delayed evidence and recovery preserve the meaning of the intended work. |
| **Make behavior understandable** | Developers and operators can determine why work occurred, what evidence supported it, and what is preventing progress. |
| **Make the framework practical to adopt** | Developers can build and extend representative applications using the public vocabulary, documentation, and examples without studying engine internals. |

Evaluation uses working applications, observed developer tasks, and behavioral tests. Code volume alone is insufficient: a shorter program must also be understandable, correct, and maintainable.

## 3. Assumptions

- Developers building rule-rich applications benefit from expressing business relationships explicitly rather than maintaining their procedural coordination.
- Python and Pydantic provide a familiar and expressive foundation for the intended audience.
- A reusable vocabulary of values, computations, conditions, selections, and external capabilities can cover substantial business behavior without application-specific engine changes.
- The effort of learning declarative modeling is repaid through easier changes, stronger feedback, and reduced coordination code.
- Coding agents benefit from explicit relationships and observable acceptance criteria, while remaining subject to the same validation and review as human authors.
- Adoption requires useful integration and extension paths; developers cannot depend on the framework’s maintainers to supply every external capability.

These assumptions are tested through representative applications and developer use.

## 4. Developer scenarios and requirements

| Scenario | Required capability and observable acceptance |
|---|---|
| **Model a business decision** | A developer expresses relevant values, computations, conditions, and possible outcomes. The application produces the appropriate outcome from supplied evidence and explains invalid or unresolved cases. |
| **Perform an operation conditionally** | A developer declares what must be established before an operation is pursued. The operation remains withheld until those prerequisites hold; work needed to obtain the evidence can proceed, alongside independently justified work. |
| **Use an external capability** | A developer declares what is requested, what the source may report, and how the report relates to the intended business subject. Immediate and delayed reports satisfy the same business requirements. An acknowledgement does not masquerade as a completed result. |
| **Continue work over time** | An application can wait without retaining its initiating request and resume after interruption. Previously completed operations remain accounted for; uncertain outcomes are handled according to the capability’s recovery contract. |
| **Work with collections and repeated operations** | Equal-valued items and repeated operations remain distinguishable where the business requires it. Individual work can progress as evidence arrives, while conclusions requiring a complete collection wait for its declared completion. |
| **Expose the application through different interfaces** | Direct calls, command-line access, APIs, and event delivery use the same business definitions. Interface-specific input conventions do not introduce competing business rules. |
| **Diagnose and evolve an application** | Developers can inspect outcomes, outstanding evidence, refusals, and operational failures in business terms. Changes to an application do not silently reinterpret work already in progress. |

Across these scenarios, TCA preserves the distinction between a business condition that does not hold, invalid information, missing evidence, and an operational failure. Those differences remain visible wherever the application is used.

## 5. Developer experience

A developer begins with the business: what exists, what makes it valid, what follows from it, which external capabilities participate, and which outcomes the application offers. Reusable vocabulary handles common computations and relationships.

For example, an order-fulfillment application describes the order, the payment evidence required for shipment, the shipping capability, and the intended fulfillment outcome. Payment may be confirmed immediately or reported later. The developer expresses the dependency once; TCA manages when the shipment becomes justified and how execution continues.

Developers declare information that cannot be inferred, including trusted sources, relationships between reported evidence and business subjects, prerequisites for action, and completion conditions. TCA supplies execution coordination without requiring a second account of the business process.

During development, feedback identifies missing or ambiguous relationships and invalid constructions using the application’s own concepts. During execution, developers can inspect what was established, what was attempted, what remains unknown, and what could advance the outcome.

New business behavior is composed from existing capabilities where possible. New reusable computations and integrations can be implemented through explicit extension boundaries without modifying the generic engine.

Public examples should demonstrate complete, recognizable applications. A developer should be able to understand both what the application means and what they must author to build it.

## 6. Scope and exclusions

| Responsibility | Owner |
|---|---|
| Accurate business concepts, rules, intended outcomes, and prerequisites | Application developer |
| Declared external sources, subject relationships, and capability policies | Application developer, using the relevant integration contracts |
| Interpretation of declarations, evidence handling, justified execution, progress, and continuation | TCA |
| Consistent interface projections and explanations of application behavior | TCA |
| Reusable value operations and external integrations | Framework and extension authors |
| Authoritative storage constraints, external permissions, and provider guarantees | The systems that own those resources |

TCA supports durable application execution while allowing established infrastructure to supply persistence and scheduling. It does not require applications to adopt one business-data storage model.

TCA does not establish that a developer’s business requirements are correct, make arbitrary external operations universally exactly-once, or replace authorization and concurrency controls at protected resources.

The initial focus is developer-authored backend applications with meaningful business rules and external interactions. Business-user rule editors, frontend development, and specialized analytical processing are outside the initial product scope.

## 7. Open questions

- Which small set of representative applications best demonstrates the product’s value and exposes gaps in its modeling vocabulary?
- What is the smallest useful adoption unit: a new application, one business capability within an existing application, or both?
- Which reusable capabilities must be supplied initially, and what extension experience makes additional capabilities practical?
- What public declaration conventions make source relationships and conditional behavior easiest to understand without unnecessary ceremony?
- What baseline developer tasks and measurements will establish that TCA reduces effort and improves understanding compared with conventional application development?
