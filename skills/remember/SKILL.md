---
name: remember
description: Save important information to the shared memory. Use it when the user asks to remember something, or when you find a fact that has long-term value.
---

# Remember

## What to save

Save only information that has long-term value:

- Preferences of the user.
- Decisions and their reasons.
- Configurations and procedures that are difficult to find again.

Do not save:

- Temporary information.
- Information that is already in a project folder.
- Secrets: passwords, tokens, keys or personal identification data.

## Procedure

1. Use the `recall` skill to find the applicable topic file.
2. If no topic file is applicable, make `memory/<topic>.md`. Use kebab-case.
3. Add the entry to the file.
4. If the new entry replaces an old entry, remove the old entry.
5. If you made a new file, add it to the index in `memory/README.md`.
6. Make a commit with the `commit` skill. Use the `memory` type.

## Entry format

```
- YYYY-MM-DD: <one fact, in one sentence>
```

## Rules

- Write one fact in each entry.
- Keep each topic file short. If a file has more than 100 lines, divide it into two topics.
