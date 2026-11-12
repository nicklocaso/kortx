---
name: draft-framework-issue
description: Write the draft of an issue for the kortx framework and remove the private data of the instances. Use it when the user wants to report a problem or a proposal to the framework.
---

# Draft framework issue

## Procedure

1. Select the form: `problem` for a problem, `proposal` for a change or a new function.
2. Read `.github/ISSUE_TEMPLATE/<form>.yml`. Use the `label` of each `textarea` field as a `##` heading.
3. Write the draft with the `write-docs` skill. Write one idea only.
4. Write a title of one line.
5. Find the instances that the real case comes from.
6. Collect the private terms of each of these instances:
   - The instance name in the `Instance` section of `AGENTS.md`.
   - The unit names in `projects/`.
   - The URLs and the local clones in the `Repositories` sections.
   - The accounts in the `Invoices` sections.
   - The names of persons, companies and clients in `memory/` and in `projects/`.
   - The URL of the `origin` remote.
   - The name and the email of the git user.
   - The names that the user said in the session.
7. If you cannot read an instance, ask the user for its private terms.
8. Find the private terms in the draft. Also find all IDs, emails, amounts, local paths and private URLs.
9. Replace each item with a generic name. See "Generic names".
10. If you are not sure that a term is private, ask the user.
11. Show the draft and the list of replacements to the user.
12. Tell the user how to open the issue:
    - With the web form "Problem" or "Proposal" at https://github.com/nicklocaso/kortx/issues/new/choose.
    - Or with the command `gh issue create -R nicklocaso/kortx --title "<title>" --body-file <file>`. Write the file outside the repository, for example in `${TMPDIR:-/tmp}`.
    - For a proposal, add `--label enhancement` to the command.

## Generic names

| Item | Generic name |
| --- | --- |
| Client or unit | `acme`, `acme/api`, `website` |
| Instance | `my-instance` |
| Account or organization ID | `example-team`, `example-org` |
| Email | `user@example.com` |
| Invoice number | `INV-0001` |
| Private URL | `https://example.com/...` |
| Local path | `~/files`, `~/work/acme/api` |

## Rules

- Never open the issue. The user opens it.
- Never write the draft in a repository.
- Follow "Data in the framework" in `kortx/requirements.md`.
- Use only Markdown and shell commands. Do not use the tools of one harness.
