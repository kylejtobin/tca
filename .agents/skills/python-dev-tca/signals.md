---
type: Reference
description: "Every moment's signals that the default fired, in one table; the smell check and the judge's rules are generated from it."
---

# Signals

Each row is the signal that one "In the file" line of a moment page is false. Rows follow each page's lines, in order. On a signal, read the moment page and declare the thing.

| Moment | The signal |
|---|---|
| [naming](moments/naming.md) | a class with no docstring; a docstring that says what the code does |
| [naming](moments/naming.md) | a name for what the program did: `Parsed`, `Gathered`, `Published`, `Consulted`; a name that is or ends in `Record`, `Item`, `Data`, `Payload`, `Result`, `Entry`, `Info`, `Handler`, `Manager`, `Processor`, `Event`; a name beginning `Incoming`, `Outgoing`, `Processed`, `Enriched` |
| [naming](moments/naming.md) | an outcome family beside an action: `Persist`, `Persisted`, `PersistFailed` |
| [naming](moments/naming.md) | two classes differing by the path that produced them: `BuyFill`, `SellFill` |
| [naming](moments/naming.md) | `Route` or `Interpreter` on a domain class; any other role suffix |
| [naming](moments/naming.md) | a file named `store`, `repository`, `handler`, `controller`, `manager`, `processor`, `router`, `crud`, `utils`, `helpers`, `common`, `misc`, `shared`, `transformation`, `action`, `transition` |
| [sequence](moments/sequence.md) | a name assigned inside `receive_fill`; a function calling constructions in order |
| [sequence](moments/sequence.md) | a class made of exactly one other class, naming that a step was done: `Persisted(position)` |
| [sequence](moments/sequence.md) | statements ordered by hand so the steps happen in turn |
| [sequence](moments/sequence.md) | `model_copy(update=`, `model_construct`, assignment to a field, `object.__setattr__`; a verb-named class holding a before and an after: `AdvancePosition(prior, next)` |
| [choice](moments/choice.md) | a derivation returning `bool` where each answer carries facts |
| [choice](moments/choice.md) | `if`, `match`, `isinstance`, a ternary, `and`/`or`, or a class comparison choosing between things |
| [choice](moments/choice.md) | a field named `type` or `kind`; a `Literal` discriminator the other system does not send |
| [choice](moments/choice.md) | a dict of classes or callables; a partial dict; `.get(`; a default; a caught `KeyError` |
| [choice](moments/choice.md) | a route or interpreter selecting the variant by hand |
| [choice](moments/choice.md) | two stored fields checked against each other: `bid` and `ask`; a validator comparing fields |
| [absence](moments/absence.md) | `None`, `Optional`, `\| None` in an annotation; a default standing in for a missing value |
| [absence](moments/absence.md) | a vocabulary of moments: `pending`, `in_progress`, `done`; a flag beside the field |
| [absence](moments/absence.md) | a consumer that tests for the empty case before it reads |
| [absence](moments/absence.md) | an empty thing that drops the identity it was asked for |
| [absence](moments/absence.md) | two fieldless variants in one union: `NoBids`, `EmptyBook` |
| [absence](moments/absence.md) | `try` around a constructor; a `ValidationError` turned into the empty thing; a strong variant stricter than its source |
| [refusal](moments/refusal.md) | `try`, `except`, `raise_for_status`, `return None`, `ok: bool`; a reply union with one variant |
| [refusal](moments/refusal.md) | a refusal that stops at the reply; a `ValidationError` named as a refusal |
| [refusal](moments/refusal.md) | a client helper that parses, retries, counts, or raises on the reply's content |
| [refusal](moments/refusal.md) | a free-text reason; a reason outside the enum caught by a default |
| [refusal](moments/refusal.md) | a refusal that drops what was refused |
| [many](moments/many.md) | `list`, `set`, or `dict` in an annotation; `RootModel[dict[K, V]]` |
| [many](moments/many.md) | `for`, `while`, an accumulator, `append`; a generator with an `if` clause |
| [many](moments/many.md) | a fold returning a bare primitive |
| [many](moments/many.md) | a fold that fails on the empty tuple |
| [many](moments/many.md) | a class holding a growing list of fills; a receive loop |
| [many](moments/many.md) | `execute` counting, collecting, or waiting for several replies |
| [ingress](moments/ingress.md) | `json.loads`, `["key"]`, `.get(`, `**body` |
| [ingress](moments/ingress.md) | a dict, raw string, or SDK object held after the route constructs; fields read again from the source |
| [ingress](moments/ingress.md) | a class for the envelope, passed into the domain |
| [ingress](moments/ingress.md) | a foreign name as a field name; a field-copying function or class; a domain class that mirrors a foreign or contract shape |
| [ingress](moments/ingress.md) | `field_validator`, `model_validator`, `BeforeValidator`, `AfterValidator`, `WrapValidator`, `PlainValidator`, `model_post_init`, a custom `__init__`, a schema hook; `Any`, `JsonValue`, `Json`, `SkipValidation`; a bare `str`, `int`, `Decimal` field |
| [ingress](moments/ingress.md) | a foreign model that copies the domain thing's shape |
| [effect](moments/effect.md) | a client, reply, outcome, exception, or retry count on an action |
| [effect](moments/effect.md) | one interpreter taking unrelated actions; a dispatch registry of interpreters |
| [effect](moments/effect.md) | a client call outside `execute`; a client on a domain class, route, or foreign model |
| [effect](moments/effect.md) | retry, `sleep`, a loop, a flag, or a branch in `execute`; a successor constructed in `execute` |
| [effect](moments/effect.md) | a primitive or serialized text passed between domain things |
| [effect](moments/effect.md) | an action constructed by its caller's policy |
| [effect](moments/effect.md) | a file under `domain/` importing a client, SDK, framework, `requests`, `httpx`, `os`, or `subprocess` |
| [origin](moments/origin.md) | a bare `str` or `int` identity |
| [origin](moments/origin.md) | `uuid`, `datetime.now`, `time.`, `random`, `secrets`, `os.environ` in a domain file; `default_factory` |
| [origin](moments/origin.md) | a stored field that the other fields determine |
| [origin](moments/origin.md) | a derivation reading a clock, global, client, cache, or environment; a method with parameters |
| [origin](moments/origin.md) | a counter or timestamp this program assigns |
| [origin](moments/origin.md) | a clock or random source read in a derivation or in `main.py` |
| [arrival](moments/arrival.md) | a second `def` in `main.py`; a runner, pipeline, service, registry, or step list |
| [arrival](moments/arrival.md) | a module-level dict, list, cache, or `global`; `lru_cache`, `cached_property`, `PrivateAttr` |
| [arrival](moments/arrival.md) | a class or variable holding a current position; a read failure turned into `FlatPosition` |
| [arrival](moments/arrival.md) | a read keyed by the order, or by a value the fill does not carry |
| [arrival](moments/arrival.md) | an outcome dropped |
| [arrival](moments/arrival.md) | an input constructor, callback, or output serializer left to the framework's defaults |
| [missing-thing](moments/missing-thing.md) | a `def` at module level other than `receive_fill`; `lambda`, a private helper, a callback passed in |
| [missing-thing](moments/missing-thing.md) | a method with parameters beyond `self`; a `staticmethod` |
| [missing-thing](moments/missing-thing.md) | a second module-level `def`, in any file |
| [missing-thing](moments/missing-thing.md) | a wrapper class that only calls a constructor; a class no trader would name |
| [missing-thing](moments/missing-thing.md) | escaped: a meaning that lives only in a comment, a primitive, an ordering, or a convention; duplicated: two classes for one meaning; vacuous: a class with no meaning of its own; fused: one class holding two meanings that vary independently |
| [missing-thing](moments/missing-thing.md) | a check after construction in place of a reported construction gap |
| [missing-thing](moments/missing-thing.md) | a class whose shape matches no form in `constructs/` |
