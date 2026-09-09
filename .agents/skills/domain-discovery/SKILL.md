---
name: domain-discovery
description: Decides what a domain contains from evidence before any construct is written, through a three-step schema-gated process: evidence, things, constructs. Use before modeling from any outside source (a vendor reply, SDK, document, or spec), when the user says "model this", "print the reply", or "what does this tell us about our world", and whenever a domain is about to gain or change a type.
---

# Domain Discovery

Output of every step: written answers. No step passes on judgment. Every answer is decided, not deferred. One question per turn, in chat, in the form asked, no prose; the operator advances the step. Why each question exists: [`wiki/discovery/`](../../../wiki/discovery/index.md).

## 1. Evidence

Render the real evidence: instances of the thing, whole and unedited — an API reply constructed through the vendor's SDK and printed as pretty JSON; a document quoted; another program's model read as written. Read it before naming anything. Never author the evidence for this model: what you render was made for some other purpose than modeling this.

## 2. Things

1. What things in the world is this evidence of, and how do they compose into each other?
2. For each thing: is it already ours, and if so which type, or is it new?
3. For each thing: what is it, as it is in nature, and what must be true of it?
4. For each thing: what is its best name?
5. What in the evidence is the source's account of a thing and not the thing?
6. Seen whole with these things in it, should the world look different, and how?
7. From the answers above, fill this and nothing else:

```json
{
  "create": [{"name": "", "is": "what it is in nature", "must": ["what is true of every one"], "holds": ["things it composes"]}],
  "change": [{"name": "existing type", "becomes": "what it is now"}],
  "unchanged": ["existing types the evidence touches and leaves as they are"]
}
```

Output: the filled schema. No construct types.

## 3. Constructs

1. Construct per entry, both lists: the whitelist construct, its fields with their types, and for a full thing what two equal on.
2. Holders of changed things: one line per holder, per changed thing: what the field becomes.
3. Placement: one line per construct: context, file.
4. Breaks: one line per entry, per break: escaped, duplicated, vacuous, fused. State why it does not break. A pass is written or it is not a pass.
5. Any break that did not pass: name the earliest question whose answer produced it and resume there, voiding every answer after it. Otherwise 3.6.
6. From the answers above, fill this and nothing else:

```json
{
  "constructs": [{"name": "", "construct": "whitelist construct", "file": "domain/<context>/<file>.py", "fields": {"field": "Type"}, "equals": ["fields two equal on, full things only"]}],
  "holders": [{"file": "domain/<context>/<file>.py", "type": "existing type", "field": "existing field", "becomes": "Type"}],
  "removed": ["types and files that no longer exist"]
}
```

Output: the filled schema. Discovery ends here. Build makes exactly this set.

## Rationalizations

| Reach | Reality |
|-------|---------|
| The vendor already has a vocabulary. | That is the source's account. Decide ours from the thing and what the program does with it; alias theirs. |
| This needs the operator's ruling. | Nothing is the operator's to rule on. A conflict means the thing is not yet seen. Look harder. |
| The checker refuses the whitelist form. | The form is the standard. Name the checker's blindness where it bites. Never edit the whitelist. |
| This primitive is not on the list. | The whitelist is the pattern, not the primitive. Pick the value space where the wrong value cannot be built. |
| Describing the process is doing it. | A procedure is what gets written when a decision has not been made. Answer the question. |
| A name unlike the vendor's is better. | Best name is the expert's word. Matching is fine. Differing to differ is the wrong reason. |
| I read the whole set; it passes. | A pass is one written line per entry per break. Unwritten is unchecked. |
