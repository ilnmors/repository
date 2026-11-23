# Naming and Data Conventions

## Language

Everything in Sure is English: accounts, categories, merchants, transaction names, rule names and memo text. There are two exceptions:
- The `상호: ...` memo that keeps a romanized merchant's Korean trade name.
- Rule condition values, which stay Korean to match the export text.

## Accounts

- Format `<owner>) <institution> <kind>`, for example `<owner>) <Bank> account` or `<owner>) <Issuer> card`.
- One card account per issuer. Cards from one issuer are billed together, so they are not split.
- Check cards get no account. Their purchases are transactions of the linked bank account.
- Unused accounts are disabled, not deleted.
- Reward points are separate Other asset accounts.

## Merchants

Apply in order:

1. **Official English name when one exists:** chains, companies, agencies and payment processors. Examples: CU, GS25, 7-Eleven, Mega MGC Coffee, Starbucks, Coupang Eats, KG Inicis, Korail, KEPCO.
2. **English names written in Hangul go back to their spelling:** 클라우드플래닛 → Cloud Planet, 헤어스토리 → Hair Story.
3. **Otherwise, Revised Romanization of Korean:**
   - Romanize only the proper noun and translate the trade word: 약국 Pharmacy, 의원 Clinic, 식당 Restaurant, 내과 Internal Medicine.
   - Add `상호: <Korean name>` to the memo of that merchant's transactions.
   - Example: 해맑은약국 → `Haemalgeun Pharmacy`, memo `상호: 해맑은약국`.

Further rules:
- **Branches:** `<brand> <branch> branch`, with the branch written as the real place or building name: `CU <Station> branch`, `Mega MGC Coffee <University> branch`.
- **One merchant per place:** merge payment names that point to the same place (several Starbucks descriptors → `Starbucks`).
- **No ad-hoc transliteration:** when unsure, search. If no official English name exists, use rule 3.
- **Symbols in card descriptors** (the `*` in `ANTHROPIC* CLAUDE SUB`) are not masking; map the descriptor to the merchant (`Claude (Anthropic)`).

## Descriptive Names (not merchants)

| Source | English |
| --- | --- |
| 티머니_지하철 / 티머니_버스 | T-money (subway) / T-money (bus) |
| 자동결제 | Auto-payment |
| 관리비 / 가스비 | Maintenance fee / Gas bill |
| 결산이자, periods like 06.20~09.18 | Interest settlement / Interest 06.20-09.18 |
| 1 KRW `*****` transfer | Account verification (1 KRW) |

## Monthly Roll-ups

Small repeated spending is merged into one transaction per account, merchant, category and month.

- Always merged: public transit (Transportation > Public Transit) and printing or copying.
- Also merged: four or more transactions in a month at one account and merchant, with a median amount of 3,000 KRW or less.
- Name: `<merchant or Public Transit> YYYY-MM total (N tx)`.
- Date: the last transaction day of that month.
- Memo: `Monthly total of N transactions in YYYY-MM (<first> to <last>)`.

## Data Principles

- Do not try to recover what the export masks (`*****` counterparties).
- Skip zero-amount income.
- When two exports overlap on a boundary day, keep one copy. Identical rows inside one export are real repeats and are kept (consecutive transit taps).
