---
name: new-job
description: Add or change a recurring job in a project. Use it when the user wants a task that runs on a schedule.
---

# New job

## Procedure

1. Read `job-format.md` in this folder.
2. Get the unit name from the user. Make sure that `projects/<unit>/` exists.
3. Get a job name from the user. Use kebab-case.
4. Get the schedule and the time zone from the user. Write the schedule as a cron expression.
5. Find the minimum permissions for the job: `writes`, `network`, `tools` and `secrets`.
6. Write the prompt with the `write-docs` skill.
7. Write `projects/<unit>/jobs/<job>.md` as `job-format.md` tells you.
8. Validate the front matter with `job.schema.json`.
9. Make a commit with the `commit` skill. Use the `feat` type and the unit name as the scope.

## Rules

- Give the job the minimum permissions only.
- Do not write optional fields that have the default value.
- Tell the user the cron expression in words, for example "every Monday at 08:00".
- Tell the user the permissions of the job. Get approval for `network`, `tools` and `secrets`.
- To stop a job for some time, set `enabled: false`. Do not remove the file.
