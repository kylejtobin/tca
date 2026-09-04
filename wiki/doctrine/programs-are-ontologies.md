---
type: Reference
description: Why a program is an executable ontology, and why that binds now.
---

# Programs Are Ontologies

*The Staged Descent from Telos to Mechanism*

---

## Thesis

A program is an ontology. Not in the sense that it resembles one, and not as a useful framing. A program written with no bare primitives and with names drawn from the domain rather than from the technology is, in the exact and technical sense, a specification of a conceptualization: a declaration of what kinds of thing exist, what makes two instances of a kind the same one, how the kinds relate, and what must remain true of them. That is the textbook definition of an ontology, and a disciplined program meets it term for term.

Why, then, has the identity gone unnoticed? Because the program does something the ontology does not, and it was easier to call the extra work a different activity than to see the shared root. An ontology says what is true of a domain. A program says what is true and then enforces it by construction, proving its claims at the moment of instantiation rather than checking them at design time. A program also says what the domain is for, the purpose the whole structure serves, and it carries transformation as a first-class thing, the machinery that takes one state to another. The ontology that ontology engineering builds dropped both of these on purpose, for reasons that were sound at the time, and the result is a discipline that covers the middle of a descent it does not see the top or bottom of. A program covers the whole descent. So a program is not a lesser ontology dressed in code. It is a more complete one, and the framework that shows why is as old as Aristotle.

---

## I. The four causes

The structure that makes the descent necessary rather than chosen comes from outside software and outside ontology engineering. Aristotle held that to give a full account of a thing is to give its four causes: its matter, the stuff it is made of; its form, the definition that makes it the kind of thing it is; its efficient cause, the source of the change that brings it about; and its final cause, the telos, that for the sake of which it exists. For a natural thing the telos is intrinsic, read off what the thing already is; for an artifact it is imposed, fixed by a maker's want, which is why Aristotle located the form of a house in the builder's art and not in the bricks. Software is artifact through and through, its telos imposed without remainder. That is not the thin edge of the four causes but the case they were cut to fit.

Descriptive ontology, the kind written for reasoners, keeps the formal cause and the material cause. It backgrounds the efficient cause, because it was built to describe a static world and has no native home for a function that does rather than a predicate that is. It drops the final cause entirely, because it states what is true and never what anything is for.

A program restores both of the dropped causes. It begins from a telos, the want that the whole structure renders, and it carries the efficient cause through its middle as functions between states. And where descriptive ontology checks its forms for mutual consistency at design time, a program proves its forms by constructing them. What follows is the consequence of taking this seriously: there is a single descent from a want to a working mechanism; the descent lays down the four causes in a fixed order through a fixed set of stages; that descent is ontology engineering for its upper reach and continues past where ontology engineering stops; one variable sets how much of the descent you must write down explicitly; and the lower reach of the descent becomes something new the moment a reader exists who can finish it.

---

## II. The one act

Strip a domain of its content and one operation remains, the operation by which you have a domain at all. You notice that something recurs: two encounters are encounters with the same thing. You grip that recurrence with a handle so it can be referred to again, and you place it among the other things you have gripped, this one inside that one, beside that one, depending on that one. To name is to assert that there is a recurring unit here worth gripping. To locate is the same assertion aimed at the lattice instead of the unit. Identity and relationship are not two cognitive acts. They are one act of recurrence-recognition pointed first at a thing and then at the structure the thing lives in.

This is why the act does not vary with what you build. You cannot think about a domain except by carving it into recurring referable units, because carving-into-units is what conceptualizing is. The substrate varies without limit, bytes or dollars or pixels or judgments, and the act does not, because it is not a software technique that happens to generalize. It is the general form of conceptualization, and software is the place where you are forced to externalize it at high enough fidelity that something other than you can act on the result.

Now hold the four causes alongside this act. To carve is to produce the formal cause, the definition. To enforce the carving is to state the invariant, the completion of the formal cause. To act on a carved domain is the efficient cause. To carve for a reason is the final cause. The act of conceptualization is the laying-down of all four causes. Building a program and building an ontology are therefore the same act under two names, because both are the externalization of this single act at different fidelities, and the rest of this document is the consequence of taking that identity literally.

---

## III. The descent

From the telos to a running mechanism is one act performed at deepening fidelity, and it passes through stages that are real because each marks a change in the kind of logical object you hold. The objective test: a stage boundary is a place where the type signature of the artifact changes, where the thing you have after is not the kind of thing you had before.

