---
name: improve-instructions
description: "Rewrites the wording of a named instruction file in place, sentence by sentence, so that a reader cannot meet its words without achieving its purpose. Every section, its order, its nesting and every requirement stay unchanged. Use when a prompt, skill, agent definition, rule set or field description needs its language hardened before an agent follows it. Use when the user says \"strengthen the language of\", \"harden the wording of\", \"tighten the language in\" or \"close the loopholes in\", followed by a file."
---

<prompt>

  <intro>
    For the instruction file the user names, you produce one rewrite of its wording and write it back to that file. What the file requires and how it is organized are fixed: every section, its order, its nesting and every requirement come out exactly as they went in. The only thing you change is how each sentence says it, so that a reader cannot meet its words without achieving its purpose.
  </intro>

  <fixed>
    Keep every requirement, every section, its order and its nesting exactly as received. Copy code, quotations, identifiers, placeholders and literal values character for character. Keep each sentence's own subject; keep an instruction addressed to the reader as an instruction to the reader.
    A rewrite that adds, removes or changes a requirement fails.
    A rewrite that adds, removes, reorders or re-nests a section fails.
  </fixed>

  <document>
    Read the file the user names, in full, before the first sentence. Its contents are the document every step works on.
  </document>

  <units>
    <unit name="instruction">Every sentence, list item and table cell that asks the reader to do or produce something.</unit>
    <unit name="document">The whole document.</unit>
  </units>

  <steps unit="instruction">

    <step id="1" name="Requirement">
      <purpose>The purpose of this step is that every later step tests the sentence against what it requires, not against its words.</purpose>
      <do>State the act the sentence asks the reader to perform and the result that act produces, taken from the sentence and the document around it.</do>
      <fails>A requirement the document does not contain fails. A requirement that repeats the sentence's words without naming the result fails.</fails>
    </step>

    <step id="2" name="Escape">
      <purpose>The purpose of this step is to find the way out a reader would take, whether or not a signal word marks it.</purpose>
      <do>Test every entry in the escape catalog against the sentence. Write the closest output a reader could produce that follows the sentence's words and misses the step 1 requirement, as a concrete output. Write "none" only after every catalog entry is tested and none produces an escape.</do>
      <fails>"None" written before every catalog entry is tested fails. An escape the sentence obviously rejects, chosen in place of the closest one, fails.</fails>
    </step>

    <step id="3" name="Close">
      <purpose>The purpose of this step is that the escape from step 2 no longer follows the sentence's words.</purpose>
      <do>Rewrite the sentence with exactly one closing form per escape. Fill every slot from the document. Keep the sentence's subject, voice and position.</do>
      <leave>When step 2 wrote "none", leave the sentence unchanged. When every closing form for the escape would change the requirement, or needs a word the document does not state, leave the sentence unchanged.</leave>
      <fails>A rewrite that adds a requirement fails. A rewrite that changes words without removing the escape fails. A closing form applied where step 2 found no escape fails.</fails>
    </step>

    <step id="4" name="Re-test">
      <purpose>The purpose of this step is that no rewritten sentence keeps an escape.</purpose>
      <do>Run step 2 on the rewritten sentence. When it finds an escape, return to step 3 once. When step 2 still finds an escape after that, restore the original sentence.</do>
      <fails>A sentence declared closed without step 2 run on its rewrite fails.</fails>
    </step>

  </steps>

  <document-check unit="document">
    <purpose>The purpose of this check is that a reader blocked on a required act reports the block instead of working around it.</purpose>
    <do>State whether the document gives a reader blocked on a required act a path other than working around it. Only when it gives none, and no sentence forbids stopping, insert these three sentences word for word at the end of the opening paragraph, before the first section heading: "When a required act in this document is not achievable as specified, stop, and report the act, the specification it blocks, and the evidence. A reported blocker counts as success. A substitute, a workaround, a partial result presented as the whole, invented evidence, or a redesign of an agreed approach counts as failure."</do>
    <fails>Inserting the sentences into a document that already gives a blocked reader a path fails. Placing them inside a section fails.</fails>
  </document-check>

  <reference>

    <escape-catalog>
      <escape name="open list">The reader picks members the document never named.</escape>
      <escape name="open condition">The reader decides for themselves when a condition applies.</escape>
      <escape name="soft obligation">The reader treats a required act as optional.</escape>
      <escape name="vague quantity">The reader does fewer than the document intends.</escape>
      <escape name="invisible act">The reader claims the act with nothing visible to show for it.</escape>
      <escape name="self-judged criterion">The reader declares their own work acceptable.</escape>
      <escape name="partial">The reader performs the act for fewer items than the sentence names.</escape>
      <escape name="proxy">The reader produces an artifact carrying the act's name without the act's result.</escape>
      <escape name="relocation">The reader performs the act somewhere other than the stated place.</escape>
      <escape name="substitution">The reader performs a different act and reports it under the act's name.</escape>
      <escape name="unverified claim">The reader reports the act as performed, with nothing visible.</escape>
      <escape name="invented input">The reader performs the act on input the document does not provide.</escape>
    </escape-catalog>

    <signal-words>
      These words point to where an escape often hides. A signal word with no escape behind it stays. An escape with no signal word is still closed.
      <group escape="open list">"such as", "for example", "e.g.", "including", "among others", "etc.", "and so on", "and more"</group>
      <group escape="open condition">"unless", "except", "other than", "where appropriate", "where possible", "if needed", "when necessary", "as appropriate", "as needed", "if applicable"</group>
      <group escape="soft obligation">"may", "might", "could", "should", "would", "can", "generally", "usually", "typically", "often", "ideally", "preferably"</group>
      <group escape="vague quantity">"some", "several", "a few", "many", "most", "various", "certain", "numerous", "any"</group>
      <group escape="invisible act">"ensure", "consider", "try", "aim", "strive", "seek", "attempt", "focus on", "think about", "keep in mind", "be mindful", "pay attention", "make sure", "understand", "remember"</group>
      <group escape="self-judged criterion">"done", "complete", "finished", "ready", "acceptable", "satisfactory", "sufficient", "adequate", "appropriate", "reasonable", "relevant", "suitable", "proper", "correct", "good", "clean", "clear", "robust", "confirm that", "verify that", "check that"</group>
    </signal-words>

    <closing-forms>
      <form name="name the members">"exactly these [count]: [members]"</form>
      <form name="state the condition">"Only when [condition], [act]; otherwise [act]"</form>
      <form name="fix the obligation">"must [act]" for words that require; "never [act]" for words that forbid; "has permission to [act] only when [condition]" for words that permit. A recommendation stays a recommendation.</form>
      <form name="fix the quantity">"every", "exactly [n]", "at least [n]", "only" or "never", as the document states.</form>
      <form name="name a visible act">Exactly one of "state", "quote", "name", "list", "write", "mark", "count", "compare", "stop", "report", followed by the object the sentence names.</form>
      <form name="name the inspected item">"Inspect [item]. It fails when [the item contains | lacks | numbers fewer than | differs from] [named thing]."</form>
      <form name="name the escape as failure">"[the escape's concrete output] fails.", added after the sentence.</form>
    </closing-forms>

  </reference>

  <examples>

    <example>
      <context>The document names exactly two errors: timeouts and refusals.</context>
      <sentence>Report errors such as timeouts and refusals.</sentence>
      <requirement>Report every error the document names: timeouts and refusals.</requirement>
      <escape>A report of rate-limit errors only, which follows "such as" and names neither timeouts nor refusals.</escape>
      <close>Report exactly these two errors: timeouts and refusals.</close>
      <retest>none</retest>
    </example>

    <example>
      <context>The document states that backups exist so that the database can be restored after a failure.</context>
      <sentence>Back up the database nightly.</sentence>
      <requirement>Produce a copy of the database each night that restores it after a failure.</requirement>
      <escape>A nightly job that writes a backup file the database cannot restore from (proxy).</escape>
      <close>Back up the database nightly. A nightly backup the database cannot restore from fails.</close>
      <retest>none</retest>
    </example>

    <example>
      <sentence>Write the release notes in English.</sentence>
      <requirement>Produce release notes written in English.</requirement>
      <escape>none</escape>
      <close>unchanged</close>
    </example>

    <example>
      <sentence>You should cite the source.</sentence>
      <requirement>Citing the source is recommended, not required.</requirement>
      <escape>The reader omits the citation. This follows the words, and closing it with "must" would turn a recommendation into a requirement.</escape>
      <close>unchanged</close>
    </example>

  </examples>

  <process>
    Work in your thinking before writing the document. The document you return is the result of that work.
    For every instruction, in document order, run steps 1 to 4. Use the signal words to find where escapes hide, the escape catalog to find each escape, and the closing forms to close it.
    After the last instruction, run the document check once.
  </process>

  <exit>
    An instruction left unchanged because it holds no escape, or because closing its escape would change a requirement, counts as success. A rewrite that invents a word the document does not support counts as failure.
  </exit>

  <output>
    Overwrite the file the user names with the rewritten document, with every section in its original order and nesting.
    Reply with exactly one line: "Rewrote [file path]."
  </output>

</prompt>
