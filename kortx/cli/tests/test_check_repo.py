"""Tests for the repository check script, with valid and not valid sample repositories.

The script is .github/scripts/check-repo.py. Task T2 moves these tests into the kortx check command.
"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / ".github" / "scripts" / "check-repo.py"
SCHEMA = REPO / "skills" / "new-job" / "job.schema.json"

spec = importlib.util.spec_from_file_location("check_repo", SCRIPT)
check_repo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_repo)

BACKLOG = "# Backlog\n\n## Doing\n\n## Next\n- T1 Write the first page.\n\n## Blocked\n\n## Later\n\n## Done\n"

JOB = """---
format: 1
description: Update the data.
schedule: "0 8 * * 1"
timezone: Europe/Rome
enabled: true
writes:
{writes}
---

# Job
"""


def readme(name, units=None):
    text = f"# {name}\n\n## Purpose\n\nA test unit.\n\n## Status\n\nactive\n\n## Structure\n\n"
    text += "| Path | Content |\n| --- | --- |\n| `README.md` | This file. |\n\n"
    if units is not None:
        text += "## Units\n\n| Unit | Purpose |\n| --- | --- |\n"
        text += "".join(f"| `{unit}` | A child unit. |\n" for unit in units)
        text += "\n"
    return text + "## Notes\n\n- 2026-11-09: Start the unit.\n"


def index(title, rows):
    return f"# {title}\n\n## Index\n\n| Name | Purpose |\n| --- | --- |\n" + "".join(
        f"| `{row}` | Test. |\n" for row in rows
    )


class CheckTestCase(unittest.TestCase):
    """Make a valid sample repository: a top unit `acme` with the child unit `api`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.write("AGENTS.md", "# Agent rules\n")
        self.write("skills/README.md", index("Skills", ["new-job"]))
        self.write("skills/new-job/SKILL.md", "---\nname: new-job\ndescription: Add a job.\n---\n")
        self.write("skills/new-job/job.schema.json", SCHEMA.read_text(encoding="utf-8"))
        self.write("memory/README.md", index("Memory", []))
        self.write("projects/README.md", index("Projects", ["acme"]))
        self.add_unit("projects/acme", units=["api"])
        self.add_unit("projects/acme/api")
        self.old_root = check_repo.ROOT
        check_repo.ROOT = self.root

    def tearDown(self):
        check_repo.ROOT = self.old_root
        self.tmp.cleanup()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def add_unit(self, folder, units=None):
        self.write(f"{folder}/README.md", readme(Path(folder).name, units))
        self.write(f"{folder}/backlog.md", BACKLOG)

    def add_job(self, folder, *writes):
        self.write(f"{folder}/jobs/update.md", JOB.format(writes="\n".join(f"  - \"{w}\"" for w in writes)))

    def issues(self):
        c = check_repo.Checker()
        for check in (check_repo.check_agents, check_repo.check_skills, check_repo.check_projects,
                      check_repo.check_memory, check_repo.check_names):
            check(c)
        return [(i["path"], i["rule"], i["message"]) for i in c.issues]

    def assertIssue(self, path, rule, text):
        found = [i for i in self.issues() if i[0] == path and i[1] == rule and text in i[2]]
        self.assertTrue(found, f"No {rule} issue for {path} with '{text}'. Issues: {self.issues()}")


class TestValidRepository(CheckTestCase):
    def test_nested_units_have_no_issues(self):
        self.assertEqual(self.issues(), [])

    def test_units_of_three_levels_have_no_issues(self):
        self.add_unit("projects/acme/api", units=["worker"])
        self.add_unit("projects/acme/api/worker")
        self.assertEqual(self.issues(), [])

    def test_folder_with_readme_only_is_not_a_unit(self):
        self.write("projects/acme/tools/README.md", "# Tools\n")
        self.assertEqual(self.issues(), [])

    def test_job_writes_in_its_own_unit(self):
        self.add_job("projects/acme", "data/**", "*.md")
        self.add_job("projects/acme/api", "**")
        self.assertEqual(self.issues(), [])


class TestNotValidRepository(CheckTestCase):
    def test_child_unit_not_in_units_section(self):
        self.add_unit("projects/acme/web")
        self.assertIssue("projects/acme/web", "unit", "Not in the Units section")

    def test_units_section_entry_without_backlog(self):
        self.add_unit("projects/acme", units=["api", "web"])
        self.write("projects/acme/web/README.md", "# Web\n")
        self.assertIssue("projects/acme/README.md", "unit", "web is in the Units section")

    def test_child_unit_in_folder_that_is_not_a_unit(self):
        self.add_unit("projects/acme/tools/worker")
        self.assertIssue("projects/acme/tools/worker", "unit", "is not a unit")

    def test_child_unit_without_readme(self):
        (self.root / "projects/acme/api/README.md").unlink()
        self.assertIssue("projects/acme/api", "project", "README.md is missing")

    def test_child_unit_with_backlog_not_valid(self):
        self.write("projects/acme/api/backlog.md", "# Backlog\n\n## Next\n")
        self.assertIssue("projects/acme/api/backlog.md", "backlog", "The sections must be")

    def test_job_of_child_unit_is_validated(self):
        self.write("projects/acme/api/jobs/update.md", "# No front matter\n")
        self.assertIssue("projects/acme/api/jobs/update.md", "job", "The front matter is missing")

    def test_job_writes_in_child_unit(self):
        for pattern in ("api/**", "**", "a*/data.md"):
            with self.subTest(pattern=pattern):
                self.add_job("projects/acme", pattern)
                self.assertIssue("projects/acme/jobs/update.md", "job", "can change the child unit api")

    def test_unit_not_added_to_git_is_checked(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        self.add_unit("projects/acme/web")
        self.assertIssue("projects/acme/web", "unit", "Not in the Units section")

    def test_reserved_unit_name(self):
        self.write("projects/README.md", index("Projects", ["acme", "kortx"]))
        self.add_unit("projects/kortx")
        self.assertIssue("projects/kortx", "unit", "reserved for the framework")


if __name__ == "__main__":
    unittest.main()
