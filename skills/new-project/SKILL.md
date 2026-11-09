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
8. Add the first tasks to `projects/<unit>/backlog.md` with the `backlog` skill.
9. Add the unit to the index:
   - For a unit directly in `projects/`, use the index in `projects/README.md`.
   - For a child unit, use the `Units` section in the `README.md` of the parent unit.
10. Make a commit with the `commit` skill.

## Code location

- Keep code that applies the rules of the framework in `kortx/`. Change it only in the kortx repository.
- Keep the code of an independent product in its own repository.
- For an independent product, the project folder contains only `README.md`, `backlog.md` and `jobs/`. Write the repository URL in the `Purpose` section.

## Rules

- Keep all unit files in the unit folder.
- Put rules for the unit in `projects/<unit>/README.md`.
- Put skills for one unit only in `projects/<unit>/skills/`.
- Put skills for many units in the root `skills/` folder.
- Put tasks in `projects/<unit>/backlog.md`. Use the `backlog` skill.
- Put recurring jobs in `projects/<unit>/jobs/`. Use the `new-job` skill.
