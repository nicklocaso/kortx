# Framework requirements

This file gives the known requirements for the framework.

## Instances

- An instance is one private repository. It uses kortx as its `upstream` remote.
- A user can have many instances, for example a personal instance and a work instance.
- All instances use the same framework.
- The framework contains no data of an instance.
- The data of one instance must not go into another instance.
- Each instance repository is in the account of its owner. A work instance is in the company account.

## Harnesses

- The framework must not depend on one harness.
- An instance can use one harness or many harnesses, for example Claude Code, claude.ai or Codex.

## Platforms

- Use only POSIX systems: Linux and macOS.
- On Windows, use WSL.

## Structure

- A unit is a folder with `README.md` and `backlog.md`.
- A unit can contain other units.
- In a personal instance, a unit is usually a project. A project can have zero or more repositories.
- In a work instance, a unit can be a client. A client unit contains one unit for each repository: `projects/<client>/<repository>/`.
- An instance never contains the code of an external repository. The unit `README.md` has a `Repositories` section with the URL and the path of the local clone.
- To work on an external repository, the agent opens the clone and the instance together.

## Documents

- Keep original documents that are not Markdown in the Google Drive of the instance.
- Use one Drive folder for each unit, with the same structure as the repository.
- Each unit has an index of its documents: the Drive link, a short description and the Markdown version, if it exists.
- Keep in the repository only small files that code needs.

## Data in the framework

- Do not write names of persons, companies or clients in the framework.
- Exception: the author notice in `README.md`.

## Open questions

- Which executor runs the jobs?
- Where do private instances show the dashboard? GitHub Pages needs a paid plan for private repositories.
