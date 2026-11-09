"""All commands of the CLI.

To add a command:
1. Add a module in this package with `NAME`, `HELP`, `configure(parser)` and `run(args)`.
2. Add the module to `COMMANDS`.
"""

from kortx.commands import root

COMMANDS = [
    root,
]
