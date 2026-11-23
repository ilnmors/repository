# Banksalad → Sure Import

Procedure for an import from a Banksalad export. Give this file, the other documents in this directory and the private notes ([private/notes.md](../private/notes.md), outside Git) to the agent (Claude Code, Codex, OpenCode).

## Input

- Banksalad app > Household ledger > Settings > Export to file. Put the emailed xlsx into an agreed OxiCloud WebDAV folder.
  - Sheet `가계부 내역`: date, time, type, major, minor, description, amount (expenses negative), currency, payment method, memo.
  - Sheet `뱅샐현황`: a snapshot at export time (assets, debts, loans). It is not history.
- On the console, mount the WebDAV share from GNOME Online Accounts to read the file.

## Access

- The homelab is reachable only with the WireGuard connection up.
- SSH uses `id_console` with its certificate. Check the host CA fingerprint `SHA256:6tqfzyeeEgf6XkSgjrbMqQnzlvIrAF2XN640prQ4PYw` before trusting it.
  - Sure runs on the app host.
  - PostgreSQL `sure_db` runs on the infra host.
- Run Sure code by copying a script in with `podman cp`, then `podman exec sure-web bin/rails runner <script>`. Remove the script afterwards.

## Safety Rules

- Passwords come through a hidden-input terminal into a 0600 file under `$XDG_RUNTIME_DIR`; `shred -u` it afterwards.
- Workbook copies and intermediate JSON stay under `$XDG_RUNTIME_DIR` and are shredded at the end.
- Print only summary statistics (counts, match results, ratios), never amounts or merchants.
- Back up first:
  1. Run `systemctl --user start postgresql-data-backup@sure.service` on infra.
  2. Copy the dump under a dated name, because a second run on the same day overwrites it.
- Apply scripts run in one database transaction: a dry run without `--commit` (rolled back) first, then commit only if the counts are right.
- Ask the user before applying any new mapping or a new way of handling data.

## Steps

1. **Survey Sure (read only):** accounts, transaction ranges, categories, merchants, rules.
2. **Analyze the new export:**
   - Keep only rows after the last imported date.
   - Drop boundary duplicates and zero-amount income.
3. **Transform:**
   - Accounts: map payment methods to accounts (the private notes list them).
   - Categories: [categories.md](categories.md).
   - Merchant and transaction names: [conventions.md](conventions.md).
     - Reuse the existing English merchant when it is the same place.
     - Follow the auto-categorization rules (Korean conditions) when they match.
   - Monthly roll-ups: [conventions.md](conventions.md).
   - Transfers, card bills and loans: [transfers-and-loans.md](transfers-and-loans.md).
     - Split each loan installment by Sure's schedule (principal and interest) first.
4. **Apply:**
   - Transactions are `Transaction` + `Entry`. Positive amount = money out, negative = money in.
   - Transfers go through `Transfer::Creator`.
5. **Balances:**
   - After the sync, move opening anchors to the current balances.
   - Set cards from the remaining limit.
6. **Verify:**
   - Per-account counts and totals against the transformed data.
   - Balances against their targets.
   - Loan balances against the schedule.
   - Uncategorized count, names still containing Hangul, Sure log errors.
7. **Report and clean up:**
   - Report: what was created and changed, the verification numbers, the dump location for rollback.
   - Clean up: temporary files, password files, SSH sessions.

## Example Instruction

```text
Read docs/services/sure (README.md, public/ and private/notes.md) in the repository,
and import the new Banksalad export into Sure the same way as before.
Import only rows after the last imported date, and show me new merchants or new categories for approval before applying.
```
