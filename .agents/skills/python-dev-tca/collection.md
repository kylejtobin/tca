---
type: Construct
description: "Several of one thing, with a meaning of their own, as a frozen tuple, at the level of its members. Holds its members; its cardinality is a constraint, and an invariant across them no constraint states is a rejection predicate. Lives beside them. Crossing a layer, a collection is handed over as its members: a fold returning a tuple of them, from which the next layer's collection is constructed."
---

```python
# domain/shop/type.py
class DeclineReasons(RootModel[tuple[StatedReason, ...]]):
    """Every reason the payment provider gave for declining one charge; it gives at least one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[StatedReason, ...] = Field(min_length=1)
```

```python
# domain/shop/value.py
from typing import Self

from pydantic import Field, RootModel, model_validator

from domain.shop.type import Invariant


class Lines(RootModel[tuple[Line, ...]]):
    """The lines of one order, as the customer sent them."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Line, ...] = Field(min_length=1)

    @property
    def amount(self) -> Amount:
        return Amount(sum(line.amount.root for line in self.root))
```

```python
# domain/shop/value.py
class AisleMatches(RootModel[tuple[AisleMatch, ...]]):
    """The products recommended from one aisle: at least one, each once."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[AisleMatch, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def each_product_once(self) -> Self:
        if not len({match.sku for match in self.root}) == len(self.root):
            raise ValueError(Invariant.EACH_PRODUCT_ONCE)
        return self


class Aisles(RootModel[tuple[Aisle, ...]]):
    """The aisles a recommendation draws from: at least one, each once."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Aisle, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def each_aisle_once(self) -> Self:
        if not len({aisle.category for aisle in self.root}) == len(self.root):
            raise ValueError(Invariant.EACH_AISLE_ONCE)
        return self


class NoAisles(RootModel[tuple[Aisle, ...]]):
    """No aisle with a product close enough to an order to recommend."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Aisle, ...] = Field(max_length=0)
```

```python
# integration/catalog_index/model.py
class Hits(RootModel[tuple[PointHit, ...]]):
    """The products the catalog index found in one group."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[PointHit, ...] = Field(min_length=1)


class PointGroups(RootModel[tuple[PointGroup, ...]]):
    """Every group of a grouped recommendation; none when nothing was close enough."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
```