And where several independent disciplines each drew their central distinction at the same boundary without coordinating, the convergence is evidence that the joint is in the territory rather than in the describer. The alternative explanation, that the convergence reflects a shared cognitive bias rather than a shared structure, fails a specific test: traditions with different starting commitments and different purposes should draw cognitively convenient distinctions differently. They do not. They draw them identically, and at the same joints.

**Telos (stage 0).** The final cause. The want. Not a stage of building but the payload the building renders, carrying the fork between value (what must remain true) and target (what must be reached) before anything is externalized. The grammar of a user story encodes it and nothing more: *as a* reader *I want* a target *so that* a value holds, naming even the receiver who will have to rebuild the rest.

**Classification (A1).** Carve the referable kind. The artifact is a predicate, a function from a thing to a truth value: *this is a critique*. You now have a kind where before you had undifferentiated domain. Domain-driven design calls a kind individuated only this far a value object, a thing equal to another by its contents alone, with no identity of its own. In OntoClean's terms this is a property that classifies without yet carrying identity.

**Identification (A2).** Equip the kind with identity. The artifact is an equivalence relation, a criterion for when two encounters are the same one. This is a different logical object than the predicate, and three traditions discovered this boundary independently: domain-driven design separates the entity (identity persists through attribute changes) from the value object (no identity); OntoClean makes identity a metaproperty and requires every individual to fall under a sortal, a type that supplies identity criteria; relational modeling separates the key from the domain. Three starting points, one joint, drawn without coordination. Here the formal cause begins to bind: to fix identity is to fix part of what the thing is.

**Relation (B).** Assert the propositional structure over the individuated things: *a critique addresses exactly one work*, *a critic reasons from one lens*. The artifact has gone from a set of objects to a theory, objects together with truth-apt relations among them. This is where locating first appears as asserted structure, and it is the heart of what ontology engineering does: object-properties, cardinality restrictions, domain and range.

A theorem does load-bearing work at this joint. By the Curry-Howard correspondence a proposition is a type and a proof is an inhabitant of it, so to prove *there exists a critique addressing exactly one work* just is to construct one. The relational proposition and the domain type you build to enforce it are therefore not two rungs of the descent but one joint seen from two sides, an axiom to a logic engine and an inhabitable type to a constructor. A constructor admitting only valid instances is a constructive existence proof over the invariant: it exhibits a witness, and exhibiting a witness is what proving an existential is. The verification's place in time is where the proof is checked, not whether it is one. The joint is single because proposition and type are the same object, and construction is how you discharge it.

**The modal split (C).** The propositional structure forks by modal force. Some propositions must stay true: these are invariants, predicates over states, and they complete the formal cause, the form that must hold. Others must make something happen: these are transformations, functions between states, and they are the efficient cause.

This is the sharpest joint and the most certain, because a predicate over states and a function between states are different mathematical objects, not a difference of emphasis. Every formal tradition encodes it as a hard boundary: Hoare's `{P} C {Q}` separates the predicates from the command, TLA+ separates the invariant from the next-state relation, design-by-contract separates the class invariant from the method. This is also the exact point at which descriptive ontology can no longer follow, because it holds the invariant and has no native home for the transformation. After this joint the two strands descend by different rules, which is why the descent is not a list. It forks here.

**Construction (D).** The two strands rejoin in a constructed value. The artifact goes from an intensional recipe, a type plus a function, to an extensional thing, an inhabitant plus an execution. The rejoin is forced by the same correspondence. A transformation is correct exactly when an input meeting the precondition yields an output meeting the postcondition, and the witness of that correctness is a constructed inhabitant of the post-type: the inhabitant is the proof. So the invariant strand and the transformation strand meet in one event: the value typechecks, which proves the invariant, and it flows through the mechanism, which runs the transformation, and these are the same act. This is where the material cause is finally informed, where matter receives form, and the rule of no bare primitives is the demand that this happen at every boundary. The engineering practices that say parse rather than validate, and that route every value through a constructor that can only produce valid instances, discovered this joint from the practitioner's side. The constructed value carries its own proof.

