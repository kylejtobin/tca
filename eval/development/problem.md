# Error Analysis

## Context
Claude, in Claude Code, writes the example code and code specifications of the `python-dev-tca` skill: the reference other agents copy when they build Type Construction Architecture. The standard is "Construction is the only operation: a step you are about to write is a class you have not named." A good output declares a type for every thing, produces every value by constructing a declared type, and reports exactly what it delivered.

## Trace Sample
This session's transcript. The sample is the deliveries matched by one rule, not a census of every delivery: a delivery is an assistant turn whose code block declares a `BaseModel`, `RootModel` or `StrEnum`, an assistant turn whose text specifies skill classes with their fields or lists changes to skill pages, or a build that writes skill code. A trace is one delivery with the message that delivers it; a build spread over several tool turns is one trace with its report. Skill prose without code, the code-review agent and the eval documents are outside the rule. n = 17, with IDs t01 to t17; each trace's sample is in `eval/development/trace/`, named by its ID.

## Open Codes

| Trace ID | First failure observed |
|---|---|
| t01 | An `execute` that forwards to `self.root.execute()` stands where a settlement type belongs. |
| t02 | `DiscountAbsent` and `NoDiscount` are left undeclared ("Open"). |
| t03 | `DiscountReading`, a class named for a stage of the run, is added between the discount reply and the priced order. |
| t04 | An f-string assembles the discount path in `DiscountRequest.path` where an address type belongs. |
| t05 | `ChargeAnswered.reply` parses its own text with `ChargeReply.model_validate_json(self.text.root)`, a JSON parse made anywhere but an interpreter's `interpret` or the callback in `main.py`. |
| t06 | `ChargeAnswered.reply` parses its own text with `ChargeReply.model_validate_json(self.text.root)`, a JSON parse made anywhere but an interpreter's `interpret` or the callback in `main.py`. |
| t07 | An f-string assembles the discount path where an address type belongs. |
| t08 | The raw `customer.root` string is passed to the client where an address type belongs. |
| t09 | `FieldName` is specified as lowercase, so it cannot construct from real header names such as `Content-Type`. |
| t10 | `FieldName` requires lowercase, so it cannot construct from real header names such as `Content-Type`. |
| t11 | A vendor SDK that does not exist is invented as the dictionary source. |
| t12 | `Whole`, a scalar whose only value is 100, is declared to stand in for a literal, not to name a thing. |
| t13 | `CheckoutRoute.model_validate(await request.json())` cannot construct under strict validation from the decoded dictionary. |
| t14 | The raw `customer.root` string is passed to the client where an address type belongs. |
| t15 | The rule that governs the provider's fixed-width settlement report is named and inhabits no declared construct: the rules paragraph is marked "One decision that is yours". |
| t16 | `SettlementReport.settlement` calls `model_validate_strings` on records from outside the type, in place of the agreed `FixedWidth` core-schema type. |
| t17 | The settlement API (`/settlements`, the `charge` query parameter, `SettlementQuery`) is invented. |

## Failure Modes

