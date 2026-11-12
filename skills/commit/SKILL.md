---
name: commit
description: Make a git commit in this repository. Use it for all commits.
---

# Commit

## Message format

Use Conventional Commits:

```
<type>(<optional scope>): <description>
```

## Rules

- Write the message in English.
- Use the imperative mood: "add", not "added".
- Use a maximum of 10 words in the description.
- Use lowercase. Do not put a period at the end.
- Use the unit name as the scope for changes in `projects/`, for example `website` or `acme/api`.
- Do not add a body or trailers, except when the user asks for them.

## Types

| Type | Use it for |
| --- | --- |
| `feat` | A new function or skill. |
| `fix` | A correction of an error. |
| `docs` | A change to documentation only. |
| `refactor` | A change to structure, with no change to behavior. |
| `chore` | Maintenance and configuration. |
| `memory` | A change in `memory/`. |

## Procedure

Many agents can work on this repository at the same time.

1. Make sure that each commit contains one logical change only.
2. Make sure that no secrets are in the change.
3. Write the message.
4. Stage the changes.
5. Run the check:

   ```
   uv run --script .github/scripts/check-repo.py --changed $(git diff --cached --name-only)
   ```

6. If the check shows errors, correct them. Then do steps 4 and 5 again.
7. Make the commit.
8. Run `git push` immediately.
9. If the push fails, run `git pull --rebase`. Then push again.

Warnings in files that you did not change do not stop the commit.
If uv is not available, tell the user that the check did not run.

## Examples

- `feat(skills): add recall skill`
- `memory: add home network configuration`
- `fix(dumper): correct output path on windows`