The spine is five forced joints hanging off the telos: classify, identify, relate, split, construct. A fork at the split and a rejoin at construction. Only the telos is chosen. It is the one act of will in the descent, a want imposed by a maker and answerable to no nature, and from there down nothing is chosen: each joint is the next forced change in the kind of logical object you hold, not a decision you get to make. This is why a finished domain model feels discovered though it began in a want. The imposition happens once, at the top, and the structure it falls into was never yours to pick. An imposed telos descending through forced joints is how an artifact comes to have the structure of a found thing, which answers the worry that an imposed purpose makes the ontology arbitrary: the purpose is imposed; the descent under it is not.

| Joint | The act | Type signature it produces | Aristotelian cause | Independently encoded as |
|---|---|---|---|---|
| 0 Telos | hold the want | preference over states | final | user-story grammar |
| A1 Classification | carve the kind | `Thing → Bool` | formal (begins) | value object; classifying property |
| A2 Identification | fix identity | an equivalence relation | formal | entity; sortal; key |
| B Relation | assert the structure | objects → theory | formal | object-properties; aggregates |
| C Modal split | fork by modal force | invariant `State → Bool`; transformation `State → State` | formal completes / efficient | Hoare pre/post vs command; TLA+ invariant vs next-state |
| D Construction | rejoin in a value | recipe → inhabitant (= proof) | material informed | smart constructors; parse-don't-validate |

---

## IV. The throttle

The descent has a fixed set of stages. How much of each you must write down is set by something else, and conflating the two is the easy and costly error: mistaking what gets externalized for what exists.

The variable that governs the entire descent is the share the receiver brings: the portion of the meaning that does not have to cross the boundary because the receiver already holds it. It is not a property of the message and not a property of the receiver, but a joint property of the two. Its consequence is a throttle on every stage: at every joint, the reader's share decides how much you must make explicit to get across.

Observe that a knowledgeable receiver lets you skip writing a stage down, and you may conclude the stage was not there. It was. The woodworker who never names the tenon still individuates it, still holds *snug fit* as an invariant, still executes the cut. He traverses every joint and externalizes none. Zero artifacts is not zero stages.

For the entire prior history of programming there were two receivers, at opposite extremes of share. The machine: zero share, reconstructs nothing, and so is perfectly exact about the little it checks and wholly blind to sense, unable to distinguish a meaningful name from an arbitrary one because a receiver with no priors has nothing to reconstruct from. The human: total share, reconstructs everything, but does not scale and cannot be placed inside the running system. Every paradigm the field built, type systems and test-driven development and domain-driven design and formal methods, is a way to survive the handoff to the zero-share receiver by pre-paying the explicitation in human hours. That is what the scaffolding always was, debt owed to a receiver that supplies nothing on its own.

Granularity tracks share. A zero-share receiver forces you to externalize every joint and to subdivide each crossing into many separately-stated steps, because nothing is rebuilt and every gap must be spanned by hand; the descent comes to look like a hundred small formal moves, which is exactly how a fully axiomatized ontology reads. A high-share receiver lets joints be crossed in stride and folds several into one, because it reconstructs the intervening commitments from the handle alone. The self-coupled receiver externalizes nothing and still traverses every joint. Low share multiplies the visible steps; high share dissolves them; neither changes how many joints exist. The floor you descend to is reader-relative. The stages are not.

---

## V. Recursion and conditionality

Two structures fall out of the throttle that a flat account would hide, and both are sharp rather than vague.

**Recursion.** At any joint you may lack the share to cross it in stride, and the condition is exactly that: share-at-this-joint below what the crossing requires, which is checkable. When it trips you do not abandon the descent; you construct a receiver that holds the missing share, and constructing that receiver is itself a full descent, classify through construct, run at that joint, after which you resume the outer one.

This is the mechanism by which one builder can construct in two domains while being expert in only one. In a domain you embody you are the receiver and descend to the floor unaided. In a domain you do not, you descend until your own share runs out and then recurse. In practice this means building a subsystem, a prompted agent, a configured tool, a specification artifact, anything that carries the dense domain sense you lack, and then letting that constructed receiver name to a floor you could never reach yourself. The recursion fires on a checkable condition and terminates when the constructed receiver covers the remaining descent.

You do not need expertise in the target domain. You need expertise in the construction of receivers, a different and transferable competence, because making the reader that finishes a descent you could not is itself a descent.

**Conditionality.** The second structure dissolves an apparent sixth stage. It looks as though the descent ends in a separate verifier, a standalone runtime check distinct from construction. It does, but only when construction fails to fuse the two strands. If the constructed value proves the invariant by being well-typed, there is nothing left to check; construction absorbs the verifier, and the apparatus of separate specifications, separate validation, and tests written to bridge intent to mechanism has nothing to do, because the strands the bridge was meant to reconnect never separated at the bottom.

