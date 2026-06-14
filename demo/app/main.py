"""Composition root: the program's one wiring site. Construct config, fire up the
clients, bind them to the consistency model, register or invoke the routes. No domain
logic, no domain model. This and a route reply are the only places `.root` and
`get_secret_value()` cross to the wire. A build overwrites this file.
(docs/construct.md: composition root)"""
