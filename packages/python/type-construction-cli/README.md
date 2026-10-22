# type-construction-cli

Runs a TCA program's route from the command line. The command line is the request's type: one subcommand per route, with the options read from the request class through the engine's own reads, a scalar as one option with its bounds in its help, a value as dotted options, a tuple as a repeated option. The parsed options are read back into the tree the request validates from leniently, the program is proven once at startup, the route is answered through the engine with every connection opened around it, and the reply's computed fields are printed as JSON. A program that does not prove, a request that does not construct, a run that stalls or a reply whose word refuses prints the refusal and exits 1.

`tests/type_construction_cli/` holds the program the tests are, and the scenarios in `tests/features/`.
