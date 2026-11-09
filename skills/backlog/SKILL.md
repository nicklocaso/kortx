---
name: backlog
description: Add, change, complete or show the tasks of a project. Use it for all work on a project backlog.
---

# Backlog

## Procedure

1. Read `backlog-format.md` in this folder.
2. Run `git pull`.
3. Read `projects/<project>/backlog.md`.
4. Do the change:
   - To add a task, give it a new ID. Put it in the correct section and position.
   - To start a task, move it to `Doing`. If `Doing` has 3 tasks, ask the user first.
   - To block a task, move it to `Blocked`. Add a `waits:` tag.
   - To complete a task, move it to the top of `Done`. Add the date.
   - To remove a task that is not necessary, delete the line. Do not use the ID again.
5. If `Done` has more than 20 tasks, move the oldest to `backlog-done.md`.
6. Make a commit with the `commit` skill. Use the `docs` type and the project name as the scope.

## Rules

- Make sure that the file agrees with `backlog-format.md`.
- Show tasks to the user in the sequence of the file.
- If a task is complete, remove its ID from the `after:` tags of other tasks.
- If `git pull --rebase` shows a conflict on the same ID, give your task a new ID.