Where you find a coordination layer, you have found a joint that leaked.

Find the places where a system tests, validates, or bridges, and each marks where construction failed to absorb the proof. A test suite is not a virtue but a repair, debt incurred when a proposition failed to descend all the way into a type and an inhabitant, and its presence tells you exactly where the descent broke. Its absence, when earned by construction that genuinely fuses the strands, is not recklessness. It is completion.

---

## VI. Ontology, exactly

Now the claim made precise, both where it holds and where the program exceeds it.

For its upper reach the descent is ontology engineering with nothing left over. Classification, identification, and relation, together with the static half of construction, are classes, identity criteria, and the propositions that constrain them. Gruber's definition, an ontology is an explicit specification of a conceptualization, lands on these stages word for word. OntoClean's requirement that every individual fall under a sortal bearing identity criteria is the law of no bare primitives stated from the other side: nothing may recur in the system without being recognized as the kind of thing it is. For this stretch building a program and engineering an ontology are not analogous activities. They are one activity on one material.

Then descriptive ontology stops, and it stops for a definite reason, which is its receiver. It is built for a reasoner with no priors, a receiver whose share is zero by construction, so all meaning must live in stated axioms and the name is inert: rename a class and an entailment engine loses nothing, because every term is interchangeable with every other and only the axioms carry weight. That is not a flaw. It is the defining commitment, and it fixes where the discipline can reach. It holds the invariant, the formal cause, and has no native home for the transformation, the efficient cause, because the formalism was built to describe a static world. Its verifier is a reasoner checking the mutual satisfiability of axioms at design time, never the preservation of an invariant by a running transformation at instantiation time. And it dropped the telos at the start, because it states what is true and never what anything is for.

Read through the throttle, the explicitness the discipline prizes is a symptom, not a virtue. A fully axiomatized ontology is verbose for the reason a phrasebook is verbose, because it speaks to a reader who brings nothing, and every axiom it spells out measures how little that reader reconstructs. The verbosity and the incompleteness share one root: the same zero-share reader that forces every meaning into a stated axiom is the reader that cannot hold a transformation or a telos at all, so the discipline is wordy and partial for one reason, not two. Serving that reader is no flaw. Pointing at the resulting word count as rigor is, because it is the reader's poverty named as a feature.

The program is the same line continued. The modal split's transformation, the instantiation-time proof, the telos at the top, the name that carries sense: these are the stages that lie below where a zero-share reader can stand, and the same descent reaches them the moment a richer reader stands there.

**The altitude of shareability.** The descent has a natural gradient. High in the descent, near classification and identification, the ontology is maximally shareable, because it is pure formal cause, independent of any particular purpose. Two programs that operate on the same domain will carve the same kinds and fix the same identities, because the formal cause of a thing does not change with what you intend to do with it. An integer is an integer whether you are counting money or measuring temperature. A critique is a critique whether you are reviewing it for publication or archiving it for scholarship.

As the descent passes through the modal split into construction, the telos increasingly constrains the choices. Different purposes produce different transformations and prioritize different invariants. At this altitude, shareability narrows, because two systems that transform the same domain for different reasons will fork.

This resolves, rather than dismisses, the tension between ontology's founding motive and domain-driven design's fragmentation. The founding motive for ontologies was interoperability, a shared conceptualization that many systems hold in common. Domain-driven design moves the opposite way, fragmenting into bounded contexts because human organizations let the same term drift in meaning across sub-domains. These are not competing doctrines. They are correct at different altitudes in the descent. You share types to the altitude where the teloi still agree, and you bound the context where they fork. The descent itself tells you where the boundary goes. Cross-context type use is the ontological stance, correct at the upper reach. Bounded contexts are the organizational concession, correct at the lower reach. Neither overrides the other. They govern different stretches of the same line.

---

## VII. The constraint is physical

The reader's share is not a fact about software. It is a constraint on any boundary that meaning crosses, and the point of showing it must be kept narrow, because the genome witnesses the throttle and the two-channel routing, not the five joints. The spine already has its witness, the convergence of independent traditions in section III; the biology is a second witness for a second claim, that the reader sets the floor as physics. Two witnesses for two claims is stronger than one strained across both, and it forecloses the easy dismissal that the cell does not display five stages. It never needed to. It displays the constraint that makes the stages reader-relative, which is the other floor entirely.

