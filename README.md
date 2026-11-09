# kortx

kortx is a framework for a repository that you share with AI agents.
The repository keeps your projects, the memory of the agents, the rules and the skills.
All agents and all harnesses use the same rules.

## Principles

- **Skills do the work.** `AGENTS.md` has only the rules for all tasks. The skills have the details.
- **The repository is the source of truth.** Agents read and write plain Markdown files.
- **Contracts are strict.** Backlogs and jobs have a fixed format. A check validates the format on each push.
- **The text is simple.** All documentation uses the ASD-STE100 writing rules.
- **Harness-neutral.** The skills use the Agent Skills format. They do not depend on one model or one tool.

## Framework and instances

kortx is the framework. An instance is a private repository that uses the framework.

- The framework contains no data of an instance.
- An instance contains your projects and your memory.
- An instance gets framework updates from this repository.
- You can have many instances, for example one for personal work and one for company work.

Do not use a GitHub fork for an instance. A fork of a public repository is public. Use a private repository with an `upstream` remote.

## Structure

| Path | Content |
| --- | --- |
| `AGENTS.md` | Rules for all agents. The `Instance` section is different in each instance. |
| `CLAUDE.md` | Link to `AGENTS.md` for Claude Code. Do not add content. |
| `skills/` | Skills. Each skill is one folder with a `SKILL.md` file. |
| `projects/` | Projects of the instance. Empty in the framework. |
| `memory/` | Shared memory of the instance. Empty in the framework. |
| `kortx/` | The framework project: CLI, backlog, requirements and framework jobs. |
| `.github/` | Repository check: script and GitHub Action. |
| `.claude/skills` | Symbolic link to `skills/` for Claude Code. |

## Make an instance

1. On GitHub, make an empty private repository, for example `my-instance`.
2. Clone kortx and connect the two repositories:

   ```
   git clone https://github.com/nicklocaso/kortx.git my-instance
   cd my-instance
   git remote rename origin upstream
   git remote add origin <URL of your private repository>
   ```

3. In `AGENTS.md`, change the `Instance` section: the name of the instance and your language.
4. Commit and push:

   ```
   git commit -am "chore: configure instance"
   git push -u origin main
   ```

## Update an instance

```
git pull upstream main
```

- Change framework files only in the kortx repository. Then update the instances.
- Change only the `Instance` section of `AGENTS.md` in an instance. Other changes to framework files cause merge conflicts.

## Install the CLI

The CLI runs on Linux and macOS. On Windows, use WSL.

1. Install uv: `brew install uv` on macOS, or see the uv documentation.
2. Add these lines to `~/.zshrc` or `~/.bashrc`. Change the path to the clone of your instance:

   ```
   export KORTX_ROOT="$HOME/my-instance"
   kortx() { uv run --locked --quiet --project "$KORTX_ROOT/kortx/cli" kortx "$@"; }
   ```

3. Open a new terminal. Make sure that the CLI operates:

   ```
   kortx --version
   kortx root
   ```

The CLI uses the code in the clone. After `git pull`, the next command uses the new code.
Do not use `uv tool install`. It does not use `uv.lock`, so the versions of the dependencies can be different.

## Check

A GitHub Action checks the repository on each push.

- An issue in a changed file is an error. The check fails.
- An issue in another file is a warning. The audit job corrects it.

To run the check on your computer:

```
pip install pyyaml jsonschema
python .github/scripts/check-repo.py --all-strict
```

## License

- Markdown files (documentation and skills): [CC BY-SA 4.0](LICENSE-DOCS).
- All other files (code, schemas and configuration): [AGPL-3.0](LICENSE).

If you use or change kortx, keep the copyright notice and the license. Share your changes under the same license.

## Author

Copyright (C) 2026 Nicola Lo Caso ([@nicklocaso](https://github.com/nicklocaso)).
