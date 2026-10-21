# 0051. The proof refuses a union whose members it can see both constructing, and a relation it can see never holding or never refusing

Status: accepted

## Context

A choice is a union whose members each say fully what they are (0003). Two members that can both construct from one run would make Pydantic's smart mode the decision, silently, at run time. A relation whose operands' constraints make it certain or impossible is a rule that decides nothing.

## Rejected

Leaving disjointness to the developer's discipline and a test. Refusing every union the proof cannot prove disjoint: two facts told apart by the records they hold, or by fields of different names, are disjoint in every run and the proof cannot read that, so it would refuse correct programs.

## Decision

The proof refuses what it can see, and reports nothing it cannot. `interval(cls)` reads the `Gt`, `Ge`, `Lt` and `Le` metadata on a scalar's `root` field as the interval the scalar admits. Two classes a field may hold are `overlapping` when they are the same class; two scalars whose intervals meet; two relations of one kind over the same operands; or two facts whose shared fields all overlap and whose unshared fields hold nothing selective, where a class is selective when it is a record, a relation, or holds one. Two records, two relations of different kinds, and two facts told apart by a selective field are not reported. `proven` raises `overlap` at `(class, field)` for each pair of members of a single field's union that overlap. For a relation kind, `never(cls)` reads the operands' intervals: `AtMost` never holds when the value's lower bound is above the bound's upper, and never refuses when the value's upper bound is at or below the bound's lower; `Beyond` the reverse; `Between` never holds when the value lies entirely outside either bound or the bounds cross, and never refuses when the value lies entirely inside; `Equal` never holds when the intervals do not meet, and never refuses when both are the same single point. `proven` raises `relation` at `(class,)` naming which.

## Evidence

The engine's shop with `Large` rewritten as `AtMost[LineTotal, Threshold]`, so that `Discounted` and `FullPrice` both hold an `AtMost` over the same operands under the field `tier`, was refused at startup with exactly `overlap` at `("Charge", "priced")` and `("LinePaid", "priced")`; the shop as written, with `Large` as `Beyond`, was accepted. With `SmallAmount` bounded `gt=0, le=100` and `LargeAmount` bounded `gt=100`, both carried by the catalog's record: `Impossible(Beyond[SmallAmount, LargeAmount])` was refused as `relation` "never holds, by the constraints on its operands", `Certain(AtMost[SmallAmount, LargeAmount])` as "never refuses", `Never(Equal[SmallAmount, LargeAmount])` as "never holds", and `Outside(Between[LargeAmount, SmallAmount, SmallAmount])` as "never holds".

## Consequences

A wrong union the proof can see is unwritable; one it cannot see is the developer's, and the records say which. The program's constraints are read by the proof, so a bound on a scalar is also a bound on every relation that holds it. Refuted by an overlap the proof reports on a program whose members cannot both construct; none found.
