# 0043. A scalar is a RootModel subclass

Status: accepted

## Context

A business value needs a name, a constraint, and a type the checker distinguishes from every other value of the same primitive.

## Rejected

`Annotated[int, Field(gt=0)]` aliases: no nominal type, so `Quantity` and `Retries` are both `int` to basedpyright, and no class docstring reaches the JSON schema's `$defs`.

## Decision

`class Quantity(Scalar[int])` with `root: int = Field(gt=0)`. The class is nominal to the checker, its docstring is its schema description, its constraint travels with every field that holds it, and the value is read as `.root`. The cost is one model instance per value and `.root` on the page where arithmetic reads it.

## Evidence

`Quantity(0)` refused `greater_than`; `$defs["Quantity"]["description"]` is the class docstring; the CLI rendered `--quantity QUANTITY ... (> 0)` from the definition. The cost is not yet measured; the product's P5 names the benchmark.

## Consequences

A field is never annotated with a bare primitive. Refuted by a measured cost that a program cannot bear; none measured.
