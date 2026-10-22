# Architecture

A program is nothing but a true description of a business, and it runs because it is true. This document says how that is made mechanically true: what the engine knows, how the proof places every class, how a run constructs the same classes as instances, and where the boundaries are. Every value in it was produced by a run of the code at this revision over the program the engine's tests are, `packages/python/type-construction-engine/tests/type_construction_engine/test_engine.py`, whose classes are named for what they are to the framework: an `Element` the request holds several of, a `Heard` record a `Party` says about it, a `Low` or `High` relation against a constant `Limit`, a `Cheap` or `Dear` conclusion, a `Total`, an `Answered` reply, an `Operation` route.

## One source of meaning

The developer's classes are the only source of meaning. The engine has three verbs: read a class, ask Pydantic, refuse. It reads each class's fields once, through seven reads over `model_fields`, `model_computed_fields` and the generic parameters:

| read | what it answers |
|---|---|
| `holds(cls)` | each single field and the classes it may hold |
| `collects(cls)` | each tuple field and the classes an element may be |
| `premises(cls)` | the required single fields the scope must hold before the class is asked for |
| `declares(cls)` | the element classes a request or a record holds as tuples |
| `heard(action)` | the record classes an action declares as `Action[P, T]` |
| `carried(cls)` | the scalars and values a request, a record or a value brings with it |
| `produces(cls)` | the classes a computed field constructs as words |

Nothing else is known about a program. The proof and the run are the same construction read at two levels: the proof places classes, the run constructs instances, and a premise is satisfied in the first by a placed class and in the second by a present instance.

Each kind declares its meaning once, as something Pydantic reads, so the proof cannot decide from a second description of a rule:

- A relation is the restriction of one shared comparison to the orderings it admits. `AtMost[A, B]` is `Compare[A, B, Literal[-1, 0]]`; `Beyond` admits `1`; `Under`, `Equal`, `AtLeast` and `Differs` admit `-1`, `0`, `{0, 1}` and `{-1, 1}`. The ordering field carries a `Comparison` of two operand fields as its `default_factory`: Pydantic computes the ordering from the validated operands and admits it through the `Literal` or refuses it with `literal_error`. The proof reads the same field: the operands and the admitted set.
- A selection's shape is its tuple annotation: `tuple[E, ...]` with `min_length=1` for `Least`, `Greatest` and `First`, `tuple[E]` for `Only`. Pydantic refuses the wrong count; the proof reads the count from the annotation.
- A derivation declares one `Derived` operation as the `default_factory` of its `root`: `Times` multiplies, `Sum` adds. Pydantic computes and validates the root at construction; the proof applies the operation's interval to the operands' intervals.
- A constant is a scalar with a default root; a fresh scalar, `Instant` or `Identity`, has a default factory. A record union is told apart by a `Literal` field or a required key.

## The proof

A placement is a path of element classes. `()` is once per run; `(Element,)` is once per element; `(Element, Part)` is once per part of each element. The proof's passes ask `place` for every class not yet placed:

- the request, what it carries, the connections and the constants are placed at `()` before any pass;
- an element is placed one level under the request or record that declares it, and what it carries with it;
- a record is placed where its hearer is;
- a scalar or value is placed where its carrier is, a word where its holder is;
- every other class is placed at the finest placement its premises name, which every other premise's placement must be a prefix of, and one level above each class it collects, which must be exactly that level.

The passes stop when a pass places nothing, and `Proof` is constructed from the placements, what was left waiting, and the faults found while placing. `Proof` is a Pydantic model; its validator reads every fault from those fields and the declarations and refuses the program with one `ValidationError`, each error with a `type`, a `loc` whose first element is the class, and a message in the developer's names. For the test program it placed:

```
()               Elements, Limit, Total, Concluded, Answered, Operation
(Element,)       Element, Name, Asked, Heard, Amount, Portions, Largest, Low, High, Notify, Noted, Cheap, Dear
(Element, Part)  Part, Share, Portion
```

