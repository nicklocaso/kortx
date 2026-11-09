"""Entry point of the kortx command."""

import argparse
import sys
from importlib.metadata import version

from kortx.commands import COMMANDS
from kortx.repo import RepoNotFoundError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kortx", description="Command line interface of kortx.")
    parser.add_argument("--version", action="version", version=f"kortx {version('kortx')}")
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    for command in COMMANDS:
        sub = subparsers.add_parser(command.NAME, help=command.HELP, description=command.HELP)
        command.configure(sub)
        sub.set_defaults(run=command.run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "run"):
        parser.print_help()
        return 2
    try:
        return args.run(args)
    except RepoNotFoundError as error:
        print(f"kortx: {error}", file=sys.stderr)
        return 1
