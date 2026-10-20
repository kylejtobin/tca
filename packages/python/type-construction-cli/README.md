# type-construction-cli

Runs a TCA program's route from the command line: arguments and standard input as the request, the reply on standard output.

## Notes

- A transport, not part of the engine. It adapts the command line to the edge's one idea of an inbound connection: one arrival in, its answer out.
- The first argument names the route; standard input is the request as JSON, validated as the route's `Request`.
- The reply the fact at rest answers is written to standard output as JSON; partial replies, if the route declares them, are written one per line before it.
- The exit status says what happened: zero for a reply, one for a reply this transport declares a failure, two for a request that is not the contract. A reply carries no status; which replies are failures is declared here.
