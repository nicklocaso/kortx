#!/usr/bin/env python3
"""Check the repository against its rules and contracts.

Usage:
    check-repo.py [--changed FILE ...] [--all-strict] [--report PATH]

Each issue belongs to a path. An issue is an error if its path is in the
changed files of the push. Other issues are warnings: they go in the report
only. The audit job corrects the warnings.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(\.[a-z0-9]+)*$")
PYTHON_NAME = re.compile(r"^(__[a-z]+__|[a-z][a-z0-9]*(_[a-z0-9]+)*)$")
NAME_EXCEPTIONS = {"README.md", "AGENTS.md", "CLAUDE.md", "SKILL.md", "LICENSE", "LICENSE-DOCS"}
AGENTS_MAX_LINES = 50
MEMORY_MAX_LINES = 100
FRAMEWORK_UNIT = "kortx"
PROJECT_SECTIONS = ["Purpose", "Status", "Structure", "Notes"]
PROJECT_STATUS = {"active", "paused", "done"}
BACKLOG_SECTIONS = ["Doing", "Next", "Blocked", "Later", "Done"]
BACKLOG_DOING_MAX = 3
BACKLOG_DONE_MAX = 20
TASK_MAX_WORDS = 15
TASK_LINE = re.compile(
    r"^- (?P<id>T\d+) "
    r"(?:(?P<date>\d{4}-\d{2}-\d{2}) )?"
    r"(?P<text>.+?)"
    r"(?: after:(?P<after>T\d+(?:,T\d+)*))?"
    r"(?: waits:(?P<waits>.+))?$"
)
MEMORY_LINE = re.compile(r"^- \d{4}-\d{2}-\d{2}: .+$")
INDEX_ROW = re.compile(r"^\| `([^`]+)` \|", re.MULTILINE)


class Checker:
    def __init__(self):
        self.issues = []

    def add(self, path, rule, message):
        self.issues.append({"path": str(path), "rule": rule, "message": message})


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def subdirs(path):
    return sorted(p.name for p in (ROOT / path).iterdir() if p.is_dir())


def front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    return yaml.safe_load(text[4:end])


def sections(text):
    """Return the level-2 headings and the lines under each heading."""
    result = {}
    order = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            result[current] = []
        elif current is not None and line.strip():
            result[current].append(line)
    return order, result


def check_agents(c):
    lines = read("AGENTS.md").splitlines()
    if len(lines) > AGENTS_MAX_LINES:
        c.add("AGENTS.md", "agents-length", f"{len(lines)} lines. The limit is {AGENTS_MAX_LINES}.")


def check_index(c, index_file, folder, items):
    listed = set(INDEX_ROW.findall(read(index_file)))
    for name in sorted(set(items) - listed):
        c.add(f"{folder}/{name}", "index", f"Not in {index_file}.")
    for name in sorted(listed - set(items)):
        c.add(index_file, "index", f"{name} is in the index but does not exist.")


def check_skills(c):
    skills = subdirs("skills")
    check_index(c, "skills/README.md", "skills", skills)
    for name in skills:
        path = f"skills/{name}/SKILL.md"
        if not (ROOT / path).exists():
            c.add(f"skills/{name}", "skill", "SKILL.md is missing.")
            continue
        meta = front_matter(read(path)) or {}
        if meta.get("name") != name:
            c.add(path, "skill", "The name in the front matter is not the folder name.")
        if not meta.get("description"):
            c.add(path, "skill", "The description is missing.")


def check_projects(c):
    projects = subdirs("projects")
    check_index(c, "projects/README.md", "projects", projects)
    units = [f"projects/{name}" for name in projects]
    if (ROOT / FRAMEWORK_UNIT).is_dir():
        units.append(FRAMEWORK_UNIT)
    for unit in units:
        check_project_readme(c, unit)
        check_backlog(c, unit)
        check_jobs(c, unit)


def check_project_readme(c, folder):
    path = f"{folder}/README.md"
    if not (ROOT / path).exists():
        c.add(folder, "project", "README.md is missing.")
        return
    order, content = sections(read(path))
    for section in PROJECT_SECTIONS:
        if section not in order:
            c.add(path, "project", f"The section '{section}' is missing.")
    status = [l.strip() for l in content.get("Status", [])]
    if status and status[0] not in PROJECT_STATUS:
        c.add(path, "project", f"The status '{status[0]}' is not valid.")
    for listed in INDEX_ROW.findall("\n".join(content.get("Structure", []))):
        if not (ROOT / folder / listed.rstrip("/")).exists():
            c.add(path, "structure", f"{listed} is in the structure table but does not exist.")


def check_backlog(c, folder):
    path = f"{folder}/backlog.md"
    if not (ROOT / path).exists():
        c.add(folder, "backlog", "backlog.md is missing.")
        return
    order, content = sections(read(path))
    if order != BACKLOG_SECTIONS:
        c.add(path, "backlog", f"The sections must be {', '.join(BACKLOG_SECTIONS)}, in this sequence.")
    ids = {}
    tasks = []
    for section in order:
        for line in content[section]:
            m = TASK_LINE.match(line)
            if not m:
                c.add(path, "backlog", f"Line not valid: {line}")
                continue
            tasks.append((section, m))
            ids[m["id"]] = ids.get(m["id"], 0) + 1
    done_path = ROOT / folder / "backlog-done.md"
    if done_path.exists():
        for line in done_path.read_text(encoding="utf-8").splitlines():
            m = TASK_LINE.match(line)
            if m:
                ids[m["id"]] = ids.get(m["id"], 0) + 1
    for task_id, count in ids.items():
        if count > 1:
            c.add(path, "backlog", f"The ID {task_id} is used {count} times.")
    open_ids = {m["id"] for section, m in tasks if section != "Done"}
    for section, m in tasks:
        if section == "Done" and not m["date"]:
            c.add(path, "backlog", f"{m['id']} is in Done without a date.")
        if section != "Done" and m["date"]:
            c.add(path, "backlog", f"{m['id']} has a date but it is not in Done.")
        if section == "Blocked" and not m["waits"]:
            c.add(path, "backlog", f"{m['id']} is in Blocked without a waits: tag.")
        if len(m["text"].split()) > TASK_MAX_WORDS:
            c.add(path, "backlog", f"{m['id']} has more than {TASK_MAX_WORDS} words.")
        for dep in (m["after"] or "").split(","):
            if dep and section != "Done" and dep not in open_ids:
                c.add(path, "backlog", f"{m['id']} is after {dep}, but {dep} is not open.")
    if len(content.get("Doing", [])) > BACKLOG_DOING_MAX:
        c.add(path, "backlog", f"Doing has more than {BACKLOG_DOING_MAX} tasks.")
    if len(content.get("Done", [])) > BACKLOG_DONE_MAX:
        c.add(path, "backlog", f"Done has more than {BACKLOG_DONE_MAX} tasks. Move old tasks to backlog-done.md.")


def check_jobs(c, folder):
    jobs = ROOT / folder / "jobs"
    if not jobs.is_dir():
        return
    schema = json.loads(read("skills/new-job/job.schema.json"))
    validator = jsonschema.Draft202012Validator(schema)
    for job in sorted(jobs.glob("*.md")):
        path = rel(job)
        try:
            meta = front_matter(job.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            c.add(path, "job", f"The front matter is not valid YAML: {error}")
            continue
        if meta is None:
            c.add(path, "job", "The front matter is missing.")
            continue
        for error in validator.iter_errors(meta):
            where = "/".join(str(p) for p in error.absolute_path) or "front matter"
            c.add(path, "job", f"{where}: {error.message}")


def check_memory(c):
    files = sorted(p.name for p in (ROOT / "memory").glob("*.md") if p.name != "README.md")
    check_index(c, "memory/README.md", "memory", files)
    for name in files:
        path = f"memory/{name}"
        lines = read(path).splitlines()
        if len(lines) > MEMORY_MAX_LINES:
            c.add(path, "memory", f"{len(lines)} lines. The limit is {MEMORY_MAX_LINES}.")
        for line in lines:
            if line.startswith("- ") and not MEMORY_LINE.match(line):
                c.add(path, "memory", f"Entry not valid: {line}")


def tracked_files():
    """Return the files that git tracks, or all files if git is not available."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        ).stdout.decode()
        return [f for f in out.split("\0") if f]
    except (OSError, subprocess.CalledProcessError):
        return [
            rel(Path(d) / f)
            for d, _, files in os.walk(ROOT)
            if "/." not in d.replace(str(ROOT), "")
            for f in files
        ]


