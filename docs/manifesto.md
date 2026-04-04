# Manifesto

## The Origin

We built systems the way everyone builds systems. Services coordinated domain objects. Adapters mapped between layers. If/elif chains dispatched on tags. Dictionaries carried data between functions. Strings represented concepts that deserved names.

And the systems failed. Not spectacularly. Gradually. A mapping function silently dropped a field. A service method grew to three hundred lines because every new requirement added another branch. A string that meant "status" could hold any value, and eventually it held one nobody expected. The domain model was "complete" but the service layer kept growing, because the models didn't carry enough meaning to do the work themselves.

Every failure had the same root: the modeling was too weak. The types expressed less than the program knew. The gap between knowledge and structure was filled with procedure, and procedure is where bugs live.

---

## The Claim

**A program's correctness should be visible in its structure, not hidden in its execution.**

If a concept exists in the domain, it gets a type. If a value varies by case, the cases are variants in a union. If a vocabulary is closed, it is an enum. If a boundary exists, it is named and contained. If a derivation depends only on proven fields, it lives on the model that owns those fields.

The program is the construction graph. Not the procedural glue around it. The glue is the disease. The graph is the cure.

---

## What We Believe

**Construction is proof.** If the object exists, every constraint declared in its type was satisfied. If construction fails, no object exists. There is no "invalid but present" state. The act of building the object IS the proof.

**Frozen is forever.** A mutable proof is not a proof. It is a hope. Freezing converts a momentary check into a permanent certificate. A proof that can be violated after issuance is worthless.

**The domain is the program.** Domain types are not passive containers that services operate on. They carry construction logic, classification, derivation, and boundary translation. The service layer is a symptom of incomplete modeling. We do not treat symptoms.

**Modeling is the work.** Survey the domain. Name every concept. Give every value a type that carries its meaning. Wire the relationships through fields. The program emerges from the modeling. You do not design it separately. You do not write it afterward. It was already there in the structure of the domain. You just had to model precisely enough to see it.

**Every error is a design error.** When the type checker complains, the design is weak. We do not suppress. We do not work around. We do not move things to make the linter quiet. We build the type, fix the ownership, model the boundary. The fix is always more modeling. Never less.

---

## What We Reject

**The service layer as home of logic.** When services grow, it means models shrank. If you need a service to map, transform, enrich, or decide, the types are too weak.

**Procedure where structure would serve.** An if/elif chain that dispatches on a tag is a discriminated union that hasn't been declared. A mapping function between two representations is a wiring that hasn't been named. A helper that derives a value from model fields is a projection that doesn't live on the model yet. Every piece of procedure is a question: is this irreducible, or is it a modeling failure? Almost always the latter.

**Flat modeling.** `str` where there should be an enum. `dict` where there should be a product. `Any` where there should be a named boundary type. Flat modeling is not simplicity. It is the refusal to name what you know.

**Validation separated from acceptance.** Check the data, then proceed with the unchecked type. This is the original sin. Construct, don't check. The proven type flows forward. The unproven type does not exist.

**Mutable domain objects.** Every setter is a hole in the proof boundary. Every mutation is a moment where the object's guarantees are suspended. We do not suspend guarantees. We construct new proven snapshots.

---

## What We Build

Frozen types wired through fields. Name agreement as the contract between models. Discriminated unions whose variants carry the answer. Projections that extend proven fields into further proof. Construction graphs where demand drives evaluation and proofs chain.

Programs whose entire semantic surface instructs. When a language model reads the schema, every field name is an instruction, every enum member is a constraint, every type boundary is a proof obligation. The types don't just structure the program. They program the model that reads them.

Programs where procedure is contained, justified, and terminal. Some boundaries resist pure construction. At those boundaries, a small piece of procedure normalizes foreign input into owned truth, and the construction graph resumes. That place is small, named, and surrounded by proven types on every side.

---

## The Ontology

Model the domain exhaustively. Freeze everything. Wire through fields. Dispatch through tags. Project through proven derivation. Let construction execute the graph.

What emerges is not a program in the traditional sense. It is an ontology. A complete, formal naming and structuring of a domain's concepts and relationships. But this ontology executes. The relationships fire. The constraints prove.

The program was always there, latent in the domain. Procedure obscured it. Weak modeling hid it. Mutable state blurred it. TCA is the discipline of modeling precisely enough that the program becomes visible. The construction machine makes it run.

---

*Every system we build is a bet on where truth lives. We bet on structure.*
