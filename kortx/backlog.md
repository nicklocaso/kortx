# Backlog

## Doing

## Next
- T1 Move check-repo.py into the kortx check command.
- T2 Add tests for kortx check: valid and invalid sample files. after:T1
- T3 Change the check GitHub Action to run kortx check. after:T2
- T4 Warn when a commit in an instance changes framework files.
- T5 Update the GitHub Actions to Node 24 versions. Pin them by commit SHA.
- T6 Choose the job executor.
- T7 Write the registrar GitHub Action. It validates jobs with the schema. after:T6
- T8 Write the run-jobs skill for the executor. after:T6
- T9 Add the kortx run command with uv and PEP 723.
- T10 Add the kortx backlog commands: list, add, start, block, done.
- T11 Change the backlog skill to use the kortx backlog commands. after:T10
- T12 Decide the dashboard hosting for private instances.
- T13 Write the GitHub Action that makes stats.json.
- T14 Build the static dashboard page for mobile and desktop. after:T12,T13

## Blocked

## Later
- T15 Add the kortx job validate command.
- T16 Add the kortx new project and kortx new job commands.
- T17 Support nested units in the check, for clients with many repositories.
- T18 Add a document index for original files in Google Drive.
- T19 Add a rule to update exclude-newer dates in project scripts.

## Done