def check_names(c):
    files = tracked_files()
    packages = {str(Path(f).parent) for f in files if Path(f).name == "__init__.py"}
    seen = set()
    for f in files:
        parts = Path(f).parts
        for i, name in enumerate(parts):
            path = "/".join(parts[: i + 1])
            if path in seen:
                continue
            seen.add(path)
            if any(p.startswith(".") for p in parts[: i + 1]) or name in NAME_EXCEPTIONS:
                continue
            is_file = i == len(parts) - 1
            if is_file and name.endswith(".py"):
                ok = bool(PYTHON_NAME.match(name[:-3]))
                rule = "Python files use snake_case."
            elif not is_file and path in packages:
                ok = bool(PYTHON_NAME.match(name))
                rule = "Python package folders use snake_case."
            else:
                ok = bool(KEBAB.match(name))
                rule = "The name is not in kebab-case."
            if not ok:
                c.add(path, "name", rule)


def is_strict(issue_path, changed, all_strict):
    if all_strict:
        return True
    return any(f == issue_path or f.startswith(issue_path.rstrip("/") + "/") for f in changed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed", nargs="*", default=[], help="Files changed in the push.")
    parser.add_argument("--all-strict", action="store_true", help="Make all issues errors.")
    parser.add_argument("--report", help="Write the report as JSON to this path.")
    args = parser.parse_args()

    c = Checker()
    for check in (check_agents, check_skills, check_projects, check_memory, check_names):
        check(c)

    for issue in c.issues:
        issue["level"] = "error" if is_strict(issue["path"], args.changed, args.all_strict) else "warning"
    errors = [i for i in c.issues if i["level"] == "error"]
    warnings = [i for i in c.issues if i["level"] == "warning"]

    if args.report:
        Path(args.report).write_text(json.dumps({"errors": errors, "warnings": warnings}, indent=2) + "\n")

    for issue in errors + warnings:
        print(f"{issue['level'].upper()} {issue['path']} [{issue['rule']}] {issue['message']}")
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
