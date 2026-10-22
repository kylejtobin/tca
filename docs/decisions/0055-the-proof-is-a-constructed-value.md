# 0055. The proof is a value Pydantic constructs, and every fault is a refusal of that construction

Status: accepted

## Context

The program's rule is that refusal is the only control flow and a fault is a `ValidationError`. The proof found faults as the return values of functions and raised them from a procedure of its own, so the engine obeyed a rule the page was held to and the engine was not, and a fault had no `loc`, `type` and `msg` of the shape every other refusal has.

## Rejected

`prove(route)` returning a set and `proven(program)` returning `None` after raising from a list of checks, cached per process with `functools.cache` on the module: a procedure with a hidden memo. Placement faults raised as exceptions from inside the passes, which stopped the passes at the first and reported one fault at a time.

## Decision

`Proof` is a frozen, strict Pydantic model holding the program's name, its classes, every `Placement` of a class at a path, every `Waiting` of a class on the classes it could not be placed without, and every `Fault` the passes found while placing. `proven(program)` runs the passes and constructs it. Its one `model_validator(mode="after")`, `sound`, reads the faults from those fields and the declarations, `unfilled`, the placement faults, `twice`, `unreached`, `unmodeled`, `boundary`, `deployment`, `ambiguous`, `certain`, `undiscriminated` and `undecided`, and raises one `ValidationError.from_exception_data` naming every fault, each with a `type`, a `loc` whose first element is the class, and a message in the developer's names. The server constructs the proof once at startup and passes it to every `answer` (0030); the proof's reads, `path`, `built`, `reached` and `constants`, are what the run asks of it. Nothing is cached on a module.

## Evidence

On Pydantic 2.13.5, a `ValidationError` raised from an after-validator reaches the caller with its errors intact: the program with the faults was refused with twenty-one errors under the title `Proof`, among them `("missing", ("Concluded", "unheard"))`, `("cycle", ("Egg",))`, `("twice", ("Name",))`, `("unplaceable", ("Twin",))`, `("collects", ("Collects",))`, `("route", ("Misplaced",))`, `("unreached", ("Stray",))`, `("unmodeled", ("Bare", "count"))`, `("boundary", ("Direct", "cheap"))`, `("config", ("type_construction_engine.faults",))`, `("ambiguous", ("Either", "which"))`, `("never", ("Impossible",))`, `("undiscriminated", ("Both",))` and `("undecided", ("Charge",))`. The engine's test program's proof had no waiting class, placed `Cheap` at `(Element,)` and `Portion` at `(Element, Part)`, and its `constants` were `(Limit,)`. A `Placement` whose `cls` is not a model is refused by Pydantic with `is_subclass_of`.

## Consequences

The engine's own values obey the page's rule: a fault is a refusal, with the shape of every other refusal, and the CLI prints it as it prints any. Refuted by a fault that cannot be read from the proof's fields; none found.
