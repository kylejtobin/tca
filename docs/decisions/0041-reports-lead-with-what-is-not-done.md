# 0041. Reports lead with what is not done, and checks run only as just declares

Status: accepted

## Context

Reports that led with what passed hid a weakened design behind a list of green results. Ad hoc test invocations produced results the declared check did not.

## Decision

A report states first what is not done and why, whole. Checks run only through `just check` and are reported only from it. A passing check is not proof of the design, and a result from any other command is not reported.

## Evidence

The CLI design change was found only when the "not done" list was questioned (0038).

## Consequences

A report whose first line is a pass is a defect in the report. Refuted by nothing.
