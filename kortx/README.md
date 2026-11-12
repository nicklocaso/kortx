# kortx

## Purpose

This is the framework project. It keeps the CLI, the backlog, the requirements and the jobs of the framework.

## Status

active

## Structure

| Path | Content |
| --- | --- |
| `README.md` | This file. |
| `backlog.md` | Tasks of the framework. Use the `backlog` skill. |
| `requirements.md` | Known requirements for the framework and the instances. |
| `jobs/` | Framework jobs. They maintain all the repository. |
| `cli/` | The `kortx` command line interface. |

## CLI design

- Skills tell when and why to do a task. The CLI does the task, so the result is the same each time.
- Commands for repository rules: `kortx check`, `kortx backlog`, `kortx job`.
- Project scripts stay in their projects. `kortx run <project> <script>` runs them.
- The check GitHub Action runs `kortx check`. The check is the same on the computer and on GitHub.

## Technical decisions

- Language: Python 3.12 or later. `uv` installs the correct version on each computer.
- Library: `argparse` from the standard library. The CLI has few commands and must stay small.
- Dependencies: only `pyyaml` and `jsonschema`. Each new dependency needs a reason in the notes.
- Lock file: commit `cli/uv.lock`. The GitHub Action installs with `uv sync --locked`.
- Package: `cli/src/kortx/`. The command is `kortx`. The environment variable is `KORTX_ROOT`.
- Commands: one module for each command in `cli/src/kortx/commands/`. One file lists all commands. Do not use automatic discovery: a new command must be visible in a review.

## Project scripts

- A project script is a `.py` file in a project folder with a PEP 723 metadata block.
- The block declares the dependencies. The block also makes the script available to `kortx run`.
- A `.py` file without the block is not a script for `kortx run`. It cannot run by mistake.
- The script name is the file name without `.py`. Two scripts with the same name in one project are an error.
- `kortx run <project> <script>` runs the script with `uv run`, in an isolated environment.
- A framework script, for example in `skills/sync-invoices/` or `.github/scripts/`, is not a project script. Run it with `uv run --script <path>`.
- Each block has `[tool.uv] exclude-newer` with a date. uv uses only package versions older than this date. The result is the same each time, and a new malicious version cannot enter.

## Development

Run these commands in `kortx/cli/`.

| Task | Command |
| --- | --- |
| Run the tests | `uv run --locked python -m unittest discover -s tests` |
| Run the CLI | `uv run --locked kortx <command>` |
| Add a dependency | `uv add <package>`. Then write the reason in the notes. |

To add a command:

1. Make a module in `cli/src/kortx/commands/` with `NAME`, `HELP`, `configure(parser)` and `run(args)`.
2. Add the module to `COMMANDS` in `cli/src/kortx/commands/__init__.py`.
3. Add tests in `cli/tests/`.

## Notes

- 2026-11-08: Use skills for all work. Keep `AGENTS.md` shorter than 50 lines.
- 2026-11-08: Write repository content in English with ASD-STE100. Talk to the user in the language of the instance.
- 2026-11-09: Define jobs in `projects/<project>/jobs/`. The contract is `skills/new-job/job-format.md`.
- 2026-11-09: The registrar compares all jobs in the repository with all jobs in the scheduler, on each push and one time each day.
- 2026-11-09: Give jobs minimum permissions. `writes` paths are relative to the project folder.
- 2026-11-09: Keep tasks in `backlog.md`. The contract is `skills/backlog/backlog-format.md`.
- 2026-11-09: Check the repository on each push. Issues in changed files are errors. Other issues are warnings.
- 2026-11-09: Do not migrate files when a rule changes. The check reports them. The audit job corrects them.
- 2026-11-09: The audit job writes to the `audit` branch. The user reviews and merges the changes.
- 2026-11-09: Support only POSIX systems. Windows users use WSL.
- 2026-11-09: Python code uses snake_case. All other files and folders use kebab-case.
- 2026-11-09: Use argparse and Python 3.12. Keep the dependencies to pyyaml and jsonschema.
- 2026-11-09: A PEP 723 block makes a script available to `kortx run`. No other registration is necessary.
- 2026-11-09: Run the CLI with a shell function and `uv run --locked`. `uv tool install` does not use the lock file.
- 2026-11-09: Separate the framework from the instances. An instance is a private repository with kortx as `upstream`. Do not use GitHub forks.
- 2026-11-09: Keep the instance settings in the `Instance` section of `AGENTS.md`.
- 2026-11-09: License: AGPL-3.0 for code, CC BY-SA 4.0 for Markdown files.
- 2026-11-09: Commits have no trailers.
- 2026-11-09: A folder in `projects/` with `backlog.md` is a unit. A child unit is in the `Units` section of its parent. The contract is `skills/new-project/unit-format.md`.
- 2026-11-09: The unit name is the path relative to `projects/`. The name `kortx` is reserved. A job cannot write in a child unit.
- 2026-11-09: A unit of an external repository has a `Repositories` section. It contains only Markdown files and data files in `data/`, never code.
- 2026-11-09: Start the session in the repository of the main work. Add the repositories that you only read. In each repository, the rules of that repository apply.
- 2026-11-12: Skills keep downloaded files in `$KORTX_FILES/<instance>/<unit>/`, outside the repository. Invoice skills follow `skills/sync-invoices/invoice-format.md`.
- 2026-11-12: A framework skill locks its npm tools with `package-lock.json` and installs them in the user cache with `npm ci --ignore-scripts`.
