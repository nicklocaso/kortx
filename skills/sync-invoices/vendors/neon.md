---
vendor: neon
api: undocumented
---

# Neon

## Account

Write the Neon organization ID in the `Account` column, for example `org-example-00000000`. The ID starts with `org-`. The organization name is not the ID.

## CLI and API

- The adapter uses the official Neon CLI `neonctl`, version 9.3.2, only to refresh the session.
- `package.json` and `package-lock.json` in the skill folder lock the CLI and all its dependencies. The script installs the CLI as for Vercel. See `vercel.md`.
- The adapter lists the invoices with `GET https://console.neon.tech/api/v2/organizations/<org>/billing/invoices`. It sends the OAuth token of `neonctl`.
- The adapter downloads each PDF from the `pdf_url` of the invoice. It does not send the token with this request.

The adapter uses these commands:

| Command | Use |
| --- | --- |
| `neonctl me --no-analytics` | Check and refresh the session. |

## Risks

- The invoice endpoint is not in the Neon API documentation. The Neon Console uses it.
- Neon can change or remove the endpoint at any time. Then the script shows `error:`.
- The tests of the adapter use only fixtures. A real account did not test this version of the adapter.

Before the first download, tell the user these risks.

## Errors

| Error | Step |
| --- | --- |
| `no Neon session` | Tell the user to run the login command in the error. The login stops after 60 seconds. |
| The endpoint gives an error | Tell the user. The user can get the invoices in the Neon Console: Billing, View/Pay invoices. |
| The list has more pages | Tell the user. The adapter does not support pagination. |

## Rules

- Never copy, show or write the token. The script reads it from `~/.config/neonctl/credentials.json` and keeps it in memory only.
