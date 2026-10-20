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
3. How far: rows written over rows listed; files written over files the list names.
4. How it is going: tries per accepted step as a sparkline; every verdict in order as small marks.
5. Verdict counts: since the last board, and for the whole run.

## Rules

- 🟢 running, 🟡 needs you or stuck (a prompt waiting, or the same step rejected three times on one ground), 🔴 stopped.
- Health alone carries saturated colour. History marks are `✓` and `×`, never ✅ ❌.
- Columns flow left to right: to do, doing, done. One card is one step of the
  loop; the file steps are one card per file the list names; at most one card
  is doing.
- Bars are twenty cells of `■` and `□`, one scale, labelled.
- Every icon has one lowercase word; every section has a one-line caption.
- Fixed positions. New information never reorders the board.
- Frame width 86 inside the borders. Pad each line to the frame by character
  count, one column less per emoji. Section rules are `├─┤` lines.
- Sparkline: tries 1 to 7 are `▁▂▃▄▅▆▇`; above 7 is `█`.

## Where each number comes from

- Cards: the loop's lines in order: `outcome`, `chain`, `gate`, one card per file in the list's file order, `verify`, `commit`.
- Tries on a done card, and the sparkline: verdicts per accepted step, from the coordinator's verdict messages to `main`.
- Rows: on the latest accepted `nouns.json`, rows whose class exists over rows listed.
- Files: a file is written when its step is accepted; files from the list's file order.
- Verdict marks and counts: every verdict message in order; `red check` is a `just check` that exited nonzero and was recovered by the loop; `revert` is code written out of order and removed; `exit` is work handed back, which never happens.
- Elapsed: from the coordinator's first verdict. Last: from its last accepted verdict.
- Since last board: deltas against the previous board posted.

## Template

Placeholders in braces. Lines beginning `#` are section rules.

```
 {🟢|🟡|🔴} {running|needs you|stopped} · {what, if anything, waits on the owner}     ⏰ elapsed {h}h{mm}m    ✅ last {m}m ago
   {one line: why the dot is this colour}
#
 WHERE THE WORK IS   one card = one step of the loop; one card per file the list names
 ⬜ to do · {n}              ⏳ doing · {0|1}            ✅ done · {n}
 ─────────────────────────  ─────────────────────────  ─────────────────────────
 {next card}                {doing card}               {first done card  ·tries if >1}
 {next card}                   🔁 try {k}   ⏰ {m}m     {done card}
 {…}                                                   {…}
#
 HOW FAR
 📋 rows        {bar}   {pct}%    {written} / {listed} listed
                classes already written, over every row the list names
 📄 files       {bar}   {written} / {files} written
                files of the list written, in its file order
#
 HOW IT IS GOING
 🔁 tries     outcome {▇}   chain {▂}   gate {▁}   files {▁▃▁…}        last {n}   worst {n}
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
┌─ 🟦 TCA · outcome 1 ─────────────────────────────────────────────────────────────────┐
│ 🟢 running · nothing needs you                 ⏰ elapsed 0h41m    ✅ last 4m ago    │
│   green: the loop is running and no prompt or decision is waiting on you             │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ WHERE THE WORK IS   one card = one step of the loop; one card per file the list names│
│ ⬜ to do · 4               ⏳ doing · 1               ✅ done · 6                    │
│ ─────────────────────────  ─────────────────────────  ─────────────────────────      │
│ checkout/order.py          checkout/connections.py    outcome  ·2 tries              │
│ api/checkout.py               🔁 try 1   ⏰ 3m        chain    ·3                    │
│ config.py                                             gate                           │
│ 🧪 verify · 3 tests                                   checkout/type.py               │
│ 💾 commit                                             checkout/value.py              │
│                                                       checkout/record.py             │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ HOW FAR                                                                              │
│ 📋 rows        ■■■■■■■■■■■□□□□□□□□□   56%    14 / 25 listed                          │
│                classes already written, over every row the list names                │
│ 📄 files       ■■■■■■■■■□□□□□□□□□□□   3 / 7 written                                  │
│                files of the list written, in its file order                          │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ HOW IT IS GOING                                                                      │
│ 🔁 tries     outcome ▂   chain ▃   gate ▁   files ▁▁▁                 last 1   worst 3 │
│              submissions each accepted step took; a tall bar was a fight             │
│ 🧾 verdicts  ×✓××✓✓✓✓✓                                     ✅ 6    ❌ 3             │
│              every verdict in order, × rejected ✓ accepted; clustered × = trouble    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ VERDICT COUNTS        ✅ accepted  ❌ rejected  🔧❌ red check  🔙 revert  🚪 exit   │
│ ▲ since last board         +1          0            0          0        0            │
│ Σ whole run                 6          3            1          0        0            │
│   red check: a just check that failed and was recovered by the loop, not patched     │
│   revert: code written out of order, removed · exit: work handed back; never allowed │
└──────────────────────────────────────────────────────────────────────────────────────┘
```
