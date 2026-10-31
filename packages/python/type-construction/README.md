# type-construction

TCA is a declarative, event-driven application framework under development.

The package currently exports two configuration-only Pydantic value bases:

```python
from type_construction import Model, Root
```

`Model` extends `BaseModel`; `Root[T]` extends `RootModel[T]`. Both enable
`validate_default=True` and `frozen=True` without overriding native construction.

Application constructs and native execution integrations are not yet implemented.
The product definition and architectural contract are maintained in the
[TCA repository](https://github.com/kylejtobin/tca).
