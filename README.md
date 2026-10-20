<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

<p align="center"><strong>The model of the business is the program. What the model cannot say, the program cannot do.</strong></p>

---

TCA is for modeling an organization as types and running the model. You write the things your world is made of, as Pydantic types that say what each one holds, and you build the application out of those pieces and nothing else. Each fact holds the one before it, and that holding is the whole of the program's behavior. A small engine you do not write runs your types themselves, not a model of them: every step is Pydantic constructing one of your classes, and the engine only orders the steps and finds each field's value by its type. Before anything runs, it proves from your types alone that the model is whole.

It is right for three reasons, and they are one. A state the business does not have has no type, so it cannot occur: this is what the typed-functional tradition established, illegal states unrepresentable, parse don't validate, effects as data, and TCA brings it to Python and makes it mechanical. A program with no procedure in it is one a product owner can read, because the order of facts is the order of the business, and nothing else is there. And a program that is only a model is the one kind of program a language model writes reliably: it is given the semantics as types and constrained to produce types, which is structured output, the thing it is good at, judged by the same checker that judges a person.

Every program, in any style, has the same seven parts. TCA places each one so that the developer writes only the model.

| part | every program has | in TCA it is |
|---|---|---|
| entry | where control is handed over | one line in `main.py`: a transport, or the engine itself, serves the config |
| configuration | what the environment says about this run | a `Config`: the connections the program holds and the values the deployment may set |
| arrivals | where facts come in | a `Request` on a route, a `Record` a party answers or streams, a callback from a library; each validated once, by the type you declared for it |
| state | what is held between arrivals | the current fact of each context, held by the engine; the lasting state lives with the parties that own it |
| meaning | the rule from an arrival and the state to the next state | a `Fact` whose fields hold the fact before it and what arrived; when an arrival may lead to more than one, your `Ordered` says which is tried first, and the first one Pydantic can construct is the next fact |
| effects | where the program acts on the world | an `Action` a fact carries, with the one expression that names the call; the engine performs it and what returns is the next arrival |
| resources | the handles through which the world is reached, acquired and released | a `Connection` per party, as the deployment names it; opened once at start, closed at stop, by the engine |

Composition is the eighth thing and is not a part. Here it is the holding: a fact's fields are its wiring, there is no second vocabulary for plumbing, and the engine reads the types instead of being told.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
