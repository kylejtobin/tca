---
name: tca-status
description: "The TCA run status board: a framed kanban of the loop's steps with the run's progress, trend and verdict counts beneath, each element captioned. Use when the project owner asks how a tca-agent run is going, after each accepted step, or whenever a status is requested. Template and schema only; any agent renders it by hand."
---

# TCA status board

One board, one layout, every time. The reader learns where each thing lives
once, then reads by position and shape; the captions say what each thing means.
Rendered inside a code block so the frame holds.

## Sections, in reading order

1. Health: do I need to act. The dot is the only saturated colour in the frame.
2. Where the work is: a kanban of the loop's steps, to do, doing, done.
3. How far: nouns written over nouns listed; crossings built; files of the current crossing.
4. How it is going: tries per accepted step as a sparkline; every verdict in order as small marks.
5. Verdict counts: since the last board, and for the whole run.

## Rules

- 🟢 running, 🟡 needs you or stuck (a prompt waiting, or the same step rejected three times on one ground), 🔴 stopped.
- Health alone carries saturated colour. History marks are `✓` and `×`, never ✅ ❌.
- Columns flow left to right: to do, doing, done. One card is one step of the
  loop; a crossing's file steps are its cards; at most one card is doing.
- Bars are twenty cells of `■` and `□`, one scale, labelled.
- Every icon has one lowercase word; every section has a one-line caption.
- Fixed positions. New information never reorders the board.
- Frame width 86 inside the borders. Pad each line to the frame by character
  count, one column less per emoji. Section rules are `├─┤` lines.
- Sparkline: tries 1 to 7 are `▁▂▃▄▅▆▇`; above 7 is `█`.

## Where each number comes from

- Cards: step 2's derivation gives the crossings; the accepted list gives each crossing's files in order; `verify outcome` and `commit` close the queue.
- Tries on a done card, and the sparkline: verdicts per accepted step, from the coordinator's verdict messages to `main`.
- Nouns: on the latest accepted list, rows written over rows total for the crossings listed so far.
- Crossings: built when a crossing's last file step is accepted; files from the accepted list's file order.
- Verdict marks and counts: every verdict message in order; `red check` is a `just check` that exited nonzero and was recovered by the loop; `revert` is code written out of order and removed; `exit` is work handed back, which never happens.
- Elapsed: from the coordinator's first verdict. Last: from its last accepted verdict.
- Since last board: deltas against the previous board posted.

## Template

Placeholders in braces. Lines beginning `#` are section rules.

```
 {🟢|🟡|🔴} {running|needs you|stopped} · {what, if anything, waits on the owner}     ⏰ elapsed {h}h{mm}m    ✅ last {m}m ago
   {one line: why the dot is this colour}
#
 WHERE THE WORK IS   one card = one step of the loop; a crossing's files are its steps
 ⬜ to do · {n}              ⏳ doing · {0|1}            ✅ done · {n}
 ─────────────────────────  ─────────────────────────  ─────────────────────────
 {next card}                {doing card}               {first done card  ·tries if >1}
 {next card}                   🔁 try {k}   ⏰ {m}m     {done card}
 {…}                                                   {…}
#
 HOW FAR
 📋 nouns       {bar}   {pct}%    {written} / {listed} listed
                types already written, over every type the one list names so far
 🔀 crossings   {bar}   {built} / {derived} built · C{k} 📄 {done} / {files} files
                the outcome's crossings fully built; the current one's files done
#
 HOW IT IS GOING
 🔁 tries     s1 {▇}   s2 {▂}   C1 {▁▃▁…}   C{k} {…}        last {n}   worst {n}
              submissions each accepted step took; a tall bar was a fight
 🧾 verdicts  {×✓… in order}                                 ✅ {n}   ❌ {n}
              every verdict in order, × rejected ✓ accepted; clustered × = trouble
#
 VERDICT COUNTS        ✅ accepted  ❌ rejected  🔧❌ red check  🔙 revert  🚪 exit
 ▲ since last board         {+n}        {n}          {n}        {n}      {n}
 Σ whole run                {n}         {n}          {n}        {n}      {n}
   red check: a just check that failed and was recovered by the loop, not patched
   revert: code written out of order, removed · exit: work handed back; never allowed
```

Columns in the kanban are 27 characters each, padded by character count with
one less per emoji in the cell. The title bar reads `─ 🟦 TCA · outcome {n} `.

## Rendered example

```
┌─ 🟦 TCA · outcome 2 ─────────────────────────────────────────────────────────────────┐
│ 🟢 running · nothing needs you                 ⏰ elapsed 2h07m    ✅ last 9m ago    │
│   green: the loop is running and no prompt or decision is waiting on you             │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ WHERE THE WORK IS   one card = one step of the loop; a crossing's files are its steps│
│ ⬜ to do · 10              ⏳ doing · 1               ✅ done · 11                   │
│ ─────────────────────────  ─────────────────────────  ─────────────────────────      │
│ C2 record/model.py         C2 record/identity.py      s1 state  ·7 tries             │
│ C2 record/score.py            🔁 try 2   ⏰ 1m        s2 derive ·2                   │
│ C2 __init__.py                                        C1 compose · list              │
│ C2 task.py                                            C1 6 files                     │
│ C2 verify · 2 tests                                   C2 compose · list ·4           │
│ C3 read the log                                       C2 value.py                    │
│ C4 rescore                                            C2 evaluator/model.py          │
│ C5 Phoenix writes                                     C2 evaluator/provider.py       │
│ 🧪 verify outcome                                     C2 score.py                    │
│ 💾 commit                                             C2 dataset.py                  │
│                                                       C2 run.py                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ HOW FAR                                                                              │
│ 📋 nouns       ■■■■■■■■■■■■□□□□□□□□   59%    37 / 63 listed                          │
│                types already written, over every type the one list names so far      │
│ 🔀 crossings   ■■■■□□□□□□□□□□□□□□□□   1 / 5 built · C2 📄 6 / 11 files               │
│                the outcome's crossings fully built; the current one's files done     │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ HOW IT IS GOING                                                                      │
│ 🔁 tries     s1 ▇   s2 ▂   C1 ▁▃▁▁▁▁▁▁   C2 ▂▄▁▁▁▁▁▁▁▂       last 2   worst 7        │
│              submissions each accepted step took; a tall bar was a fight             │
│ 🧾 verdicts  ×××××××✓×✓✓××✓✓✓×✓✓✓✓✓×✓×✓✓××✓✓✓✓✓✓✓×          ✅ 21   ❌ 16            │
│              every verdict in order, × rejected ✓ accepted; clustered × = trouble    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ VERDICT COUNTS        ✅ accepted  ❌ rejected  🔧❌ red check  🔙 revert  🚪 exit   │
│ ▲ since last board         +0          1            0          0        0            │
│ Σ whole run                21         16            5          1        0            │
│   red check: a just check that failed and was recovered by the loop, not patched     │
│   revert: code written out of order, removed · exit: work handed back; never allowed │
└──────────────────────────────────────────────────────────────────────────────────────┘
```
