# Decision records

One file per decision. Fields: Status, Context, Rejected, Decision, Evidence, Consequences. Evidence is a run on Pydantic 2.13.5 and Python 3.14, or "not run" with what would refute the decision. Scenarios for each run are in `packages/python/type-construction/tests/features/`.

| # | Decision |
|---|---|
| 0001 | A Pydantic behavior is run before it is written down |
| 0002 | A rule is a constrained Scalar or a union member |
| 0003 | A choice is a union in a field annotation |
| 0004 | Several of one thing is a tuple |
| 0005 | A route is a class |
| 0006 | A record validates by alias only |
| 0007 | A party's naming convention is an alias generator |
| 0008 | A nested value in a payload is an AliasPath |
| 0009 | A tagged record union is discriminated |
| 0010 | A reply serializes only its computed fields |
| 0011 | Instant and Identity construct themselves |
| 0012 | Failure has no noun |
| 0013 | A record with no fields is not a type |
| 0014 | An unused generic parameter distinguishes nothing |
| 0015 | An action hears one record; perform is abstract on Action and the library kind implements it |
| 0016 | A connection with a credential is a subclass, not a union |
| 0017 | Edges validate in the mode the edge needs; code constructs strict |
| 0018 | A field's docstring is its description |
| 0019 | Config reads the environment and .env |
| 0020 | StrEnum is the enumeration |
| 0021 | The engine has no classes |
| 0022 | The classes are the inventory |
| 0023 | The interface is defined once |
| 0024 | A page subclasses a kind, never one of its own classes |
| 0025 | A deployment value is a Setting, lenient; a business value is a Scalar, strict |
| 0026 | The command line validates with model_validate(tree, strict=False) |
| 0027 | The command line is rendered from the request's JSON schema parsed into node classes |
| 0028 | A key a party may omit is T | None = None on a Record |
| 0029 | A program is one module named by the entry-point group |
| 0030 | answer takes the route, the request, the config and the program, and returns the reply |
| 0031 | Narrowing to a parametrized class is a TypeIs guard, never a cast |
| 0032 | A red check is answered by modeling, not by narrowing |
| 0033 | Tests are written for procedure only |
| 0034 | world and engine are separate distributions under an empty namespace root |
| 0035 | A page holds classes only; procedure lives in a library kind's perform |
| 0036 | Nothing on a page exists for the engine |
| 0037 | A type is never weakened to pass a check |
| 0038 | A decision is recorded, with what it rejects and what refutes it, before the code it decides is reported |
| 0039 | What a thing is, its valid states and its owner are stated before its kind |
| 0040 | Every behavior is named by the Pydantic call that performs it |
| 0041 | Reports lead with what is not done, and checks run only as just declares |
| 0042 | A computed field is a producer, and a class the run needs has exactly one |
| 0043 | A scalar is a RootModel subclass |
| 0044 | Several of one thing in a run is a child run per element |
| 0045 | A connection opens once at startup and closes once at shutdown, holding its client outside validation |
| 0046 | The engine emits OpenTelemetry spans named by the program's classes, through the API alone |
