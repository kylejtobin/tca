Model domain name registration as a program.

A registrant asks for a domain name: labels under a top-level domain, for a term of one to ten years. The registrar is asked whether the name is available. It answers one of four ways: the name is available at a price per year in its currency; the name is premium, at a premium price for the first year and a renewal price for each year after; the name is taken, until an expiry date; or the name is reserved under a policy, and cannot be registered. An available or premium name is an offer: it has a cost for the term, an amount in the registrar's currency, and the registrant is told it. A taken or reserved name has no cost and nothing follows.

An offered name is then registered for the term, at that cost. The registrar either grants the registration, with its own registration id and the date it expires, or refuses it with every reason it gives: some refusal reasons this program has words for, `object_exists`, `policy_violation` and `registrant_invalid`; the rest it keeps as the registrar gave them.

The registrar is at one address, holding its availability answers at `availability` and its registrations at `registrations` under it, and knows this program by a key, sent as the basic-auth user with a blank password. The deployment names the address and the key in the environment.

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

Prices and amounts are in minor units of the currency, `usd` or `eur`. A refusal carries at least one reason. The program offers two callbacks: check, a registration request to its availability; and register, an offer to its registration outcome.
