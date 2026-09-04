---
type: Reference
description: One complete discovery run, from a rendered Plaid identity reply to the exact construct set, taken from a real session.
---

# Worked Example

This is a real run of the process against Plaid's `/identity/get` reply, recorded from a session in which the operator advanced one question per turn. It is carried here as it happened, in a personal-finance domain rather than the venue domain the construct pages share, because the two-witness convergence in it cannot be paraphrased into another domain without inventing evidence. The reply itself is described, not reproduced, for the same reason.

## 1. Evidence

The reply, constructed through `plaid-python` and printed as JSON, carried the accounts frame already read from `/accounts/get` (account id, balances, mask, name, official name, type, subtype) and, under each account, an `owners` list. Each owner carried `names` as a flat list of strings; `phone_numbers`, `emails`, and `addresses` as lists of rows, each row with a `data` field holding the value, a `primary` boolean, and on phones and emails a free-string `type`; each address `data` an object of street, city, region, postal code, and country as a string. The same owner appeared under both accounts.

The operator's prompt: identity is not only financial; think about what Plaid shows, the ontology already built, and SCIM. "They all matter to nature."

## 2. Things

**1. What things is this evidence of, and how do they compose?**

There is one thing in nature, a person, and Plaid, SCIM, and our ontology are three witnesses to it, none of them the thing. Plaid is the bank's account of a person: an account owner. SCIM (RFC 7643) is the cross-domain consensus on what a person is to any system: a structured name, many contact points each with a type and one primary, addresses the same way. Our world already holds a person as `Party` with one name and addresses. Where independent witnesses converge, the shape is real.

- Person: a human who holds accounts. A person is a party; an institution is a party; so party splits into person and organization.
- Personal name: several forms, one the person goes by; structured as given, middle, family.
- Phone number: a way to reach a person, of a kind, one primary among a person's phones.
- Email address: same shape as phone.
- Address: ours already; here it gains a kind and primacy among a person's addresses.
- Contact point kind: the axis phone, email, and address share.
- Ownership: the relation between an account and the persons who hold it. Two holders is a joint account. The same person on two accounts is one thing, so the relation lives on the account as owners, not on the person.
- Account, balances, connection, institution: ours, unchanged, the frame the owners hang on.

Composition: connection → institution (party, organization). Account → owners (party, person). Person → names, phones, emails, addresses. Address → street, city, region, postal code, country.

**2. Already ours, or new?**

Person: new; `Party` exists with id, name, addresses, is the organization shape, and becomes one arm of a union. Organization: ours as today's `Party`, renamed to the arm it is. Personal name: new; `PartyName` is one flat string. Phone number, email address, contact point kind: new. Address: ours; new around it are kind and primacy. Ownership: new field on every account kind. Account, balances, connection, institution: ours; `PartyId` on `Connection.institution` stays.

**3. What is it in nature, and what must be true?**

- Person: a natural human with identity independent of any account; at least one name form, zero or more phones, emails, addresses; at most one primary per set; the same person across accounts and institutions.
- Organization: a legal entity, not a human; one legal name, addresses; no given/family structure.
- Personal name: given and family required, middle optional; several forms, exactly one the person goes by; whitespace-only parts are not names.
- Phone number: E.164, `+` then 8 to 15 digits.
- Email address: a mailbox address; Pydantic's email validation is the constraint.
- Contact point kind: mobile applies to phones only in nature; a home email is real, a mobile address is not. So phones have {mobile, home, work, other}, emails and addresses share {home, work, other}. Two axes, not one.
- Primary: among a person's phones, emails, addresses, and names, exactly one is primary per non-empty set. A fact of the set, not the member. Modeled so that two primaries are unrepresentable.
- Ownership: an account has at least one holder, each a person, none listed twice.

**4. Best name?**

`Person`, `Organization`, union `Party`. `PersonalName` with `given`, `middle`, `family`. `PhoneNumber` with axis `PhoneKind`. `EmailAddress` with axis `ContactKind`, shared with address. `Address` unchanged. The set with one preferred member: `Names`, `Phones`, `Emails`, `Addresses`; Plaid says primary, a person says the number they prefer to be reached on, so preferred is the thing and primary is a flag on the vendor's row. `owners` on each account kind, holding `PartyId`s.

**5. The source's account, not the thing?**

`names` as flat strings: Plaid's rendering of a structured name. `primary: true/false` per row: the source marking one member, and a flag per row can be true twice where the thing cannot. `type: "primary" / "secondary"` on emails: rank restated as kind, discarded. `type` on phones as free string: the vendor's label set. `data` as the field name for the value: the vendor's wrapper. `owners` repeated under every account: the person rendered once per account, when the person is one thing and accounts point at him. The account frame and `request_id`: transport, nothing new about accounts here.

