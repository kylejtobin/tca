# Error Analysis

## Context
<the system, the task, and what a good output is>

## Trace Sample
<the source of the traces, the sampling method, and the number reviewed>

## Open Codes

| Trace ID | First failure observed |
|---|---|
| <ID> | <note> |

## Failure Modes

### <Mode name>
- **Definition:** <what the failure is, in observable terms>.
- **Pass/fail criterion:** <the binary test that decides whether a trace shows the mode>.
- **Fail example:** <a trace that shows the mode>.
- **Pass example:** <a similar trace that does not>.
- **Frequency:** <the count and share of sampled traces that show the mode>.
- **Evaluator:** <a code-based check or an LLM judge, validated against human labels>.

## Priority
<the order in which modes are addressed, by frequency and impact>
