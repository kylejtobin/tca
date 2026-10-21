"""``python -m type_construction.cli <program> <route> [options]``: the program's name first."""

import sys

from type_construction.cli import main

sys.exit(main(sys.argv[2:], name=sys.argv[1]))
