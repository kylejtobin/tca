# TCA Product Definition

**Status:** Target product definition  
**Owner:** Kyle Tobin  
**Date:** October 31, 2026

## 1. Product definition

TCA is a declarative, event-driven backend application framework for developers building business applications with rules, decisions, and external interactions. Developers name and compose business types and framework-provided application constructs into one executable application model.

Each supplied construct defines its supported behavior. Developers specialize its types, constraints, and relationships to express their application. They do not author handlers, startup orchestration, or a separate workflow describing how those constructs execute.

An event establishes that information was received, work was requested, or a result was produced. Declared relationships determine which activity it activates and what that activity requires. Established results can activate subsequent work. The application can perform immediate work, await additional evidence, and continue across interruptions.

Business meaning is commonly distributed across validation models, service methods, integration code, transport schemas, and documentation. TCA makes the composed application model authoritative for its business definitions and relationships, reducing the representations developers must reconcile when making a change.

The primary customer is a developer building and maintaining business applications. Operators, integrators, reviewers, and coding agents use the same declared concepts to understand and inspect their behavior.

## 2. Goals and success measures

| Goal | How success is evaluated |
|---|---|
| **Author complete applications through models** | Representative applications declare inputs, activities, outcomes, configuration requirements, and integrations without application-authored execution procedures. |
| **Make business changes easier** | A change is made at its authoritative declaration without repeating business meaning in orchestration, interface, or transport code. |
| **Make execution trustworthy** | Work follows declared demand, evidence, authority, and policy; delayed evidence and recovery preserve the meaning of the intended work. |
| **Make behavior understandable** | Developers can read declarations and explain activation, prerequisites, possible results, and waiting. Runtime explanations identify those same named components and their evidence. |
| **Make the framework practical to adopt** | Developers complete representative tasks using familiar modeling, documentation, and examples without studying framework implementation. |

Evaluation uses working applications, observed developer tasks, and behavioral tests. Measure authoring and change effort, required knowledge, and correctness of developers' explanations. Code volume alone is insufficient; a configuration that encodes an execution algorithm does not meet the authoring goal.

## 3. Assumptions

- Developers building rule-rich applications benefit from explicit business relationships and an understandable event-driven execution model.
- Python and Pydantic provide a familiar and expressive modeling foundation.
- A bounded vocabulary of composable values, events, activities, operations, policies, and capabilities can cover substantial business behavior.
- Consistent composition and declaration-specific feedback make the vocabulary learnable and repay the effort through easier changes and stronger feedback.
- Coding agents benefit from explicit relationships and observable acceptance criteria while remaining subject to the same review as human authors.
- Useful integration and extension paths let developers adopt capabilities without depending on framework maintainers to supply every provider.

Vocabulary coverage and usability are tested through representative applications and developer use. Supporting arbitrary Python programming is not the coverage objective.

## 4. Developer scenarios and requirements

| Scenario | Required capability and observable acceptance |
|---|---|
| **Model a business decision** | A developer composes typed values, supported computations, conditions, and alternatives. Supplied evidence produces the appropriate outcome, with invalid and unresolved cases explained separately. |
| **Activate work from an event** | A developer declares an event and its activity relationship. Received information or an established result activates the intended work without an application handler. |
| **Perform an operation conditionally** | A developer selects the operation and declares its prerequisites. It remains withheld until justified; work needed to obtain evidence can proceed alongside independently justified work. |
| **Use an external capability** | A developer composes a supplied integration with typed requests, possible reports, and business-subject relationships. Immediate and delayed reports satisfy the same requirements. Provider acknowledgement and business completion remain distinct. |
| **Continue work over time** | An application waits and resumes without keeping the initiating connection or process alive. Necessary request information and completed work remain accounted for; uncertain external outcomes follow the capability's recovery contract. |
| **Work with collections and repeated operations** | Equal-valued items and repeated operations remain distinguishable where required. Individual work progresses as evidence arrives; conclusions requiring complete membership wait for its declared completion. |
| **Configure and run an application** | A developer declares typed configuration and resource requirements, starts a minimally configured application, and adds behavior through model composition without writing startup or handler code. Deployment supplies values; invalid required configuration prevents dependent activity. Changing deployment values or supported configuration sources does not require rewriting business behavior. |
| **Expose different interfaces** | Direct calls, CLI access, APIs, and event delivery use the same business definitions and declared activity. Input conventions do not create competing business rules. |
| **Diagnose and evolve an application** | Developers inspect triggering events, consumed evidence, outcomes, outstanding requirements, refusals, and operational failures using the names they authored. Changes do not silently reinterpret existing work. |

A business condition that does not hold, invalid information, missing evidence, and operational failure remain distinct across these scenarios.

## 5. Developer experience

Developers begin with business concepts and use supplied constructs to name events, compose activities, select capabilities, and declare application-specific relationships. Business values and application constructs follow one consistent typed modeling discipline. Event-driven behavior is visible in those declarations.

For example, an order-fulfillment application names payment confirmation, the evidence shipment requires, the shipping capability, and the fulfillment outcome. The developer declares their relationship once. The selected constructs already define how to receive confirmation, withhold unjustified shipment, and continue when evidence arrives.

Types and composition determine relationships wherever possible. Developers provide information that cannot be inferred: trusted sources, occurrence identity, business-subject relationships, prerequisites, and meaningful evidence-selection or completion policies. They do not repeat delivery, continuation, or enforcement mechanisms already supplied by the constructs.

Names identify application components, types define their contracts, and composition defines their relationships. Development feedback points to the relevant declaration and explains missing relationships or invalid constructions. Runtime explanations use those same names to show what happened, why work was justified, and what could advance an unresolved outcome.

Consuming an integration means importing and composing its supplied constructs. Framework and extension authors implement reusable computations and provider protocols with explicit typed contracts. Application developers select and compose that behavior without implementing execution procedure.

Public examples show complete, recognizable applications and their observable behavior. A developer can explain both what must be authored and the consequences of those declarations.

## 6. Scope and exclusions

| Responsibility | Owner |
|---|---|
| Accurate business concepts, outcomes, application composition, and application-specific policy choices | Application developer |
| Reusable construct semantics and their execution guarantees | TCA and extension authors |
| Native execution of declarations, evidence handling, justified work, and continuation | TCA through its supported infrastructure |
| Consistent interface projections and explanations using declared application concepts | TCA and relevant integrations |
| Reusable computations and provider protocol implementations | Framework and extension authors |
| Deployment values, credentials, infrastructure, and permission grants | Deployment operator |
| Authoritative external data, resource constraints, and provider guarantees | The systems that own those resources |

TCA supports durable event-driven application execution through established infrastructure. External business-data storage can vary without implying interchangeable execution infrastructure.

TCA does not establish that business requirements are correct, make arbitrary external operations universally exactly-once, or replace authorization and concurrency controls at protected resources.

The initial focus is developer-authored backend applications with meaningful business rules and external interactions. Business-user rule editors, frontend development, and specialized analytical processing are outside the initial scope.

## 7. Open questions

- Which representative applications best demonstrate value and expose gaps in vocabulary coverage?
- What is the smallest useful adoption unit: a new application, one capability within an existing application, or both?
- Which reusable capabilities must be supplied initially, and what extension experience makes additional providers practical?
- Which declaration conventions make event relationships and policy choices easiest to understand with the least authoring effort?
- What baseline tasks and measurements establish reduced effort and better understanding compared with conventional development?

Model-only composition and an understandable event-driven execution model are product requirements. Exact Python declaration syntax and native realization belong in the authoring and architecture specifications.
