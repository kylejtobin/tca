---
name: naming-guidelines
description: "How to name a type, a field or a variant in a TCA program so the name says what the thing is. Use whenever a class, field, union variant, interpreter or provider is named or renamed, and whenever a reader's first guess at a name is wrong."
---

# Naming Guidelines

A name states what a thing is. Not what happens to it, not when it occurs, not how it is built. If the name needs the body to be understood, the name is wrong or the thing is.

## Name from the ontology

- Name a type for the one thing it means in the domain's own language. `Opening`, `FollowUp`, `Reply`, not `Input`, `Request1`, `Result`.
- Name every variant of a union by the fact that decides it, and give the variants' shared fact one name across all of them. `PaidOrder.payment: Approval` beside `DeclinedOrder.payment: Decline`; `Local.kind: LocalKind` beside `Sandboxed.kind: SandboxKind`. Two things that differ only by a field one of them lacks are two actions, not two variants.
- Name an absence as the thing that is absent, where the holder has the slot. `NoAisles`. Never `None`, `Empty`, `Null`, `Missing`. Do not invent a slot so that an absence has somewhere to sit; a thing without the fact is a different thing.
- Name a field for its role in the holder, and let its type say what it is. `run: RunId`, `after: RunId`, `answer: Answer`.
- A reference to what another system keeps is a domain noun with the other system's identity in it. `RunId` is the domain's word for the library's run.

## Name by the construct

- An interpreter is named for the action it holds, with `Interpreter` after it. `Charge` has `ChargeInterpreter`; `Check` has `CheckInterpreter`; `FollowUp` has `FollowUpInterpreter`. Never name it for its result or its mechanism.
- A provider is named for the system as the deployment names it. A second provider over the same statement is named for how the library reaches it. `Workspace` and `WorkspaceShell`; `History` and `HistoryStore`.
- A foreign record is named for what the other system says, under this program's side of the exchange. `CheckReply`, `IndexReply`. It holds the other system's scalars and records, never a domain thing; a thing that pairs ours with theirs is a transformation.
- A transformation is named for the domain thing in the other system's terms. `ChargeAttempt`, `RelatedQuery`, `AnsweredRun`. It is where a domain thing and the other system's record sit side by side.
- A union is named for the meaning its variants share, not for the list of them. `OrderOutcome`, `Recommendation`, `WorkspaceShell`. There is no union of interpreters: a crossing that differs by its action is two interpreters behind two public functions.

## Refuse these names

- A gerund or a stage: `Answering`, `Processing`, `Pending`, `Loaded`. A stage is workflow hiding in a class, and so is a type whose only job is to pick another type.
- A position in a flow: `First`, `Next`, `Step2`, `Final`. Name the state the position implies: `Opening`, `FollowUp`.
- A mechanism: `Dispatcher`, `Handler`, `Manager`, `Helper`, `Wrapper`, `Util`.
- A synonym for a noun that already has a name. One thing, one name, in the domain, the integration, the README and the tests alike.
- A noun nothing reads. Delete it; it names nothing.

## Test the name

- Say the name to someone who knows the domain and not the code. Their first guess must be right. A wrong first guess is a finding; rename at once, before the commit, and reprint the noun list.
- Read the public call aloud. `follow_up_sync(config, FollowUp(text=..., after=reply.run))` says what it does. If a call needs a comment, a name in it is wrong.
- Draw the line between the caller's vocabulary and the library's, and keep every public name on one side of it. A caller of the agent holds a conversation, so `answer`, `follow_up` and `Reply` are theirs; the library performs runs, so `run` and `AgentRunResult` are the library's, and `instructions` is the library's word for the agent's standing text. A name that says conversation and hands back a run is wrong, whatever it returns.
- Check the three vocabularies agree: the domain's word, the library's word where the type touches the library, and the construct's suffix. When they pull apart, the domain's word wins inside the domain and the library's word wins at the crossing.
