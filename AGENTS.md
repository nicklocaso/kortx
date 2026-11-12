# Agent rules

These rules apply to all agents in all harnesses.
The skills contain the details.
These rules apply to the files of this repository. In another repository, the rules of that repository win.

## Instance

- Name: `kortx`, the framework.
- Language of the user: Italian.

## Rules

1. Talk to the user in the language of the instance. Write all repository content in English. Write in English all names that you make, also outside the repository.
2. Apply the ASD-STE100 rules to all text. Use the `write-docs` skill.
3. Do all work through skills. Find them in `skills/README.md`. If no skill is applicable, use `new-skill`.
4. Before you start a task, run `git pull`. Use the `commit` skill for each commit.
5. Save project information in `projects/<project>/`. Save shared information with the `remember` skill.
6. Save only important information. Never save secrets.

## This file

- Keep this file shorter than 50 lines.
- Each instance has its own `Instance` section. The other sections are the same in all instances.
- Add a rule here only if it applies to all tasks. Put all other rules in skills.
