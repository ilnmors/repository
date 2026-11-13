# Transfers, Cards, Loans and Balances

## Transfers

- Money between own accounts is a Sure transfer, so both legs are paired.
  - Pairing rule: same amount, within one day, different accounts.
- A transfer whose other side is not in Sure stays a one-legged `funds_movement` (excluded from budgets).
- Cash withdrawals and deposits are transfers between the bank account and the Cash account.
- Sure names transfer legs after the accounts:
  - `Payment to/from <account>` when the destination is a liability (card, loan).
  - `Transfer to/from <account>` otherwise.
  - Rename the legs when an account is renamed.

## Cards

- One card account per issuer.
- A card bill is one transfer bank account → card account (`cc_payment`).
- If the bill also carries a card loan installment, split that off first (see Loans). Only the rest is the card bill.
- Check-card purchases are transactions of the bank account, not of a card account.
- Bills for a card that has no purchase data stay on the bank side only.
  - Name them `<Issuer> payment (card without purchase data)`, kind `cc_payment`, excluded from budgets.
- Set the card balance (amount used) from the card app: amount used = credit limit − remaining limit (lump sum and installments).
- Store the remaining limit in `available_credit`.

## Loans

- Put the loan terms on the Sure loan account, so Sure shows the equal-payment schedule and payoff projection:
  - `interest_rate`, `term_months`, `rate_type: fixed`
  - `initial_balance` = principal
  - `start_date`
- Due dates are `start_date` plus one month each, so pick a `start_date` on the real payment day of the month.
- Split every repayment by the matching installment in Sure's schedule:
  1. **Principal:** transfer bank account → loan (`loan_payment`), category Finance > Loan Repayment. The loan balance drops by the principal only. Sure counts `loan_payment` as spending, so a leg without a category shows as uncategorized.
  2. **Interest:** an expense on the bank account named `<loan> interest`, category Finance > Interest. It counts as spending and does not reduce the loan.
  3. **The rest of a combined bill** (for example a card bill): its own transfer.
- Sure does not split interest or adjust the balance by itself; the schedule is display only. Importers must do the split.
- Check the result: after the split installments, the loan balance must match the lender's remaining balance. Settle rounding in the latest installment.
- A loan draw is a transfer loan → bank account.
- Loans with no repayment history yet only get their balance set from the lender's figures.

## Setting Balances

- Deposit and card accounts are matched to the current balance by moving the opening anchor.
  - Do not add a one-day reconciliation: it makes the chart jump on that day, and the transaction flow no longer matches reality.
- Targets come from the user or the export's snapshot sheet.
- `set_current_balance` on a deposit account moves the opening anchor by (target − cached balance).
  - Calling it on a new account before the first sync uses a cached 0 and lands wrong.
  - Always wait for the sync first.