The faults, each one read:

| type | what it names |
|---|---|
| `missing` | a field that holds a class with no source: `no class fills Concluded.unheard, which holds Unheard` |
| `cycle` | classes that wait on each other and nothing else explains |
| `twice` | a class with two sources: `Name has 2 sources: carried by Element, carried by Heard; exactly one` |
| `unplaceable` | a class whose fields name sibling elements |
| `collects` | a tuple over a class placed once per run, or more than one level down |
| `route` | a route whose reply would exist once per element |
| `unreached` | a class no route's reply leads to, through fields, carriers, hearers and declarers |
| `unmodeled` | a bare primitive anywhere, an enumeration on a fact, `None` or a `Literal` outside a record |
| `boundary` | a request or value that holds what does not arrive; a config or connection that holds a business value |
| `config` | no one `Config` |
| `ambiguous` | two union members the proof cannot show exclusive |
| `never` | a relation its operands' intervals make certain or impossible |
| `undiscriminated` | two records one action hears that no field tells apart |
| `undecided` | an action performed on one branch of a choice that holds nothing deciding it |

Two of these are reasoning rather than reads, and they are the only algorithms in the engine. A relation's possibility is decided from intervals: a constant is its default exactly, a scalar is its `Field` bounds, a derivation is what its operation makes of its operands' intervals, and `outcomes(left, right)` says which orderings two intervals allow; `Low(AtMost[Amount, Limit])` with `Amount` above 0 and `Limit` at 10 allows `{-1, 0, 1}`, so it is neither certain nor impossible, while `Beyond[SmallAmount, LargeAmount]` with the first at most 100 and the second above 100 allows `{-1}` and never holds. Two union members are exclusive when every choice of what each holds conflicts with every choice of the other: two records one action hears, two relations whose comparisons over the same operands admit disjoint orderings, two selections with disjoint counts, or intervals and comparisons that have no solution together, which Bellman-Ford over difference constraints decides. Both are sound in the direction the proof refuses: infeasibility of an over-approximation proves infeasibility, and a pair the proof cannot prove exclusive is refused as one it cannot decide.

The `undecided` fault is what makes an effect on a branch safe without a scheduler. `Notify` is performed when `Dear` holds and not when `Cheap` holds; it holds `High`, which contradicts the `Low` that `Cheap` holds, so it holds a decider and the proof passes. A `Charge` that held only the element would be performed whichever held, and the proof refuses it at startup, naming it.

## The run

A run is a tree of scopes with the shape the proof placed. A scope holds its own instances over its ancestors', as a `ChainMap`, and one list of child scopes per element class, in element order. The root holds the request, what it carries, the connections and the constants. When a request or a record enters a scope, each tuple it holds fans out: one child scope per element, holding the element and what it carries; an element class with no element gets an empty list.

A pass visits every scope and asks Pydantic for every class of the route placed there and not yet present whose premises are present, `cls.model_validate(supplied)`: each single field is the present member, a fresh scalar is constructed for the holder, and a tuple field is every child scope's instance in element order once every child holds one, the empty tuple for no element. A relation or a selection that refuses is refuted in that scope and asked again next pass; any other refusal propagates. The pass's actions are performed together in one `TaskGroup`, and each record enters the scope its action was built in and fans out its own elements. The run ends when the route constructs. Provenance is inheritance: everything built inside an element's scope shares that element by being there, and no join is computed, keyed or matched.

Two elements the party values at 2.50, each in two parts of a half:

```
pass 1   (Element,)        Asked built and performed; Heard enters each element's scope; parts fan out
pass 2   (Element, Part)   Portion 1.250
         (Element,)        Low holds (ordering -1); High refuted
         ()                Total 5.00
pass 3   (Element,)        Portions 2.500, Largest 1.250, Cheap
pass 4   ()                Concluded, Answered, Operation
```

