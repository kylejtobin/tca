# type-construction-cli

Runs a TCA program's route from the command line. The options are rendered from the request's JSON schema, the parsed options are read back into the request by the same schema nodes, the route is answered through the engine with every connection opened around it, and the reply's computed fields are printed as JSON.

`shop --help` lists the routes and the environment variables the config reads; `shop checkout --help` lists the request's options with their descriptions and constraints. A program that does not prove, a request that does not construct, or a deployment missing a variable prints the `ValidationError` and exits 1; an unknown route exits 2.
