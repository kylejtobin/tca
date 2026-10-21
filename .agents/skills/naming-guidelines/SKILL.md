---
name: naming-guidelines
description: "How to name a type, a field or a variant in a TCA program so the name says what the thing is. Use whenever a class, field or union variant is named or renamed, and whenever a reader's first guess at a name is wrong."
---

# Naming Guidelines

A name states what a thing is. Not what happens to it, not when it occurs, not how it is built. If the name needs the body to be understood, the name is wrong or the thing is.

This skill is a skeleton. Each section is refilled with examples from the first page in the `tca-python-dev` skill once it constructs under `tca-python-dev`'s schema.

## Name from the ontology

A type is named for the one thing it means in the domain's own language. A union member is named by what decides it. An absence is named as the thing that is absent, never `None`. A field is named for its role in the holder; its type says what it is. A kind is never in a name. A route is a class, named as the business names the thing it does.

## Refuse these names

A gerund or a stage, a position in a flow, a mechanism, a synonym for a noun that already has a name, a noun nothing reads.

## Test the name

Say the name to someone who knows the domain and not the code; their first guess must be right. Keep the domain's vocabulary and each party's on their own sides of the line: a `Record` carries the party's names under aliases, every other class carries the domain's.
