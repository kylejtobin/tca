---
type: Construct
description: "Several of one thing, with a meaning of their own, as a frozen tuple. Holds its members. Lives beside them. Crossing a layer, a collection is handed over as its members: a fold returning a tuple of them, from which the next layer's collection is constructed."
---

```python
# domain/shop/type.py
class DeclineReasons(RootModel[tuple[StatedReason, ...]]):
    """Every reason the payment provider gave for declining one charge."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
```

```python
# domain/shop/value.py
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
class RelatedMatches(RootModel[tuple[Match, ...]]):
    """The products recommended beside an order, at most one per aisle, at least one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Match, ...] = Field(min_length=1)


class NoMatches(RootModel[tuple[Match, ...]]):
    """No product close enough to an order to recommend."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Match, ...] = Field(max_length=0)
```

```python
# integration/catalog_index/model.py
class Hits(RootModel[tuple[PointHit, ...]]):
    """The products the catalog index found in one aisle."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[PointHit, ...] = Field(min_length=1)


class PointGroups(RootModel[tuple[PointGroup, ...]]):
    """Every aisle of a grouped recommendation; none when nothing was close enough."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class IndexGroups(BaseModel):
    """The catalog index's answer to a grouped recommendation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    result: GroupResult
    status: IndexStatus
    time: QueryTime

    @property
    def matches(self) -> tuple[PointHit, ...]:
        return tuple(hit for group in self.result.groups.root for hit in group.hits.root)
```
