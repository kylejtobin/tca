# 0042. A computed field is a projection: it constructs a word from what it holds, and the run never keeps its value

Status: accepted

## Context

A reply tells the caller values read from the fact it is made from, and a fact may say what it knows from what it holds. The engine must decide what a computed field is to the run and to the proof.

## Rejected

The engine searching constructed instances for a value of the needed class. The engine converting a value to the needed class by its root. A validator on the fact. A computed field as a producer: the run kept its value under the class it returned, so that a fact holding that class became constructible; with derivations and relations declared as kinds (0047, 0048), the one use of it was a comparison or an arithmetic expression written on the page, which the smell check refuses as `COMPUTATION`.

## Decision

A computed field reads fields and constructs a declared class, and computes nothing. The run never evaluates it and never keeps its value; it is evaluated when the holder is serialized, so a word that refuses refuses at the boundary, as a `PydanticSerializationError` wrapping the `ValidationError`, which the command line prints and exits 1 on. The proof reads the classes a computed field returns, `produces(cls)`, as words: a word is reached from its holder (0052), a scalar only words name is placed where its holder is, and a word is not a source (0050), so a reply may say a scalar the request carries.

## Evidence

`produces(Picked)`, for a fact with one computed field `which -> Amount | Limit`, returned `{"which": (Amount, Limit)}`, read from `model_computed_fields`. In the engine's test program, `Answered.total -> Capped` constructs `Capped(le=30)` from `Total`: with two elements at 2.50 the reply serialized to `{"total":"5.00"}`; with two elements at 25 the run answered with `Total` 50 and `model_dump_json()` raised `PydanticSerializationError`, "1 validation error for Capped", `less_than_equal`. In the command line's test program, `Told.name -> Name` returns the `Name` the request carries, and the proof accepted `Name` with its one source.

## Consequences

A computed field is a reply's word or a fact's statement of what it holds; a value computed from others is a derivation kind and a rule is a relation kind. A word that can refuse is a rule written as a check, and a relation over the value is the type-driven form. Refuted by nothing.
