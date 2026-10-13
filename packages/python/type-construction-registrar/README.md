# type-construction-registrar

Type Construction Architecture's reference program: domain name registration, modeled as types.

```python
from type_construction.registrar import (
    Offer,
    RegistrarConfig,
    check,
    check_sync,
    register,
    register_sync,
)

config = RegistrarConfig()

availability = await check(config, request)
outcome = await register(config, Offer.model_validate(availability.root))

availability = check_sync(config, request)
```

## The domain

A registrant asks for a domain name, labels under a top-level domain, for a term of one to ten years. The registrar is asked whether the name can be had. It answers one of four ways: the name is available at a price per year; the name is premium, at a premium price for the first year and a renewal price for each year after; the name is taken, until a date; or the name is reserved under a policy, and cannot be registered. An available or premium name is an offer: it has a cost for the term, in the registrar's currency, and the registrant is told it. A taken or reserved name has no cost and nothing follows.

An offered name is then registered for the term, at that cost. The registrar either grants the registration, with its own identity for it and the date it expires, or refuses it, with every reason it gives; some reasons this program has words for, the rest it keeps as the registrar gave them.

## The registrar

The registrar is at one address, holding its availability answers at `availability` and its registrations at `registrations` under it, and knows this program by a key, sent as the basic-auth user with a blank password. The deployment names them in the environment:

| Variable | Holds |
|---|---|
| `REGISTRAR__URL` | The registrar's address. |
| `REGISTRAR__KEY` | The key. |

Availability, `GET <registrar>/availability/<name>`, answers with one of:

```json
{"status": "available", "price": 1200, "currency": "usd"}
{"status": "premium", "premium": 250000, "renewal": 1200, "currency": "usd"}
{"status": "taken", "expires": "2027-03-01"}
{"status": "reserved", "policy": "icann-reserved"}
```

Registration, `POST <registrar>/registrations` with a JSON body, takes:

```json
{"name": "example.com", "years": 2, "registrant": "acct_42", "amount": 2400, "currency": "usd"}
```

and answers with one of:

```json
{"id": "reg_9f1c", "expires": "2028-03-01"}
{"refusals": ["object_exists", "policy_violation"]}
```

Prices and amounts are in minor units of the currency. A refusal carries at least one reason. The refusal reasons this program names are `object_exists`, `policy_violation` and `registrant_invalid`.
