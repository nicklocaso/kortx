# Unit format

This file is the contract for all units.
Agents, the check and the dashboard use this contract.
Do not change it without a review of all tools that use it.

## Definition

- A unit is a folder in `projects/` with `README.md` and `backlog.md`.
- The `backlog.md` file identifies a unit. A folder without `backlog.md` is a normal folder of its unit.
- Each folder directly in `projects/` is a unit.
- A unit can contain other units. A child unit is directly in the folder of its parent unit.
- The framework unit is `kortx/`. It is not in `projects/`.

## Location

```
projects/<unit>/                  ← unit
projects/<unit>/<child>/          ← child unit
```

For example, in a work instance, `projects/acme/` is a client and `projects/acme/api/` is a repository of the client.

## Unit name

- The unit name is the path relative to `projects/`, for example `website` or `acme/api`.
- Use kebab-case for each folder of the path.
- The name `kortx` is reserved for the framework unit. Do not make `projects/kortx/`.

The unit name gives the references:

| Reference | Format | Example |
| --- | --- | --- |
| Task | `<unit>#<ID>` | `acme/api#T4` |
| Job | `<unit>/<job>` | `acme/api/weekly-report` |
| Commit scope | `<unit>` | `docs(acme/api): add release tasks` |

## README.md

- Use the structure of `template/README.md` in this folder.
- Keep the sections `Purpose`, `Status`, `Structure` and `Notes`.
- Write one status in `Status`: `active`, `paused` or `done`.
- Make sure that each path in the `Structure` table exists.

## Units section

A parent unit has a `Units` section in its `README.md`, after `Structure`:

```markdown
## Units

| Unit | Purpose |
| --- | --- |
| `api` | The backend of the client. |
```

- Write one row for each child unit. Write the folder name, not the full unit name.
- Each row must have a folder with `backlog.md`.
- A unit with no child units does not need this section.

## Index

- Put each unit that is directly in `projects/` in the index of `projects/README.md`.
- Put each child unit only in the `Units` section of its parent unit.

## Jobs

- A job of a unit can write only in its unit. It cannot write in a child unit.
- See `skills/new-job/job-format.md`.

## Change the contract

Follow "Change a rule" in the `new-skill` skill.
