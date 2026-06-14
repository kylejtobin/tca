"""The transport edge for this context. The route is the function at ingress: it
constructs a contract or foreign model from raw transport, dispatches the innermost
value to a verb, and serializes the reply, computing no domain fact. Contract models,
this program's own request and reply shapes, live here too. A build overwrites this
file. (docs/construct.md: route, contract model)"""