**6. Should the world look different?**

Yes. `Party` becomes the union `Person | Organization` on a `kind` axis; today's flat party is the organization arm; `PartyName` becomes `OrganizationName`. `PartyId` stays the one reference type, because accounts can be held by an organization and counterparties can be either, so every holder keeps `PartyId`. Every account kind gains holders. Preferred-among-a-set is one shape used four times. A person's addresses carry a kind; an organization's stay a plain sequence, since home/work is not an axis an organization has. No household or joint-account thing: a joint account is an account with two owners, already said by the field.

**7. The filled schema** (abridged to shape; the run produced every entry):

```json
{
  "create": [
    {"name": "Person", "is": "a natural human who holds accounts, one thing across all accounts and institutions", "must": ["at least one name form", "identified by PartyId"], "holds": ["Names", "Phones", "Emails", "Addresses"]},
    {"name": "PersonalName", "is": "a structured name a person goes by", "must": ["given and family required, middle optional", "no blank part"]},
    {"name": "Phones", "is": "a person's phones, each of a PhoneKind, with the one they prefer", "must": ["one preferred when non-empty", "the rest others"]}
  ],
  "change": [
    {"name": "Party", "becomes": "union of Person | Organization on kind"},
    {"name": "PartyName", "becomes": "OrganizationName"},
    {"name": "Account", "becomes": "every kind gains owners: one or more PartyId, no repeats"}
  ],
  "unchanged": ["PartyId", "Address", "Connection.institution", "StudentLoan.servicer", "StudentLoan.guarantor", "WithParty.party"]
}
```

## 3. Constructs

**1. Construct per entry.** `PartyKind`: union axis, `StrEnum` {person, organization}. `Person`: concept model pinning `PartyKind.PERSON`, with `id`, `names`, `phones`, `emails`, `addresses`; equal on `id`. `Organization`: concept model pinning `ORGANIZATION`, with `id`, `name: OrganizationName`, `addresses: tuple[Address, ...]`; equal on `id`. `Party`: the discriminated union alias. `GivenName`, `FamilyName`: semantic scalars over `str`, pattern `\S`; middle names are given names. `PersonalName`: value object of `given`, `middle: tuple[GivenName, ...]`, `family`. `Names`: collection over `PersonalName`, `min_length=1`, ranked: first is the one the person goes by, so rank as position makes two preferred unrepresentable and no flag exists. `PhoneNumber`: scalar, E.164 pattern. `PhoneKind`/`PhoneType`, `ContactKind`/`ContactType`: axis enum and its scalar. `Phone`, `Email`, `ContactAddress`: value objects of the value and its kind. `Phones`, `Emails`, `Addresses`: ranked collections, may be empty. `EmailAddress`: scalar over `EmailStr`. `OrganizationName`: today's `PartyName` renamed. `Owners`: collection over `PartyId`, `min_length=1`; no-repeat is not provable by a tuple and the whitelist admits no set, so it is the one escaped invariant, stated in the docstring. Six account kinds each gain `owners: Owners`.

**2. Holders of changed things.** `Party` → union: no holder imports `Party` itself; nothing becomes. `PartyName` → `OrganizationName`: held only by `Party.name`, becomes `Organization.name`. `Account` gains owners: the six kinds in `account/account.py`, each gains `owners: Owners`. `PartyId` holders unchanged: `Connection.institution`, `StudentLoan.servicer`, `StudentLoan.guarantor`, `WithParty.party`.

**3. Placement.** `party/type.py`: the scalars and both axes. `party/value.py`: `PersonalName`, `Phone`, `Email`, `ContactAddress`. `party/person.py`: the four collections and `Person`. `party/organization.py`: `Organization`. `party/party.py`: the union alone. `account/ownership.py`: `Owners`. `account/account.py`: the six kinds.

**4. Breaks.** Every entry received four written lines. Three worth showing: `PhoneKind` and `ContactKind` share home, work, other and are not duplicated, because they are two axes in nature, decided in question 3. `Names`, `Phones`, `Emails`, `Addresses` are not escaped, because rank is position, a structure, and not duplicated, because no `primary` flag sits beside the position. `Owners` is escaped, once, the no-repeat invariant, admitted and stated.

**5. The filled schema.** Every construct above with its file, its fields, and for `Person` and `Organization` `"equals": ["id"]`; the six account holders; `removed: ["PartyName"]`.

## What the run shows

Two witnesses that never met agreed on the shape of a person, and the ontology already built supplied the third. Every vendor rendering was named as rendering and discarded. The one conflict, a flat party against a structured person, resolved by looking harder into a union, not by a ruling. The one invariant no construct can carry was written down as an escape rather than hidden in a validator. And the build had nothing left to invent.