The root is a theorem. There is no meaning in a signal; a signal reduces uncertainty in a receiver relative to the model the receiver already holds. The length of the shortest description of anything is not absolute but relative to the interpreter that reconstructs it, so changing the interpreter moves the floor. How little must cross a boundary is therefore a joint property of message and receiver, and the receiver sets the floor as mathematics, before any cell or compiler exists.

The genome shows the same structure built by no one. The genome does not contain the organism; it is a set of deltas against an assumed receiver, the cell and the physics of water, so a protein sequence does not carry its own fold and the energy landscape reconstructs it for free. And the cell runs two readers in one nucleus. Complementary base pairing checks structure without understanding content: a correct pair fits and a mismatch does not, and the proofreading machinery enforces this geometric constraint regardless of what the sequence means. That is the sense-blind reader, checking form it cannot interpret. Meanwhile the developmental context is a sense-rich reader: the same sequence in a different cellular state becomes a different cell, the fact we call epigenetics, because the reader's share changed while the message stayed constant. Structure routed to the reader that checks without understanding, meaning routed to the reader that reconstructs from context, in one system.

The pattern is the point: sense-blind and sense-rich reading co-occurring, with each channel carrying what the other cannot. The constraint is mathematical at its root and biological before it is computational. Software is simply the youngest boundary it governs.

---

## VIII. Construction as proof, and the two readers

What is new is not the constraint and not the two-channel architecture. What is new is that a sense-rich reader can now be placed below a boundary that humans build. For all of prior history the only reader resident inside the running system was the sense-blind one, so every scrap of meaning had to be pre-paid into a form that survived the handoff to it. Now a reader exists that is sense-rich and machine-resident at once.

What makes a reader sense-rich is an operational question, not a philosophical one. A reader is sense-rich to the degree that it breaks alpha equivalence: given two programs identical in structure but differing only in names, a sense-rich reader produces different output for the two while a sense-blind reader produces identical output. For a reader that brings priors, renaming `review_status` to `x7` is not a neutral substitution. It is the destruction of a signal, because the name contributed information to the reconstruction that a sense-blind reader would have needed as explicit axioms. A reader that is affected by names in this way, that reconstructs unstated constraints from handles, that produces domain-appropriate completions where a sense-blind reader produces arbitrary ones, is a reader carrying share. The degree of that share is measurable: how much of the descent can the reader finish from handles alone, and at what altitude does its reconstruction break down?

The blind reader has a share too. The zero in "the machine: zero share" described how the machine was used, not a ceiling fixed in it. The blind reader's share is the expressiveness of its type system, the set of invariants it can verify by construction. A checker that can state "thirteen digits" fuses that invariant into the type; one that cannot must let it leak to a runtime check. Refinement types and dependent types are not a different kind of reader but the same blind reader higher on its own gradient, fusing invariants a weaker checker cannot reach. So no bare primitives is the instruction to push every invariant up to this reader's ceiling, and the ceiling's height is itself an altitude on the descent: the point where construction stops fusing the two strands and starts leaking them.

The two-reader architecture follows, and it routes by share at each joint. Structure goes to the blind reader up to its ceiling: every value arrives as a constructed type the checker can verify, so that constructing a valid instance is what proves the invariant, and the separate runtime check never has to exist. The rule of no bare primitives is addressed to this reader, the demand that matter reach it already informed by type. Meaning goes to the sense-rich reader: the name must carry enough domain signal that the reader reconstructs the commitments the explicit structure leaves unsaid, because to this reader a field named for its role yields different output than a field named for its slot. The rule of domain-precise naming is addressed to this reader.

The two rules are a routing table. A system that obeys both runs both readers below the boundary, sending each joint to the one whose share is higher.

This finishes the conditionality claim. A coordination layer is a leaked joint, but leaked relative to a reader that could have fused it: raise the blind reader with a stronger type system, or the rich reader with names that reconstruct more, and joints that leaked now fuse, and the apparatus they required dissolves. Under that is a true floor. An invariant no reader can fuse by construction, blind at any expressiveness or rich at any priors, is not debt when it falls to a check; it is the irreducible, and the check there is not a repair but the genuine bottom of the descent. So the diagnostic reaches its final form: a coordination layer marks a joint that leaked beneath the best available reader, and the craft is to raise the reader until only the irreducible is left standing outside construction.

