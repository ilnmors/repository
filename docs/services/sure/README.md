# sure

| Item | Value |
| --- | --- |
| Host | app (`sure-web`, `sure-worker`) |
| Version (2026-11-13) | 0.7.6 |

Household finance tracker. These documents hold the rules for importing bank and card exports (Banksalad) and keeping the data consistent. Account names, loan terms and other personal details are kept outside Git in [private/notes.md](private/notes.md).

| Document | Contents |
| --- | --- |
| [conventions.md](public/conventions.md) | Naming (accounts, merchants, transactions), monthly roll-ups, memos, data principles |
| [categories.md](public/categories.md) | Banksalad categories → Sure English categories |
| [transfers-and-loans.md](public/transfers-and-loans.md) | Transfers, card bills, check cards, loan principal and interest, balances |
| [import-workflow.md](public/import-workflow.md) | Procedure and agent instructions for an import |
| [sure-notes.md](public/sure-notes.md) | Sure internals confirmed in the source and on the server |

## Layout

- Each user's accounts carry an owner prefix: `<owner>) <institution> <kind>`.
- Categories are English with two levels (parent > child).
- Merchant and transaction names are English. Romanized merchants keep their Korean trade name in the transaction memo (`상호: ...`).
- Auto-categorization rules are named `Banksalad · <merchant>`.
  - The condition matches the Korean transaction name, because exports are Korean.
  - The actions set the category and the merchant.

## Login

`AUTH_LOCAL_LOGIN_ENABLED=false`, `AUTH_LOCAL_ADMIN_OVERRIDE_ENABLED=false`.

## Rollback

Take a database dump before every import (see [import-workflow.md](public/import-workflow.md)) and restore it to undo.