### Step in place of a type
- **Definition:** at a hard type, a value is produced by something other than constructing a declared type: a method that dispatches to a variant instead of a union whose construction picks it, string formatting, a JSON parse made anywhere but an interpreter's `interpret` or the callback in `main.py`, or a value handed to a library that was not read from a constructed instance of the type the argument means. A hard type is a type that no construct already declared and no library in the stack produces, or whose input strict validation rejects.
- **Pass/fail criterion:** fail when the delivery produces a value at a hard type without constructing a declared type for it.
- **Fail example:** t04, `return ProviderPath(f"/discounts/{self.customer.root}")`.
- **Pass example:** t14, `CollectionUrl` declared with `root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")` for a provider address.
- **Frequency:** 9 of 17 (t01, t04, t05, t06, t07, t08, t14, t16, t17).
- **Evaluator:** an LLM judge applying the criterion, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Misreport of the delivery
- **Definition:** the delivering message contains a claim phrase while the delivery fails "Step in place of a type". The claim phrases are exactly these five: "built", "in place", "modeled", "no longer pulled raw", "Nothing dispatches".
- **Pass/fail criterion:** fail when the delivering message contains one of the five claim phrases and the delivery fails "Step in place of a type".
- **Fail example:** t14, "The id is no longer pulled raw out of the action." while the client receives `customer.root`.
- **Pass example:** t05, a delivery that fails "Step in place of a type" and whose message contains none of the five claim phrases.
- **Frequency:** 5 of 17 (t01, t04, t14, t16, t17).
- **Evaluator:** a code check for the five claim phrases combined with the "Step in place of a type" label, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Construction fails on real input
- **Definition:** a declared type cannot construct from the input the crossing actually receives.
- **Pass/fail criterion:** fail when the input the transport delivers is rejected by the type declared to receive it.
- **Fail example:** t13, `CheckoutRoute.model_validate(await request.json())`, where strict validation rejects the string `"usd"` for `Currency` and the list for `Lines`.
- **Pass example:** t14, `CollectionUrl`, which accepts the provider address it receives.
- **Frequency:** 3 of 17 (t09, t10, t13).
- **Evaluator:** a code check that constructs each declared type from a recorded real input, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Type without a thing
- **Definition:** a declared type that no thing in the domain inhabits: a type whose fields hold only the types it lies between and add no meaning of its own, or a scalar whose inhabitants are a literal value and not a thing.
- **Pass/fail criterion:** fail when the delivery declares a type whose docstring cannot name a thing in the domain without naming another declared type or a literal value.
- **Fail example:** t03, `DiscountReading` declared between `DiscountOffer` and `PricedOrder`.
- **Pass example:** t14, `CollectionUrl` declared as "The address of a collection another system holds" for a provider address.
- **Frequency:** 2 of 17 (t03, t12).
- **Evaluator:** an LLM judge applying the criterion, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Thing without a type
- **Definition:** a thing in the domain that the delivery names inhabits no declared type: a state, a variant or a rule of the domain has no inhabitant in any type the delivery declares, so the declared types have fewer inhabitants than the domain has states.
- **Pass/fail criterion:** fail when the delivery names a thing in the domain that no declared type in the delivery has as an inhabitant.
- **Fail example:** t02, `DiscountAbsent` and `NoDiscount` left undeclared ("Open").
- **Pass example:** t05, `ChargeReply` declared with `ChargeApproved | ChargeDeclined | ChargeFailed` for each reply the payment provider gives.
- **Frequency:** 2 of 17 (t02, t15).
- **Evaluator:** an LLM judge applying the criterion, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Invented input
- **Definition:** the delivery depends on a library, API or source that does not exist or was never agreed.
- **Pass/fail criterion:** fail when the delivery imports, calls or describes an interface absent from the agreed design and from the real dependency set.
- **Fail example:** t11, "The promotions SDK is a stand-in, invented for the demo".
- **Pass example:** t13, the checkout read through Starlette's documented `request.json()`.
- **Frequency:** 2 of 17 (t11, t17).
- **Evaluator:** a code check that every import resolves in the dependency set, plus a human check of described APIs against the agreed design, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

## Priority
Impact is the share of a mode's traces whose failure reached a commit of the skill. Priority is frequency × impact.

1. Step in place of a type: 9/17 × 2/9 (t04 in `9fcd8fc`, t14 in `523f8c2`) = 0.12; first, because "Misreport of the delivery" is defined on it.
2. Misreport of the delivery: 5/17 × 2/5 (t04, t14) = 0.12.
3. Construction fails on real input: 3/17 × 1/3 (t13 in `523f8c2`) = 0.06.
4. Type without a thing: 2/17 × 1/2 (t03 in `9fcd8fc`) = 0.06.
5. Thing without a type: 2/17 × 1/2 (t02 in `9fcd8fc`) = 0.06.
6. Invented input: 2/17 × 0/2 = 0.
