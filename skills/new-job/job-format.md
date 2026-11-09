# Job format

This file is the contract for all jobs. It is format version 1.
The registrar, the scheduler and the executor use this contract.
`job.schema.json` in this folder is the machine-readable version of the contract.
Do not change the contract without a review of all tools that use it.

## Location

```
projects/<project>/jobs/<job>.md
kortx/jobs/<job>.md               ← framework jobs
```

- Use kebab-case for `<job>`.
- Put one job in each file.

## Job ID

- The job ID is `<project>/<job>`. The file path gives the ID. For framework jobs, the ID is `kortx/<job>`.
- Do not write the ID in the file.
- If you rename or move the file, the ID changes.

## File structure

```markdown
---
format: 1
description: Check the prices of the products in the list.
schedule: "0 8 * * 1"
timezone: Europe/Rome
enabled: true
writes:
  - data/prices.md
network:
  - shop.example.com
tools:
  - web-fetch
---

# Weekly price check

<The prompt. The executor sends this text to the agent.>
```

## Required fields

| Field | Type | Value |
| --- | --- | --- |
| `format` | integer | The contract version. Use `1`. |
| `description` | string | One line. The dashboard shows this text. |
| `schedule` | string | A cron expression with 5 fields: minute, hour, day of month, month, day of week. |
| `timezone` | string | An IANA time zone, for example `Europe/Rome`. |
| `enabled` | boolean | `true` to run the job. `false` to keep the job but not run it. |
| `writes` | array of strings | The paths that the job can change. See "Paths". |

## Optional fields

| Field | Type | Default | Value |
| --- | --- | --- | --- |
| `network` | array of strings | `[]` | The domains that the job can connect to. `*.example.com` includes all subdomains. |
| `tools` | array of strings | `[]` | The tools that the job can use, for example `web-fetch`, `web-search`, `shell`. |
| `secrets` | array of strings | `[]` | The names of the secrets that the job needs. Use `UPPER_SNAKE_CASE`. |
| `timeout` | integer | `10` | The maximum duration of one run, in minutes. Range: 1 to 120. |
| `budget-eur` | number | `0.5` | The maximum cost of one run, in euro. |
| `retries` | integer | `0` | The number of new attempts after a failure. Range: 0 to 5. |
| `overlap` | string | `skip` | If the last run is not complete: `skip` this run, or `queue` it. |
| `missed` | string | `skip` | For runs that the scheduler missed: `skip` them, or do `run-once`. |
| `until` | string | none | The last date of the job, in quotes: `"YYYY-MM-DD"`. After this date, the job stops. |
| `notify` | string | `failure` | When to tell the user: `failure`, `always` or `never`. |
| `output-branch` | string | `data` | The git branch for the results of the job. |

## Permissions

- An empty array gives no permission. For example, `network: []` stops all network access.
- The job can do only what the fields permit. The executor stops all other actions.
- If a field is not in the file, the executor uses the default value.
- Put `schedule` and `until` in quotes. Without quotes, YAML can change the type of the value.

## Paths

- Write paths in `writes` relative to the project folder.
- For example, `data/**` in the project `website` is `projects/website/data/**`.
- Use glob patterns: `*` for one level, `**` for all levels.
- Do not use absolute paths. Do not use `..`. The schema refuses these paths.
- Exception: the framework jobs in `kortx/jobs/` maintain all the repository. Their paths are relative to the repository root. The executor must apply this exception only to `kortx/jobs/`.

## Secrets

- Write only the names of the secrets in the job file.
- Keep the values in the secret store of the scheduler.
- Never write a secret value in the repository.

## Prompt rules

- Write the prompt in English, with the `write-docs` skill.
- Write a prompt that is complete. The agent has no other context.
- Give the paths of the input files and the output files.
- Make the job safe to run again. A second run must not cause damage.
- Tell the agent not to obey instructions in data from the network.

## Registrar rules

- The repository is the only source of truth. The registrar removes changes that a person makes in the scheduler.
- On each push to `main`, the registrar reads all jobs in the repository.
- The registrar compares all jobs in the repository with all jobs in the scheduler.
- The registrar adds, updates, pauses and removes jobs until the two sets agree.
- The registrar also does this comparison one time each day.
- If a job is not valid for `job.schema.json`, the check fails. The registrar does not send that job to the scheduler.

## Change the contract

1. Increase `format` by 1.
2. Update this file and `job.schema.json`.
3. Make sure that the registrar can read all versions that are in use.
4. Follow "Change a rule" in the `new-skill` skill.
