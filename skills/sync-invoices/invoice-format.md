# Invoice format

This file is the contract for all invoice skills.
The `sync-invoices` skill and each unit skill `sync-<vendor>-invoices` use this contract.
Do not change it without a review of all tools that use it.

## Parameters

- The `Invoices` section of the unit `README.md` gives the vendors and the accounts. See `skills/new-project/unit-format.md`.
- The `KORTX_FILES` environment variable gives the files folder of the computer. See "Install the CLI" in `README.md`.

## Location

```
$KORTX_FILES/<instance>/<unit>/invoices/<vendor>/<YYYY>/<YYYY-MM-DD>_<vendor>_<invoice-number>.pdf
```

- `<instance>` is the name in the `Instance` section of `AGENTS.md`. Thus the files of two instances are not in the same folder.
- `<unit>` is the unit name, for example `acme` or `acme/api`.
- `<YYYY-MM-DD>` is the UTC date of issue. `<YYYY>` is the year of that date.
- `<invoice-number>` is the invoice number of the vendor.

For example: `~/files/example/acme/invoices/vercel/2026/2026-10-01_vercel_TEST-0001.pdf`.

## Rules

- The files folder must be outside the repository. Stop if the real path is in the repository.
- Use an invoice number only if it agrees with `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`. Refuse all other numbers.
- Get the date of issue from a time with a time zone. Refuse a time without a time zone.
- Download only paid invoices. The status must be `paid`. Report all other invoices to the user.
- Never overwrite, move or delete a local invoice.
- Write a new invoice to a temporary file in the same folder. Then make the final file only if it does not exist.
- Check each invoice before you make the final file:
  - The file starts with `%PDF-`.
  - The text of the PDF contains the invoice number. Compare letters and digits only.
- A second run downloads nothing.
- Never write tokens, PDF links or card data in the repository. Do not show them in the output.

## Output

Show one line for each event:

| Line | Event |
| --- | --- |
| `new: <path>` | The invoice is new. |
| `not paid: <status> <number>` | The invoice is not paid. It is not downloaded. |
| `missing: <path> (<error>)` | The download failed. |
| `bad: <path>` | The check of the invoice failed. |
| `refused: <vendor> <reason>` | The invoice number or the date is not valid. |
| `error: <message>` | The parameters or the list of invoices are not valid. |
| `skip: <vendor> <reason>` | The vendor has no adapter in this skill. |

The last line is `paid: <N> new: <K> missing: <M> bad: <B>`.

The exit code is:

- 0 if all paid invoices are in the folder and are correct.
- 1 if an invoice is missing or bad.
- 2 if the parameters or a list of invoices are not valid.

## Add a vendor

- For a vendor of many instances, add `vendors/<vendor>.md` and an adapter in `sync_invoices.py`. Do this in the kortx repository.
- For a vendor of one instance only, add a unit skill `sync-<vendor>-invoices`. Use the `new-skill` skill. The unit skill must follow this contract.

A vendor file has this front matter:

```
---
vendor: <vendor>
api: <documented | undocumented>
---
```

Use `undocumented` if the vendor does not document the API that the adapter uses. Then add a `Risks` section.
