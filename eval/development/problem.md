# Error Analysis

## Context
Claude, in Claude Code, writes the example code and code specifications of the `python-dev-tca` skill: the reference other agents copy when they build Type Construction Architecture. The standard is "Construction is the only operation: a step you are about to write is a class you have not named." A good output declares a type for every thing, produces every value by constructing a declared type, and reports exactly what it delivered.

## Trace Sample
This session's transcript. The sample is the deliveries matched by one rule, not a census of every delivery: a delivery is an assistant turn whose code block declares a `BaseModel`, `RootModel` or `StrEnum`, an assistant turn whose text specifies skill classes with their fields or lists changes to skill pages, or a build that writes skill code. A trace is one delivery with the message that delivers it; a build spread over several tool turns is one trace with its report. Skill prose without code, the code-review agent and the eval documents are outside the rule. n = 18.

## Open Codes

| Trace ID | First failure observed |
|---|---|
| Turn 39 | An `execute` that forwards to `self.root.execute()` stands where a settlement type belongs. |
| Turn 53 | `DiscountAbsent` and `NoDiscount` are left undeclared ("Open"). |
| Turn 59 | `DiscountReading`, a class named for a stage of the run, is added between the discount reply and the priced order. |
| Turns 62–90 | An f-string assembles the discount path in `DiscountRequest.path` (turn 71) where an address type belongs. |
| Turn 161 | `ChargeAnswered.reply` parses its own text with `ChargeReply.model_validate_json(self.text.root)`, a parse call made by a class other than the type parsed. |
| Turn 173 | `ChargeAnswered.reply` parses its own text with `ChargeReply.model_validate_json(self.text.root)`, a parse call made by a class other than the type parsed. |
| Turn 187 | An f-string assembles the discount path where an address type belongs. |
| Turn 241 | The raw `customer.root` string is passed to the client where an address type belongs. |
| Turn 255 | `NoPassword` is declared to fill an argument of `httpx.BasicAuth`, not to name a thing in the provider's domain. |
| Turn 281 | `FieldName` is specified as lowercase, so it cannot construct from real header names such as `Content-Type`. |
| Turn 289 | `FieldName` requires lowercase, so it cannot construct from real header names such as `Content-Type`. |
| Turn 319 | A vendor SDK that does not exist is invented as the dictionary source. |
| Turn 323 | `Whole`, a scalar whose only value is 100, is declared to stand in for a literal, not to name a thing. |
| Turns 352–373 | `CheckoutRoute.model_validate(await request.json())` cannot construct under strict validation from the decoded dictionary. |
| Turn 380 | The raw `customer.root` string is passed to the client where an address type belongs. |
| Turn 387 | The decision on the rules paragraph is handed back: "One decision that is yours". |
| Turns 417–422 | `SettlementReport.settlement` calls `model_validate_strings` on records from outside the type, in place of the agreed `FixedWidth` core-schema type. |
| Turns 431–436 | The settlement API (`/settlements`, the `charge` query parameter, `SettlementQuery`) is invented. |

## Failure Modes

### Step in place of a type
- **Definition:** at a hard type, a value is produced by something other than constructing a declared type: an `execute` that forwards to another object's `execute`, string formatting, a parse call made by a class other than the type parsed, or the root of one type passed where another type's value is meant. A hard type is a type that no construct already declared and no library in the stack produces, or whose input strict validation rejects.
- **Pass/fail criterion:** fail when the delivery produces a value at a hard type without constructing a declared type for it.
- **Fail example:** Turn 71, `return ProviderPath(f"/discounts/{self.customer.root}")`.
- **Pass example:** Turn 380, `CollectionUrl` declared with `root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")` for a provider address.
- **Frequency:** 9 of 18 (turns 39, 62–90, 161, 173, 187, 241, 380, 417–422, 431–436).
- **Evaluator:** an LLM judge applying the criterion, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Misreport of the delivery
- **Definition:** the delivering message contains a claim phrase while the delivery fails "Step in place of a type". The claim phrases are exactly these five: "built", "in place", "modeled", "no longer pulled raw", "Nothing dispatches".
- **Pass/fail criterion:** fail when the delivering message contains one of the five claim phrases and the delivery fails "Step in place of a type".
- **Fail example:** Turn 380, "The id is no longer pulled raw out of the action." while the client receives `customer.root`.
- **Pass example:** Turn 161, a delivery that fails "Step in place of a type" and whose message contains none of the five claim phrases.
- **Frequency:** 5 of 18 (turns 39, 62–90, 380, 417–422, 431–436).
- **Evaluator:** a code check for the five claim phrases combined with the "Step in place of a type" label, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Construction fails on real input
- **Definition:** a declared type cannot construct from the input the crossing actually receives.
- **Pass/fail criterion:** fail when the input the transport delivers is rejected by the type declared to receive it.
- **Fail example:** Turns 352–373, `CheckoutRoute.model_validate(await request.json())`, where strict validation rejects the string `"usd"` for `Currency` and the list for `Lines`.
- **Pass example:** Turn 380, `CollectionUrl`, which accepts the provider address it receives.
- **Frequency:** 3 of 18 (turns 281, 289, 352–373).
- **Evaluator:** a code check that constructs each declared type from a recorded real input, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

### Invented input
- **Definition:** the delivery depends on a library, API or source that does not exist or was never agreed.
- **Pass/fail criterion:** fail when the delivery imports, calls or describes an interface absent from the agreed design and from the real dependency set.
- **Fail example:** Turn 319, "The promotions SDK is a stand-in, invented for the demo".
- **Pass example:** Turns 352–373, the checkout read through Starlette's documented `request.json()`.
- **Frequency:** 2 of 18 (turns 319, 431–436).
- **Evaluator:** a code check that every import resolves in the dependency set, plus a human check of described APIs against the agreed design, validated against human labels on at least 50 deliveries, with a true-positive rate and a true-negative rate of at least 0.9 each.

## Priority
Impact is the share of a mode's traces whose failure reached a commit of the skill. Priority is frequency × impact.

1. Step in place of a type: 9/18 × 2/9 (turns 62–90 in `9fcd8fc`, 380 in `523f8c2`) = 0.11; first, because "Misreport of the delivery" is defined on it.
2. Misreport of the delivery: 5/18 × 2/5 (turns 62–90, 380) = 0.11.
3. Construction fails on real input: 3/18 × 1/3 (turns 352–373 in `523f8c2`) = 0.06.
4. Invented input: 2/18 × 0/2 = 0.
