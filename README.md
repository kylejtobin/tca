# Type Construction Architecture

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Type Checked: basedpyright](https://img.shields.io/badge/type%20checked-basedpyright-cyan.svg)](https://github.com/DetachHead/basedpyright)

Pydantic is a programming language. Python is its runtime.

TCA is the discipline of writing programs as type construction graphs. Define the types. Wire their construction pipelines. Let `model_validate` execute. If the object exists, it's proven. If construction fails, no object exists. There is no third outcome.

## What's Here

**[The specification](tca.md)** defines the architecture: the construction machine and its five layers, the two fundamental mechanisms (`from_attributes` and discriminated unions), construction graphs, the program triad, and the principles that follow from treating construction as proof.

**[The building block classifier](tca/building_block.py)** is a teaching resource, a live demonstration of every TCA mechanism in the spec, and a practical tool. Point it at any Pydantic model and it classifies every field into its structural building block — enum, newtype, record, collection, scalar — through pure construction. No branching, no external classifiers. One `model_validate` at the root cascades the entire classification. Use it to learn TCA, to see TCA working, and to understand the structure of your own models.

## Requirements

- Python 3.12+
- Pydantic 2.12+

## License

[MIT](LICENSE)
