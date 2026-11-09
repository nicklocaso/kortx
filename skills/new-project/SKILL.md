---
name: new-project
description: Add a new project or a child unit to the projects folder. Use it when the user starts a project or adds a unit to a project.
---

# New project

## Procedure

1. Read `unit-format.md` in this folder.
2. Get a name from the user. Use kebab-case.
3. Ask the user for the parent unit, if the new unit is a child unit.
4. Find the unit name: `<name>`, or `<parent>/<name>` for a child unit.
5. Make sure that `projects/<unit>/` does not exist.
6. Copy `template/` to `projects/<unit>/`.
7. Write the purpose of the unit in `projects/<unit>/README.md`.
8. For a unit of an external repository, write the `Repositories` section in `projects/<unit>/README.md`. Get the URL and the local clone from the user.
9. Add the first tasks to `projects/<unit>/backlog.md` with the `backlog` skill.
10. Add the unit to the index:
    - For a unit directly in `projects/`, use the index in `projects/README.md`.
    - For a child unit, use the `Units` section in the `README.md` of the parent unit.
11. Make a commit with the `commit` skill.
12. For a unit of an external repository, tell the user how to work on the repository. See "Work on an external repository".

## Code location

- Keep code that applies the rules of the framework in `kortx/`. Change it only in the kortx repository.
- Keep the code of an independent product in its own repository.
- For an independent product, the unit contains only Markdown files and `data/`. Write the repository URL in the `Repositories` section. See `unit-format.md`.

## Work on an external repository

Open the local clone and the instance in one agent session. Start the session in the local clone, and add the instance.
If you start in the instance, the agent can lose the rules of the external repository.

Example for Claude Code:

```
cd ~/work/acme/api
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ~/my-instance
```

- Without the variable, Claude Code does not read the `CLAUDE.md` file of a folder that `--add-dir` adds. Thus it does not read the rules of the instance.
- Claude Code reads the skills of the added folders also without the variable.

Rules for each repository:

- The precedence of the rules is in `AGENTS.md`.
- Before a commit, make sure that it is in the correct repository. Put code in the local clone. Put notes, tasks and jobs in the instance.

## Rules

- Keep all unit files in the unit folder.
- Put rules for the unit in `projects/<unit>/README.md`.
- Put skills for one unit only in `projects/<unit>/skills/`.
- Put skills for many units in the root `skills/` folder.
- Put tasks in `projects/<unit>/backlog.md`. Use the `backlog` skill.
- Put recurring jobs in `projects/<unit>/jobs/`. Use the `new-job` skill.
