"""Show the root folder of the kortx repository."""

import argparse

from kortx.repo import find_root

NAME = "root"
HELP = "Show the root folder of the kortx repository."


def configure(parser: argparse.ArgumentParser) -> None:
    pass


def run(args: argparse.Namespace) -> int:
    print(find_root())
    return 0
