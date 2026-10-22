# 0011. Instant and Identity are fresh scalars, constructed for each holder

Status: accepted

## Context

A fact that concludes at a moment, or that identifies a thing, declares a field for it, and the value does not exist before the fact does. A field typed by a class whose root has a default factory is still required on the holder: Pydantic constructs the root's default inside the class, not the class inside the holder.

## Rejected

A `__init_subclass__` on `Fact` that installs a default factory per field. A memo keyed by type, which gave every `Identity` in a run the same value. A field default on every holder, `at: Instant = Field(default_factory=Instant)`: a line the developer writes for the engine. Seeding one `Instant` at the start of the run like a constant: every fact in the run would share one moment.

## Decision

`Instant` is `Scalar[AwareDatetime]` whose root has `default_factory=partial(datetime.now, UTC)`; `Identity` is `Scalar[UUID]` whose root has `default_factory=uuid4`. A scalar whose root has a default factory is fresh: when the engine asks for a holder whose field names a fresh class and no instance is in the scope, `present` constructs one, `cls()`, for that holder alone, and it enters the holder and nothing else, so two holders never share one. A fresh class is not a premise and is not placed by the proof; `premises` leaves out a required field whose classes are all fresh. A fresh class a carrier also holds has two sources and is refused as `twice` (0057).

## Evidence

On Pydantic 2.13.5, `Placed(Fact)` with `line: Line`, `at: Instant` and `id: Identity` had required fields `line`, `at` and `id`; `Placed(line=tea)` raised `missing` at `("at",)` and `("id",)`; `Placed(line=tea, at=Instant(), id=Identity())` constructed with `at.root` an aware `datetime` and `id.root` a `UUID`; `Placed(line=tea, at="now", id=Identity())` raised `datetime_type` at `("at",)`. In the engine's test program, `Concluded` holds `at: Instant`: two answers in a row gave two `Concluded` whose `at.root` were aware and increasing, and `Concluded.model_validate({"valued": (), "total": Total(of=())})` raised `missing` at `("at",)`.

## Consequences

A page declares `at: Instant` and nothing else. The engine constructs time and identity exactly where a holder needs them and keeps neither. Refuted by a moment that must come from outside the process; that is a scalar the request or a record carries, under its own name.
