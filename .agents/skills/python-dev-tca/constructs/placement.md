---
type: Reference
description: "Which file each construct lives in and which way dependencies point."
---

# Placement

The venue's files:

```text
domain/venue/type.py                  AccountId, InstrumentId, OrderId, Side, Price, Quantity,
                                      NetQuantity, Spread, Depth, ClearingSequence, RefusalReason, VenueUrl
domain/venue/value.py                 Bid, Quote
domain/venue/order.py                 Order, LimitOrder
domain/venue/fill.py                  Fill
domain/venue/position.py              FlatPosition, Position, PositionState,
                                      ReadPosition, PersistPosition,
                                      RecordedPosition, RefusedPosition, PositionOutcome
domain/venue/bids.py                  Bids, BestBid, NoBids, TopBid
domain/venue/api.py                   FillBooked, FillDeclined, FillReply
integration/clearing/model.py         ClearingAcknowledgement, ClearingRefusal, ClearingReply
integration/clearing/submission.py    PositionSubmission
integration/clearing/interpreter.py   ReadPositionInterpreter, PersistPositionInterpreter
api/venue.py                          FillRoute, FillReplyRoute
config.py                             VenueConfig
main.py                               config, client, receive_fill
```

The file for each kind:

| kind | file |
|---|---|
| semantic scalar | `domain/<context>/type.py` |
| value object, and its unions and collections | `domain/<context>/value.py` |
| concept model, with its transformations, actions, unions, and collections | `domain/<context>/<concept>.py` |
| contract model | `domain/<context>/api.py` |
| foreign model | `integration/<system>/model.py` |
| transformation holding a foreign thing and a domain thing | `integration/<system>/<meaning>.py` |
| effect interpreter | `integration/<system>/interpreter.py` |
| route | `api/<context>.py` |
| config | `config.py` |
| composition root | `main.py` |

What each kind may hold or read:

| kind | may depend on |
|---|---|
| semantic scalar | Pydantic, and its primitive or `StrEnum` |
| value object | semantic scalars, value objects, unions, collections |
| concept model | semantic scalars, value objects, concept models, unions, collections; a fact that authorizes an effect also constructs its action |
| union | its variants; it lives in their layer |
| ordered union | its variants, where the only refusal is the fallback |
| collection | members from its own layer or a lower one |
| transformation | any domain kind, foreign models, contract models, actions |
| action | semantic scalars, value objects, concept models, unions, collections |
| foreign model | semantic scalars, matching domain things, nested foreign models |
| contract model | semantic scalars, value objects, concept models, unions, collections |
| config | semantic scalars, value objects, `SecretStr` |
| route | domain things, foreign models, contract models |
| effect interpreter | actions, foreign models, outcomes, and one imported capability |

Which way the imports point:

```text
main.py  ->  api/venue.py  ->  domain/venue/api.py  ->  domain/venue/type.py
main.py  ->  api/venue.py  ->  domain/venue/position.py  ->  domain/venue/fill.py  ->  domain/venue/type.py
main.py  ->  integration/clearing/interpreter.py  ->  integration/clearing/submission.py  ->  integration/clearing/model.py  ->  domain/venue/type.py
integration/clearing/submission.py  ->  domain/venue/position.py
main.py  ->  config.py  ->  domain/venue/type.py
```

In the file:

- A file under `domain/` imports Pydantic, `decimal`, `enum`, `typing`, and other files under `domain/`.
- Imports point one way: `main.py` to `api/`, `integration/`, and `config.py`; each of those to `domain/`.
- `Position.persistence` returns `"PersistPosition"` as a forward annotation, and both classes are in `position.py`.
- A domain file is named for the thing it holds: `fill.py`, `order.py`, `position.py`, `bids.py`.
- `type.py`, `value.py`, and `api.py` are the three role-named files, holding scalars, value objects, and contracts.
- `PositionClient` appears in `integration/clearing/interpreter.py` and `main.py`.
