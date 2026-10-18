---
name: tca-status
description: "Renders the TCA run status board: a framed, fixed-layout, dual-coded (icon + one word) picture of a tca-agent run over an outcome, with progress as bar length, health as the only colour, and the verdict history as small marks. Use when the project owner asks how a run is going, after each accepted step, or whenever a status is requested."
---

# TCA status board

One board, one layout, every time. The reader learns where each thing lives once
and then reads by position and shape. Words are labels, never sentences.

## What it answers, in order

1. Do I need to act. The health dot, the only saturated colour in the frame.
2. What is it doing now. Crossing, verb, file, rows, try, minutes on this try.
3. How far. Nouns written over nouns listed; crossings built; files in the current crossing.
4. How is it going. Tries per accepted step as a sparkline; the verdict sequence as small marks.
5. What changed since the last board, and the totals, as a table.

## Rules

- Health alone carries colour. 🟢 running, 🟡 needs you or stuck, 🔴 stopped.
- Progress is length. All bars are twenty cells of `■` and `□`, same scale, labelled.
- Dual coding: every concept is one icon followed by one lowercase word, once.
- History is small and grey: `✓` and `×`, never ✅❌, so a healthy run never reads as an incident.
- The footer is a table: icons as column headers once, numbers aligned beneath.
- Fixed positions. New information never reorders the board.
- Every line is padded to the frame by the renderer, one column less per emoji.

## Where the numbers come from

- Nouns written / listed: the latest accepted list in the modeler's reply, rows marked written against rows total for the crossings listed so far.
- Crossings built / derived: step 2's derivation; a crossing is built when its last file step is accepted.
- Tries per step: verdicts per accepted step, from the coordinator's `SendMessage` verdicts to `main`.
- Verdict sequence, red checks, reverts, exits: the same verdict messages, in order.
- Elapsed: from the coordinator's first verdict timestamp. Since last: from its last accepted verdict.

## Key

🟢🟡🔴 health · ⏰ time · ✅ accepted · ❌ rejected · ▶️ now · 📝 model it · 📄 file ·
📋 list rows, nouns · 🔀 crossings · 🔁 tries · 🧾 verdicts · 🧪 verify · 💾 commit ·
🔧❌ red check · 🔙 revert · 🚪 exit · 🆕 since last · 🧮 all time

## Template

Write the body lines to a file and render with `render.sh <file> [width]`; the
renderer draws the frame, the title and the section rules, and pads each line.
Section rules follow lines 1, 3, 6 and 8.

```
 🟢 running · nothing needs you                 ⏰ elapsed 1h52m    ✅ last 7m ago
 ▶️ now  C2 · 📝 model it · 📄 integration/evaluator/model.py · 📋 edge 116(a)
                                                           🔁 try 1    ⏰ 7m
 📋 nouns       ■■■■■■■■■□□□□□□□□□□□   43%    26 / 60 listed
 🔀 crossings   ■■■■□□□□□□□□□□□□□□□□   1 / 5 built · C2 📄 1 / 11 files
 ✅ s1   ✅ s2   ✅ C1   ⏳ C2   ⬜ C3   ⬜ C4   ⬜ C5   ⬜ 🧪 verify   ⬜ 💾 commit
 🔁 tries     s1 ▇   s2 ▂   C1 ▁▃▁▁▁▁▁▁   C2 ▂▄▁▁           last 1   worst 7
 🧾 verdicts  ×××××××✓×✓✓×✓✓✓×✓✓✓✓✓×✓×✓✓××✓✓               ✅ 16   ❌ 14
                 ✅ ok    ❌ no    🔧❌ red    🔙 revert    🚪 exit
 🆕 since last    +1       0        0           0           0
 🧮 all time      16      14        2           1           0
```

Rendered:

```
┌─ 🟦 TCA · outcome 2 ───────────────────────────────────────────────────────────────┐
│ 🟢 running · nothing needs you                 ⏰ elapsed 1h52m    ✅ last 7m ago  │
├────────────────────────────────────────────────────────────────────────────────────┤
│ ▶️ now  C2 · 📝 model it · 📄 integration/evaluator/model.py · 📋 edge 116(a)     │
│                                                           🔁 try 1    ⏰ 7m        │
├────────────────────────────────────────────────────────────────────────────────────┤
│ 📋 nouns       ■■■■■■■■■□□□□□□□□□□□   43%    26 / 60 listed                        │
│ 🔀 crossings   ■■■■□□□□□□□□□□□□□□□□   1 / 5 built · C2 📄 1 / 11 files             │
│ ✅ s1   ✅ s2   ✅ C1   ⏳ C2   ⬜ C3   ⬜ C4   ⬜ C5   ⬜ 🧪 verify   ⬜ 💾 commit│
├────────────────────────────────────────────────────────────────────────────────────┤
│ 🔁 tries     s1 ▇   s2 ▂   C1 ▁▃▁▁▁▁▁▁   C2 ▂▄▁▁           last 1   worst 7        │
│ 🧾 verdicts  ×××××××✓×✓✓×✓✓✓×✓✓✓✓✓×✓×✓✓××✓✓               ✅ 16   ❌ 14            │
├────────────────────────────────────────────────────────────────────────────────────┤
│                 ✅ ok    ❌ no    🔧❌ red    🔙 revert    🚪 exit                 │
│ 🆕 since last    +1       0        0           0           0                       │
│ 🧮 all time      16      14        2           1           0                       │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Sparkline scale

Tries 1 to 7 map to `▁▂▃▄▅▆▇`; anything above 7 is `█`.
