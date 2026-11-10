---
name: new-skill
description: Add a new skill, or change the rules of a skill or a contract. Use it when no skill is applicable to a task, or when a rule must change.
---

# New skill

## Procedure

1. Make sure that no skill in `skills/README.md` does the same task.
2. Get a name from the user. Use kebab-case.
3. Decide the location:
   - For many projects, use `skills/<name>/`.
   - For one unit only, use `projects/<unit>/skills/<name>/`.
4. Write `SKILL.md` with the structure below.
5. Write the text with the `write-docs` skill.
6. Add the skill to the applicable index:
   - For a skill in `skills/`, use `skills/README.md`.
   - For a unit skill, use the `Structure` table of the unit `README.md`.
7. Make the link of the skill in `.agents/skills/`. Agents find skills only through these links.
   - For a skill in `skills/`, run `ln -s ../../skills/<name> .agents/skills/<name>`.
   - For a unit skill, follow "Skills" in `skills/new-project/unit-format.md`.
8. Make a commit with the `commit` skill.

## Structure of SKILL.md

```
---
name: <name>
description: <What the skill does. When to use it.>
---

# <Name>

## Procedure

1. <Step>

## Rules

- <Rule>
```

## Rules

- Give each skill one task only.
- Keep `SKILL.md` short. Put long reference data in other files in the skill folder.
- Write a clear description. Agents use the description to select the skill.
- For a unit skill, write the name of the unit in the description.

## Change a rule

1. Change the rule in the skill or in the contract.
2. If a script can check the rule, update `.github/scripts/check-repo.py` in the same commit.
3. Do not change the existing files that do not agree with the new rule.
4. Make a commit with the `commit` skill.

The check reports the files that do not agree. The audit job corrects them.
Add a task to a backlog only if the migration needs a decision of the user.
