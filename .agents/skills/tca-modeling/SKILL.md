---
name: tca-modeling
description: "The modeling loop of Type Construction Architecture: the steps, in order, by which an outcome is reached by constructing a domain's types under a <language>-dev-tca skill. Use before writing any application code in a TCA project, and to judge whether a step of the loop was performed."
---

# TCA Modeling

## The loop

Name the noun. Place it by what it means. Construct it; never write the step.

An outcome is one thing a party outside the system can newly do across one
crossing, made possible by constructing the domain's types; each pass reaches
one.

    state the outcome as one crossing: what crosses, the contract that owns it, the domain type it is; then the tactics that reach it
    derive the crossings in dependency order: each validated by the contract that owns it, translated where its meaning is not the domain's
    for each crossing:
        imagine it composed bottom up: Scalar, Value, Thing, and the crossing that holds them
        add this crossing's nouns to the work's one list: name, kind, file, and layer where it carries meaning
        for each file, lowest first:
            write, before the file exists, its types, fields and valid states; for every resource, who acquires it, who owns it, who releases it, and over what lifetime; a need below changes now, a need above is listed
            model it: each placement by a sentence of the skill, quoted; each type by its construct's page
            `just check`; nonzero is not done
            when a check fails, you stopped modeling. Its findings are evidence, not a list. Accept them whole, find the step you skipped, remodel from there with the whole list in question, then check again
            remove every body. The file passes only if the types alone specify the domain. A pipeline fails: remodel
            the file passes only if no type is named for a stage of the run. A stage name fails: delete it and type the thing under it
            the file passes only if every type's inhabitants are in bijection with the domain's states. Any other count fails: remodel from the domain; never patch the type
            the file passes only if no type is missing. A missing type fails: add it to the list and model it
            the list passes only if no noun on it, none settled, is missing, redundant, misnamed, misplaced, wrongly structured or wrongly owned. One fails: it is fixed or listed by the line below
            write each verdict with its evidence: the fault, or the strongest fault sought and why it does not hold
            rebuild the whole list from what is now known and print it, every time; a failed gate is fixed from the lowest file the rebuilt list changes, before any other file; a change above is listed
    verify the outcome in tests that cross as its contract's owner would, including every applicable ending and resource release; execute its documented example where it exposes a public interface; a miss is a crossing missing or wrong
