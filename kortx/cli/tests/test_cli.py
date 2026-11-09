"""Tests for the entry point and the repository root."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from kortx import repo
from kortx.cli import main
from kortx.commands import COMMANDS


def make_repo(path: Path) -> Path:
    for marker in repo.MARKERS:
        if "." in marker:
            (path / marker).touch()
        else:
            (path / marker).mkdir()
    return path


class TestCommands(unittest.TestCase):
    def test_names_are_unique(self):
        names = [c.NAME for c in COMMANDS]
        self.assertEqual(len(names), len(set(names)))

    def test_each_command_has_the_interface(self):
        for command in COMMANDS:
            for attribute in ("NAME", "HELP", "configure", "run"):
                self.assertTrue(hasattr(command, attribute), f"{command.__name__}.{attribute}")

    def test_no_command_shows_help(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(main([]), 2)


class TestFindRoot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = make_repo(Path(self.tmp.name).resolve())
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        os.environ.pop(repo.ENV_ROOT, None)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_finds_root_from_subfolder(self):
        sub = self.root / "projects" / "a" / "b"
        sub.mkdir(parents=True)
        self.assertEqual(repo.find_root(sub), self.root)

    def test_uses_environment_variable(self):
        os.environ[repo.ENV_ROOT] = str(self.root)
        self.assertEqual(repo.find_root(Path("/")), self.root)

    def test_refuses_wrong_environment_variable(self):
        os.environ[repo.ENV_ROOT] = self.tmp.name + "/missing"
        with self.assertRaises(repo.RepoNotFoundError):
            repo.find_root()

    def test_fails_outside_a_repository(self):
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(repo.RepoNotFoundError):
                repo.find_root(Path(other))

    def test_error_message_for_user(self):
        with tempfile.TemporaryDirectory() as other:
            cwd = os.getcwd()
            os.chdir(other)
            try:
                with mock.patch("sys.stderr"):
                    self.assertEqual(main(["root"]), 1)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
