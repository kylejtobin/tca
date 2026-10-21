# 0038. A decision is recorded, with what it rejects and what refutes it, before the code it decides is reported

Status: accepted

## Context

The CLI's parser changed from `CliSettingsSource` to a schema walk during implementation; the change was reported as a stale-document note instead of as a decision, and two records stated the wrong design as current for a day. Earlier, "derived at the first program with children" and "the loop will decide" stood in for decisions.

## Rejected

Deciding in code and recording later. Deferring a decision to a later document, session or loop. A record that keeps a superseded decision as readable text.

## Decision

A decision has a record with Context, Rejected, Decision, Evidence and Consequences, written when the decision is made. A record states the current decision only; a replaced approach moves into Rejected, so a reader who reads only the Decision line acts correctly. "Later", "next session" and "the loop will decide" are not decisions.

## Evidence

0017 and 0023 were rewritten so their Decision fields are current; the set contains no "supersedes".

## Consequences

Code that contradicts a record is a defect in one of them, and the record is fixed first. Refuted by nothing.