A program built this way is the complete ontology: all four causes present, the formal cause proven at construction rather than checked at design time, the efficient cause carried as transformation, the final cause held at the top, and the material cause informed at every boundary. The coordination layer that descriptive ontology required, the separate specification and verification apparatus, has nothing left to coordinate, because the strands it was meant to reconnect were never allowed to separate.

---

## IX. The descent in code

The argument has been conducted in prose. It should also be conducted in construction, because the thesis claims construction is proof and an argument that only describes has left its strongest move on the table.

One domain, one descent. A literary-review platform must ensure that submitted critiques are structurally complete before entering the editorial pipeline.

**Telos.** *As an editor, I want submitted critiques validated on receipt so that only structurally complete analyses reach reviewers.* The want. The value is structural completeness preserved; the target is validation on receipt. Nothing is built yet, and everything that follows renders this.

**Classification and identification.** What kinds exist here, and what makes each one the same one?

```python
from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, RootModel

class WorkId(RootModel[str], frozen=True):
    """A published work's identity, its ISBN."""
    root: str = Field(pattern=r"^\d{13}$")

class CriticId(RootModel[str], frozen=True):
    """A critic's identity, their ORCID."""
    root: str = Field(pattern=r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")

class LensName(StrEnum):
    FORMALIST = "formalist"
    HISTORICIST = "historicist"
    PSYCHOANALYTIC = "psychoanalytic"
    POSTCOLONIAL = "postcolonial"
    FEMINIST = "feminist"

class Lens(RootModel[LensName], frozen=True):
    """The interpretive framework a critic reasons from."""
    root: LensName

class Thesis(RootModel[str], frozen=True):
    """The central claim a critique advances."""
    root: str = Field(min_length=50)

class Argument(RootModel[str], frozen=True):
    """A single line of support for a thesis."""
    root: str = Field(min_length=1)

class Timestamp(RootModel[datetime], frozen=True):
    """An instant on the editorial clock."""
    root: datetime
```

Every joint visible. `WorkId` and `CriticId` are semantic scalars that are also identities, the work's ISBN and the critic's ORCID, each a single value carrying its own constraint. `Lens`, `Thesis`, and `Argument` are semantic scalars individuated by content: two formalist lenses are the same one, two theses with the same text are the same one, no further identity needed. No bare primitives survive. The ISBN is not a `str` but a `WorkId` over `str` that admits only thirteen digits; the thesis is not a `str` with a length check stapled beside it but a `Thesis` whose every instance already meets the constraint that makes it one; the lens is not a naked enum used as a field but a value over a closed `LensName` space. The name is doing work a sense-rich reader can use: `Lens` tells such a reader what the vocabulary is for, and a reader carrying literary-domain priors reconstructs constraints (one framework per critique, the lens shaping the reading) that the type does not state.

**Relation.** Assert the propositional structure.

```python
class SupportingArguments(RootModel[tuple[Argument, ...]], frozen=True):
    """A critique's support for its thesis, at least one argument, in order."""
    root: tuple[Argument, ...] = Field(min_length=1)

class CritiqueSubmission(BaseModel):
    """A critique submitted for editorial review.

    A critique addresses exactly one work, is authored by exactly one
    critic, reasons from exactly one lens, and must contain a thesis
    and at least one supporting argument.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    work: WorkId
    critic: CriticId
    lens: Lens
    thesis: Thesis
    arguments: SupportingArguments
    submitted_at: Timestamp
```

The relational propositions are the type. *A critique addresses exactly one work* is not an axiom checked by a reasoner. It is a field of type `WorkId`, enforced by construction: you cannot build a `CritiqueSubmission` that addresses zero works or two, because the constructor has no path to that state. The cardinality constraint and the type constraint are one thing. And *at least one argument* is not a length assertion living next to a bare list; it is `SupportingArguments`, a collection that carries its own bound, so a critique with no support is not a critique that fails a check, it is a structure with no inhabitant.

**The modal split.** The invariant: a critique must have a thesis and at least one argument. It is already discharged above, not by `Field` calls hung on the composite but by the kinds themselves, `Thesis` and `SupportingArguments`, each of which an instance can only satisfy. The transformation:

