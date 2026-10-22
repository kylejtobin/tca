# 0043. A scalar is a RootModel subclass over a primitive

Status: accepted

## Context

A business value needs a name, a constraint, and a type the checker distinguishes from every other value of the same primitive; a scalar over a model would be a value wrapping a thing.

## Rejected

`Annotated[int, Field(gt=0)]` aliases: no nominal type, so `Quantity` and `Retries` are both `int` to basedpyright, and no class docstring reaches the help. `Scalar[T]` with `T` unbounded, which admitted `Scalar[SomeFact]`.

## Decision

`class Quantity(Scalar[int])` with `root: int = Field(gt=0)`, where `Scalar[T: Primitive]` bounds `T` to `str`, `int`, `float`, `bool`, `bytes`, `Decimal`, `datetime`, `date`, `time`, `timedelta`, `UUID` or an `Enum`. The class is nominal to the checker, its docstring is its help when the field has none, its constraint travels with every field that holds it, and the value is read as `.root`. `Instant`, `Identity` and `Duration` are scalars. The cost is one model instance per value and `.root` where a kind reads it.

## Evidence

`Duration(timedelta(0))` refused `greater_than`. The CLI rendered `--amount AMOUNT    What is offered. (> 0)` from the class's docstring and its root's bound, with no docstring on the field. A scalar over an enumeration, `Code(Scalar[Currency])`, constructed `USD` leniently from text. basedpyright strict accepts `Scalar[AwareDatetime]` and `Scalar[Decimal]` under the bound.

## Consequences

A field is never annotated with a bare primitive, and the proof refuses one as `unmodeled` (0059). Refuted by a measured cost that a program cannot bear; none measured.
