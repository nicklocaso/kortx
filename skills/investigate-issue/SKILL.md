---
name: investigate-issue
description: Find the root cause of a defect that is reported on the codebase of a unit, and write a verified analysis in the unit folder. Use it before a plan or a fix. Do not use it for an issue of the kortx framework.
---

# Investigate issue

## Procedure

1. Find the unit. Read `projects/<unit>/README.md`.
2. If the unit has no `Repositories` section, stop and tell the user. If the section has many rows, ask the user for the applicable repository.
3. Open the local clone. Follow "Work on an external repository" in `skills/new-project/SKILL.md`. If the session started in the instance, tell the user. Then continue.
4. Read the rules of the clone and the documents about the problem. In the clone, the rules of the clone win.
5. Write the branch and the commit of the clone. Do not pull the clone.
6. Collect the sources of the request:
   - The ticket and its comments.
   - The messages of the requester.
   - The recent commits and pull requests.

   Use the tools of the harness for the sources, for example an MCP server, `git` or `gh`.
7. Write the problem as the requester sees it. Write the source, its date and its words. Remove names and contact data.
8. Trace the code path from the entry point to the result. Read the code itself, not only the comments and the names.
9. CAUTION: Ask the user before you read data of a live environment. In the file and to the user, show only counts, IDs and statuses.
10. Confirm the behavior. Run the code or read the data in a local or test environment. Read live data only after the consent of the user (step 9). Use the skills of the unit, if it has them.
11. Mark each fact as `verified` or `not verified`. For a verified fact, write the file and line, the command or the query.
12. Look for the same root cause in other parts of the codebase.
13. Write the analysis in `projects/<unit>/<topic>.md`:
    - `<topic>` is a short kebab-case English name, for example `invoice-total-rounding`.
    - Do not use `readme`, `backlog` or `backlog-done` as `<topic>`. Do not end it with `-plan`.
    - If the file exists, update it. Do not make a second file.
    - Use these sections: `Problem`, `Sources`, `Root cause`, `Impact`, `Other places`, `Open questions`.
14. Make a commit with the `commit` skill. Use the `docs` type and the unit name as the scope.
15. Give the user the root cause, the path of the file and the open questions. Stop. Do not plan or fix.

## Rules

- Do not change the clone, its data or the tickets. Write only in the unit folder.
- Do not copy personal data or secrets into the repository.
- If a source is not available, write it as an open question.
- Do not mark a fact as verified without a file and line, a command or a query.
- If the user wants a task for the fix, use the `backlog` skill.
