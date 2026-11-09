# Backlog format

This file is the contract for all backlogs.
Agents and the dashboard use this contract.
Do not change it without a review of all tools that use it.

## Location

```
projects/<unit>/backlog.md        ← open and recent tasks
projects/<unit>/backlog-done.md   ← old completed tasks
```

`<unit>` is the unit name, for example `website` or `acme/api`. See `skills/new-project/unit-format.md`.

## File structure

```markdown
# Backlog

## Doing
- T3 Write the login page. Test it on mobile.

## Next
- T4 Add the password reset.
- T5 Publish the site. after:T4

## Blocked
- T6 Connect the domain. waits:domain transfer

## Later
- T7 Decide the color theme.

## Done
- T2 2026-11-08 Choose the hosting provider.
```

- Keep the 5 sections in this sequence, also when a section is empty.
- Do not add other sections or other text.

## Sections

| Section | Content |
| --- | --- |
| `Doing` | Tasks in progress. Maximum 3 tasks. |
| `Next` | Tasks to do soon. |
| `Blocked` | Tasks that wait for an external event. Each task has a `waits:` tag. |
| `Later` | Tasks with no plan yet. |
| `Done` | Completed tasks, with the date. Maximum 20 tasks. |

- The section gives the status. To change the status, move the line.
- The sequence of lines gives the priority. The first line is the most important.

## Task line

```
- <ID> [<date>] <text> [after:<ID>,<ID>] [waits:<reason>]
```

| Part | Rule |
| --- | --- |
| `<ID>` | `T` and a number, for example `T12`. |
| `<date>` | `YYYY-MM-DD`. Only in `Done`: the date of completion. |
| `<text>` | One task in the imperative, in English. Use a maximum of 15 words. |
| `after:` | Optional. The IDs of tasks that must be done first. |
| `waits:` | Required in `Blocked`. The external event. Put it at the end of the line. |

## IDs

- An ID is unique in the unit. Never use an ID again.
- The new ID is the highest ID in `backlog.md` and `backlog-done.md`, plus 1.
- The full reference is `<unit>#<ID>`, for example `website#T4` or `acme/api#T4`.
- Use the full reference in other units, in notes and in jobs.

## Archive

- When `Done` has more than 20 tasks, move the oldest tasks to `backlog-done.md`.
- `backlog-done.md` has one `# Backlog done` heading and the task lines, the newest first.

## Other information

- Write decisions in the `Notes` of the unit `README.md`. Do not write them in the backlog.
- Write an open question as a task with a verb, for example "Decide the fan power supply".

## Change the contract

Follow "Change a rule" in the `new-skill` skill.