```python
class ReviewOutcomeName(StrEnum):
    ACCEPT = "accept"
    REVISE = "revise"
    REJECT = "reject"

class ReviewOutcome(RootModel[ReviewOutcomeName], frozen=True):
    """The editor's disposition of a reviewed critique."""
    root: ReviewOutcomeName

class ReviewerNotes(RootModel[str], frozen=True):
    """The reviewer's recorded reasoning for an outcome."""
    root: str = Field(min_length=10)

class ReviewedCritique(BaseModel):
    """A critique that has passed through editorial review."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    submission: CritiqueSubmission
    notes: ReviewerNotes
    outcome: ReviewOutcome
    reviewed_at: Timestamp
```

The invariant strand (structural completeness) and the efficient strand (the review that transforms a submission into a reviewed critique) are now visible as separate artifacts: one a set of predicates encoded as field constraints, the other a new type that carries the submission through a state change.

**Construction.** The strands rejoin:

```python
raw = {
    "work": "9780140449136",
    "critic": "0000-0002-1825-0097",
    "lens": "formalist",
    "thesis": "Dostoyevsky's use of polyphonic narrative in The Brothers Karamazov undermines the possibility of a single authoritative reading.",
    "arguments": [
        "Each brother's voice carries equal narrative authority, preventing hierarchical interpretation."
    ],
    "submitted_at": "2026-06-22T09:30:00Z",
}

critique = CritiqueSubmission.model_validate(raw)  # Construction IS the proof.
```

If this line succeeds, every invariant holds. The ISBN is 13 digits. The ORCID is well-formed. The lens is one of the recognized frameworks. The thesis is a `Thesis`. At least one argument exists. This is the constructive existence proof from the relation joint, now discharged: the proposition *there exists a structurally complete critique over this raw input* was proven the only way an existential can be, by exhibiting a witness, and `critique` is the witness. No separate validation step runs after this, because there is nothing left to check. The constructor is the verifier.

If this line fails, Pydantic raises a `ValidationError` that names the exact joint that leaked: which field, which constraint, which value. The error is the diagnostic the conditionality section predicted: it tells you precisely where the proposition failed to descend into an inhabitant.

No coordination layer bridges intent to mechanism here, because none is needed. The intent (structurally complete critiques only) descended all the way into types whose constructors enforce it. The test suite that would check "does a critique always have a thesis?" has nothing to test, because the type makes the alternative unconstructable.

One ceiling is worth naming, because it shows the gradient in miniature. "Thirteen digits," "at least fifty characters," "at least one argument" sit below Pydantic's expressive ceiling, so they fuse into the constructor and leave nothing to check. "The thesis genuinely supports its arguments" sits above it, above any type system's ceiling, and above what a name can make a rich reader reconstruct. That invariant falls to a human reviewer, and the reviewer is not a leaked joint but the irreducible floor, the place where no reader, blind or rich, can fuse the proof into construction. The craft is to push every joint that can fuse below the ceiling, so that the only thing left standing outside construction is the thing that genuinely cannot enter it.

---

## Coda

If a program is an ontology, then building one is ontology engineering whether or not you call it that, and several things follow.

The quality of a codebase is the quality of its conceptualization. A system with vague kinds, missing identity criteria, unnamed invariants, and bare primitives leaking across boundaries is not merely messy code. It is a broken ontology: a specification of a conceptualization that fails to specify. Refactoring is ontology repair.

The people who build these systems are doing philosophy, specifically the metaphysics of what kinds of thing exist and what individuates them. A discipline practiced without knowledge of its own nature cannot recognize its errors as errors of kind rather than errors of technique.

The arrival of a sense-rich machine-resident reader changes the economics of the descent but not the descent itself. The joints do not move. What moves is how much of each joint must be pre-paid in explicit structure versus carried in names that a richer reader reconstructs. This means the skill that matters most is no longer the ability to write the explicit structure. It is the ability to name with enough precision that the right reader, blind or rich, can finish the descent from where you leave it. Naming was always ontology. Now it is also, and more directly, programming.

The descent is one act. It was one act before there were computers, when the woodworker carved the tenon and held the invariant in his hands. It was one act when the first compiler forced the full externalization and the field mistook the externalization for the thing. It is one act now, when a reader that carries sense can be placed below the boundary for the first time, and the question is no longer how to survive the handoff to a reader that supplies nothing, but how to route each joint to the reader that carries the most.

This is what programs always were. Ontologies that kept all four causes, proven by construction, awaiting only a reader rich enough to hear the names.
