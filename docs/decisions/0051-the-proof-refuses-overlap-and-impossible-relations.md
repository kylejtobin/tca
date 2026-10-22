# 0051. The proof decides from the relations' constraints and the scalars' bounds whether two union members can both hold and whether a relation can ever hold or ever refuse

Status: accepted

## Context

A choice is a union whose members each say fully what they are (0003). Two members that can both construct from one run would make Pydantic's smart mode the decision, silently, at run time. A relation whose operands' constraints make it certain or impossible is a rule that decides nothing.

## Rejected

Leaving disjointness to the developer's discipline and a test. A list of overlap rules in the engine, one per pair of kinds: it held the kinds' meanings in the engine, and it was wrong, since it called two relations of different kinds disjoint while `Equal` implies `AtMost`. A run-time refusal when two members are both present: a check on data that exists, made necessary only by a proof that stopped short.

## Decision

Every scalar class in a program is one variable, because a run holds one instance per class, and a derived value is a variable with no bounds. Every scalar's `gt`, `ge`, `lt` and `le` metadata on `root` are difference constraints against zero, and every relation's declared `constraints` (0048) are difference constraints between its operands. A system of difference constraints is feasible exactly when Bellman-Ford finds no cycle whose weights sum below zero, with a strict constraint on a zero-weight cycle counting below zero; `feasible(edges)` decides it. A relation never holds when its constraints and its operands' bounds are infeasible, and never refuses when the bounds with the negation of each of its constraints are infeasible, one at a time; `proven` raises `relation` at `(class,)` naming which. Two classes a field may hold can both hold when they are the same class, or when some choice of the classes each holds, through its single fields and their unions, puts in one run no two records one action hears and a feasible system; `proven` raises `overlap` at `(class, field)` for each such pair. A relation kind that declares no constraints is refused as `undecidable`, so the proof decides every union it accepts, and the run checks nothing.

## Evidence

With `SmallAmount` bounded `gt=0, le=100` and `LargeAmount` bounded `gt=100`: `Impossible(Beyond[SmallAmount, LargeAmount])` was refused as `relation` "never holds, by the constraints on its operands", `Certain(AtMost[SmallAmount, LargeAmount])` as "never refuses", and `Never(Equal[SmallAmount, LargeAmount])` as "never holds". `coexist(Cheap, Dear)`, told apart by `Low(AtMost[Amount, Limit])` and `High(Beyond[Amount, Limit])`, was false; `coexist(AtOrUnder, Exactly)`, told apart by `AtMost[Amount, Limit]` and `Equal[Amount, Limit]`, was true, and `Either.which: AtOrUnder | Exactly` was refused as `overlap` at `("Either", "which")`. `feasible` accepted `x - 0 <= 5` with `0 - x <= -5` and refused the same with `0 - x < -5`. `Same(Equal[Unit, One])` with `Unit` an `int` over 0 and under 2 and `One` an `int` at 1 was read as never refusing.

## Consequences

A wrong union is unwritable, and a union the proof cannot decide is unwritable too. The program's constraints are read by the proof, so a bound on a scalar is also a bound on every relation that holds it, and two facts told apart only by a relation the bounds decide are told apart by the proof. A scalar over `int` has no value between two integers, so its strict bounds are read as the next integer's non-strict ones and the solver is exact over integers; a derived value is unbounded, so the solver may fail to refuse a pair whose derived operands cannot meet, and it never refuses a pair that can. Refuted by an overlap the proof reports on a program whose members cannot both hold; none found.
