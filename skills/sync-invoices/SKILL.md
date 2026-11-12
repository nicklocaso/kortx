---
name: sync-invoices
description: Download the missing invoices of the SaaS vendors of a unit to the local files folder. Use it when the user asks to get or check the vendor invoices of a unit.
---

# Sync invoices

## Procedure

1. Find the unit. Read the `Invoices` section of the unit `README.md`. See `skills/new-project/unit-format.md`.
2. Make sure that `KORTX_FILES` is set. If it is not set, tell the user to follow "Install the CLI" in `README.md`.
3. For each vendor in the table, read `vendors/<vendor>.md`. If the file has `api: undocumented`, tell the user the risk before the first download.
4. Run the script:

   ```
   uv run --script skills/sync-invoices/sync_invoices.py <unit>
   ```

   To sync one vendor only, add `--vendor <vendor>`.

5. If the script shows `error:`, do the step in the vendor file for that error. Then run the script again.
6. Make sure that the exit code is 0. The last line must show `missing: 0 bad: 0`.
7. Tell the user the new files, the number of paid invoices and the invoices that are not paid.

A vendor that is not in `vendors/` has a unit skill `sync-<vendor>-invoices`. Use that skill for that vendor. The script shows `skip:` for it.

## Rules

- Follow the contract in `invoice-format.md`.
- Use this skill only in an interactive session. Do not use it in a job. A job cannot write outside the repository.
- Never overwrite, move or delete a local invoice.
- Never write tokens, PDF links or card data in the repository.
- If the script shows `bad:`, do not correct the file. Tell the user the path.
