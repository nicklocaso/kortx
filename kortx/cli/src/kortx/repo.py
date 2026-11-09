"""Find the root folder of the kortx repository: the framework or an instance."""

import os
from pathlib import Path

ENV_ROOT = "KORTX_ROOT"
MARKERS = ("AGENTS.md", "skills", "projects")


class RepoNotFoundError(Exception):
    """The kortx repository root is not found."""


def is_root(path: Path) -> bool:
    return all((path / marker).exists() for marker in MARKERS)


def find_root(start: Path | None = None) -> Path:
    """Return the repository root.

    Use the KORTX_ROOT environment variable if it is set.
    Else, search from the start folder up to the file system root.
    """
    env = os.environ.get(ENV_ROOT)
    if env:
        root = Path(env).expanduser().resolve()
        if not is_root(root):
            raise RepoNotFoundError(f"{ENV_ROOT}={env} is not a kortx repository.")
        return root
    path = (start or Path.cwd()).resolve()
    for candidate in (path, *path.parents):
        if is_root(candidate):
            return candidate
    raise RepoNotFoundError(
        f"No kortx repository in {path} or its parent folders. Set {ENV_ROOT}."
    )
