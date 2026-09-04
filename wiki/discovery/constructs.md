---
type: Reference
description: From decided things to the exact whitelist constructs to build, their holders, their placement, and a written pass for the four breaks.
---

# Constructs

Step three of discovery maps decided things to the constructs that carry them. Its input is the filled schema from [things](./things.md) and the whitelist. Its output is the exact set the build makes, and the build adds nothing the output did not name.

## Construct per entry

For each entry on the create and change lists: the whitelist construct, its fields with their types, and for a full thing what two of them are equal on. The construct follows from what the thing is, as decided in step two: one atomic value is a [semantic scalar](../constructs/semantic-scalar.md); a small value with no identity is a [value object](../constructs/value-object.md); a full thing is a [concept model](../constructs/concept-model.md); a choice on one axis is a [union](../constructs/union.md); a sequence that is its own thing is a [collection](../constructs/collection.md).

Fields are named here, and each field's type is either an existing type from step two's question 2 or a new scalar that joins the create list. A field that needs a scalar not yet on the list is a thing discovery missed, and it goes through the questions rather than being minted at the keyboard.

Where a constraint has no structural home, say so. Two ids in one model that must differ, or a tuple whose members must not repeat, cannot be proven by any construct on the whitelist. That is one escaped invariant, admitted in writing, stated in the docstring, and never enforced by a validator after construction. An admitted escape is a decision. A hidden one is a bug.

## Holders of changed things

A changed thing has holders, and every holder is a field somewhere else. `Money` becoming a magnitude changes `ledger` and `available` on two balances values, leaves `limit` alone because a limit has no standing, and leaves loan and investment balances alone because they are owed and held by their nature. `Institution` becoming a party changes `Connection.institution` from `InstitutionId` to `PartyId`. `Party` splitting into a union changes nothing, because no holder imported `Party` itself.

This is edge propagation on the construction graph. Skipped, a change lands in one file and the world is inconsistent. It is written as one line per holder per changed thing: what the field becomes.

## Placement

One line per construct: context and file, by the [topology](../topology/program-topology.md). `type.py` holds the scalars and imports nothing. `value.py` composes them and imports only `type.py`. Every other file is named for the thing it declares. A rate is not money, so `AnnualRate` lives in the account context, not the money context, and the breaks pass is where that correction surfaced.

## The breaks pass

One line per entry, per break: escaped, duplicated, vacuous, fused. State why it does not break. The [four breaks](../doctrine/definition.md#the-four-breaks) are the whole failure space, so a design that passes all four for every entry holds the correspondence.

The pass is written or it is not a pass. A design read whole and judged clean by the modeler who wrote it has passed nothing; the same reading approved a vendor taxonomy as a domain vocabulary and a sync artifact as a domain state. Written per entry, the pass has to say "duplicated: no, `PartyName` is renamed not kept," and that sentence can be wrong on the page where a glance cannot.

## The output

```json
{
  "constructs": [{"name": "", "construct": "whitelist construct", "file": "domain/<context>/<file>.py", "fields": {"field": "Type"}, "equals": ["fields two equal on, full things only"]}],
  "holders": [{"file": "domain/<context>/<file>.py", "type": "existing type", "field": "existing field", "becomes": "Type"}],
  "removed": ["types and files that no longer exist"]
}
```

Discovery ends here. The build makes exactly this set. Anything the build wants that is not in the schema is a thing discovery missed, and it goes back to step two.
