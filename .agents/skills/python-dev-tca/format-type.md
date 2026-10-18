---
type: Construct
description: "Another system's thing, under its names, in a format no maintained library reads: a foreign record whose reading and writing this program holds itself, with whatever procedure the format needs, returning the typed record or a validation failure. Its restrictions are the format's, on its own scalars. Holds semantic scalars and format types. Lives in parser/<format>.py, and only a foreign model holds it."
---

A PARSER STANDS ONLY AT A CROSSING, FOR ARRIVING TEXT NO LIBRARY READS INTO A PYTHON OBJECT, A DICT OR JSON. NOTHING ALREADY HELD IS PARSED.

```python
# parser/receipt.py
import re
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer, RootModel

from domain.shop.type import Amount, Currency


class ReceiptRef(RootModel[str]):
    """The payment provider's reference on a receipt, as the line format can carry it: no `|`,
    no line break."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[^|\r\n]+$")


class Receipt(BaseModel):
    """The payment provider's receipt for a charge, under its names, written `ref|amount|currency`."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    ref: ReceiptRef
    amount: Amount
    currency: Currency


LINE = re.compile(r"([^|\r\n]+)\|([0-9]+)\|([a-z]+)")


def read(value: object) -> object:
    if isinstance(value, Receipt):
        return value
    if not isinstance(value, str) or not (line := LINE.fullmatch(value)):
        raise ValueError("a receipt is written ref|amount|currency")
    ref, amount, currency = line.groups()
    return Receipt(ref=ReceiptRef(ref), amount=Amount(int(amount)), currency=Currency(currency))


def write(receipt: Receipt) -> str:
    return "|".join((receipt.ref.root, str(receipt.amount.root), receipt.currency.value))


ReceiptLine = Annotated[Receipt, BeforeValidator(read), PlainSerializer(write)]
```

Only a foreign model holds the line: the payment provider's reply, in full on the foreign model page.

```python
class ChargeApproved(BaseModel):  # integration/payments/model.py
    """A charge the payment provider made, with its receipt in the provider's own line format."""

    charge: ChargeId = Field(alias="id")
    receipt: ReceiptLine
```
