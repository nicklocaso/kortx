---
name: new-project
description: Add a new project to the projects folder. Use it when the user starts a project.
---

# New project

## Procedure

1. Get a project name from the user. Use kebab-case.
2. Make sure that `projects/<name>/` does not exist.
3. Copy `template/` to `projects/<name>/`.
4. Write the purpose of the project in `projects/<name>/README.md`.
5. Add the first tasks to `projects/<name>/backlog.md` with the `backlog` skill.
6. Add the project to the index in `projects/README.md`.
7. Make a commit with the `commit` skill.

## Code location

- Keep code that applies the rules of the framework in `kortx/`. Change it only in the kortx repository.
- Keep the code of an independent product in its own repository.
- For an independent product, the project folder contains only `README.md`, `backlog.md` and `jobs/`. Write the repository URL in the `Purpose` section.

## Rules

- Keep all project files in the project folder.
- Put rules for the project in `projects/<name>/README.md`.
- Put skills for one project only in `projects/<name>/skills/`.
- Put skills for many projects in the root `skills/` folder.
- Put tasks in `projects/<name>/backlog.md`. Use the `backlog` skill.
- Put recurring jobs in `projects/<name>/jobs/`. Use the `new-job` skill.
