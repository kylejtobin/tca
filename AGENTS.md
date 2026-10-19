# AGENTS.md

This repository is the normative specification and reference implementation of
Type Construction Architecture, a closed vocabulary: code MUST use only what it
permits.

TCA development is delegated to `tca-agent`, never to `tca-modeler` directly.
`tca-agent` runs the loop in the `tca-modeling` skill, which governs every
line of application code in this repository.

- Open every response with the deliverable and its scope in one line.
- Fill `.gitmessage` for every commit; its `Outcome:` is the outcome reached.
  Commit when an outcome's check is green. The gate is a check: when it fails,
  you stopped modeling, and its findings are accepted whole.
- Run checks only as `just` declares them; report no other result. Passing is
  not proof: a design that meets a rule's syntax and defeats its purpose is
  wrong.

## Working with tca-agent

`tca-agent` (`.agents/agents/tca-agent.md`) runs the `tca-modeling` loop by
delegating each step to `tca-modeler`, which it starts and resumes itself. The
main session never calls `tca-modeler`.

Start it with `Agent(subagent_type="tca-agent")`. The prompt holds the
outcome's text, where the tree stands, and the owner's constraints. Nothing
else.

It sends every verdict to `main`. Judge each against the loop's line. Message
it only with an owner constraint, an environment fact (what, when, which
paths), or a question it raised returned with the sentence that decides it.
Never an answer.

While it runs, do not commit (the gate stashes unstaged work) and do not edit
what the loop reads or writes; an unavoidable owner edit is named to it as not
the modeler's and not to be staged.

Watch the transcripts under `~/.claude/projects/<project>/<session>/subagents/`;
a sandboxed loop reading by offset is enough.

Stop both: `TaskStop` the coordinator, `ListAgents`, `TaskStop` the modeler.
Its final handback carries the commit hash; push after it.
