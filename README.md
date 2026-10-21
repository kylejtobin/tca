<h1 align="center">Type Construction Architecture</h1>
<p align="center"><img src="img/hero.png" alt="Type Construction Architecture: each fact holds the one before it" width="100%"></p>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.14%2B-3776AB?style=flat-square&logo=python&logoColor=white&labelColor=0d1117" alt="Python 3.14+"></a>
<a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white&labelColor=0d1117" alt="Pydantic v2"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-BSD--3%20%2B%20Commons%20Clause-22D3EE?style=flat-square&labelColor=0d1117" alt="License: BSD-3 + Commons Clause"></a>
</p>

---

You write your application as Pydantic classes and nothing else: what arrives, what each external party says, what your business concludes from them, and what you answer. Every field annotation is a dependency, every union is a decision, every constraint is a rule, and `ValidationError` is the only failure path.

The engine is four functions: deserialize the request, perform each action and deserialize its response, serialize the reply, open and close clients. It constructs your classes in the order their annotations require and checks at startup that every class can be reached from the request and the parties.

## License

The packages and this repository are under the BSD 3-Clause License with the Commons Clause, in [LICENSE](LICENSE): use them, change them, and build on them in your own work, commercial or not, with attribution; what is withheld is selling them, or a product or service whose value is substantially theirs. The agents and skills under `.agents/` are under the Apache License 2.0, in [.agents/LICENSE](.agents/LICENSE), with no condition beyond its own.