`tca.passes` is 4 and the reply is `{"total":"5.00"}`. With the party saying 25 in one part, `High` holds with ordering 1, `Notify` is performed, `Dear` holds the `Noted` record whose word is `dear`, and the reply is `{"total":"25"}`. With no element, `valued` is the empty tuple and `Total` is 0.

A pass that constructs nothing raises one `ValidationError` naming why. A refuted relation whose complement holds in the same scope is left out, since that choice was decided; the rest are named with what was observed, rendered from the ordering field's operands and the error's input: in a program whose only outcome is `Cheap`, the party saying 25 gives `Low did not hold: value Amount > bound Limit`. A selection with nothing to choose gives `Largest did not hold: Tuple should have at least 1 item after validation, not 0`.

`model_dump` of the reply is the derivation of the answer: a fact holds the facts it was concluded from, down to the record a party said, so the explanation of every answer is the answer. A word of a reply is a computed field, evaluated when the reply is serialized; a word that refuses refuses there.

## The boundaries

The command line is the request's type. One subcommand per route, named from the route class; the options read from the request class through `holds` and `collects`: a scalar is one option with its class name as the metavar, its docstring as help and its root's bounds after it; a value is dotted options; a tuple repeats, taking one JSON object per value. The parsed options are read back into a tree by the same reads and the request is constructed with `model_validate(tree, strict=False)`, the lenient mode for a text edge. For a request holding a name, a count, an amount, an enumeration, a value and two tuples, the help reads:

```
  --name NAME        The thing's name. (min length 1)
  --count COUNT      How many. (> 0)
  --amount AMOUNT    What is offered. (> 0)
  --kind {one,two}   Which kind.
  --place.city CITY  The city it goes to. (min length 1)
  --tags TAG         Words attached. (min length 1)
  --each JSON        The elements, any number.
```

and the answered route prints `{"name":"tea","words":["yes","yes"]}`. The program is proven once at startup, and the proof is passed with the deployment to every answer; the proof's `boundary` fault is what makes every accepted request renderable. The HTTP boundary is the same request from a body, `model_validate_json`, and is the second item of `TODO.md`.

Connections are opened once at startup and closed once at shutdown around every answer, last opened first, and a connection that fails to open closes what opened before it. Every answer is one OpenTelemetry span named for the route with one child per performed action, carrying class names and counts and never contents.

## What this rests on

- *Propositions as types* (Wadler): a kind is a proposition, an instance is its proof, and `model_dump` of the reply is the normalised proof. The engine is forward-chaining proof search over the developer's propositions.
- *Consistency as logical monotonicity* (Hellerstein, Alvaro) and *LVars* (Kuper, Newton): the run's state is a set of instances under union, every step is monotone, readiness is a threshold read, and the result is the same under every schedule, so the engine computes no order. A collection is complete when its child scopes have returned, the one wait in the engine, and it is structural.
- *Provenance semirings* (Green, Karvounarakis, Tannen) and why-not provenance (Lee, Ludäscher, Glavic): a placement is a path over element classes, a child scope inherits its parent's instances plus one element, and a stall names the premise or the refusal that was missing.
- *Build systems à la carte* (Mokhov, Mitchell, Peyton Jones): a restarting scheduler and no rebuilder; each pass re-asks every class not yet built and nothing persists between runs.
- *Out of the tar pit* (Moseley, Marks): the only state is the instances and the only control is refusal.
- *Parse, don't validate* (King): a request and a record are the two boundaries where Pydantic parses, and nothing downstream checks.

## What is procedure

The two loops, the proof's passes and the run's passes; `opened`; and inside the proof's validator, the interval arithmetic and the solver. Everything else in the engine is a read of a declaration or a call to Pydantic, and a class the engine defines is a value: `Placement`, `Waiting`, `Fault`, `Proof`, `Scope`.
