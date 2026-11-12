---
vendor: vercel
api: documented
---

# Vercel

## Account

Write the Vercel team slug in the `Account` column, for example `example-team`.

## CLI

- The adapter uses the official Vercel CLI, version 65.11.0.
- `package.json` and `package-lock.json` in the skill folder lock the CLI and all its dependencies.
- The script installs the CLI in `${XDG_CACHE_HOME:-~/.cache}/kortx/sync-invoices/` with `npm ci --ignore-scripts`. It does not use a global `vercel` command.
- The script sets `VERCEL_TELEMETRY_DISABLED=1`.

The adapter uses these commands:

| Command | Use |
| --- | --- |
| `vercel whoami` | Check the session. |
| `vercel billing invoices list --scope <team> --limit 100 --json` | List the invoices. The script follows `pagination.next`. |
| `vercel billing invoices download <id> --scope <team> -o -` | Download the PDF. |

## Errors

| Error | Step |
| --- | --- |
| `no Vercel session` | Tell the user to run the login command in the error. |
| The team is not found | Make sure that the team slug in the `Invoices` table is correct. |

## Notes

- The PDF and the CLI do not show the card that paid the invoice. The Stripe page of the invoice shows it. To open that page, remove `/pdf` from the PDF link and open the link in a browser.
- Do not write card data in the repository.
