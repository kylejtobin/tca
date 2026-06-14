"""Command entry point for running the gate package from the repository tree.

The hook command invokes ``python .claude/scripts/tca_gate`` from the project
root. Python starts this file as a script, not as an installed package, so the
parent scripts directory is added to ``sys.path`` before importing
``tca_gate.cli``.
"""

import sys
from pathlib import Path

# Keep this bootstrap here, and only here: the importable package modules should
# not mutate import state just to support hook execution.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tca_gate.cli import main

if __name__ == "__main__":
    main()
