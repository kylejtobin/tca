# type-construction

Type Construction Architecture: the world a program is written in, and the engine that runs it.

`type_construction.world` is the closed vocabulary of kinds. A program is subclasses of them and nothing else: scalars and vocabularies, values, records of what other parties say, connections to those parties, facts that each hold the one before them, actions that each carry one effect, requests and replies on routes, and one config. A kind carries the configuration every class of it shares and says, by its parameters, what the class declares. It has no behavior.

`type_construction.engine` reads a world and runs it. Before anything runs, `check` proves from the types that every arrival has a fact that holds it, every fact has a next step, and every chain ends in a reply, and reports every fault at once as Pydantic's own errors. Then, for every arrival, Pydantic constructs the developer's next class from the fact the context rests in and what arrived; an action's one effect is awaited and what the party said is the next arrival; a fact no action holds is at rest and answers its reply. `engine.parties` holds the parties the engine itself is: the clock, a schedule, and the program's own routes.

```python
from type_construction.world import Action, Config, Connection, Fact, Many, Record, Reply, Request, Route, Scalar, Value, Vocabulary
from type_construction.engine import check, run, serve
```

Transports are separate packages: `type-construction-http` serves routes over HTTP, `type-construction-cli` from the command line. The engine knows no protocol.
