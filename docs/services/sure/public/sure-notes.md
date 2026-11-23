# Sure 0.7.6 Internals

Only facts confirmed in the source (we-promise/sure v0.7.6) or on the server.

## Transactions and Transfers

- `Entry.amount`: positive = money out (spending, card charges), negative = money in.
- `Transaction.kind`:

  | Kind | Budgets |
  | --- | --- |
  | `standard` | included |
  | `funds_movement` | excluded |
  | `cc_payment` | excluded |
  | `loan_payment` | counted as spending |
  | `one_time` | excluded |

- `Transfer::Creator.new(family:, source_account_id:, destination_account_id:, date:, amount:).create`
  - Creates both legs.
  - The kind follows the destination: card → `cc_payment`, loan → `loan_payment`.
  - The name is `Payment to ...` when the destination is a liability, `Transfer to ...` otherwise.
- Deleting a Transfer resets the surviving leg's kind to `standard`; set it again when needed.

## Accounts and Balances

- `Account.create_and_sync(attrs, skip_initial_sync:, opening_balance_date:)` creates the opening anchor on that date. Loans use `start_date` when given.
- `set_current_balance`:
  - Cash-type accounts without reconciliations: moves the opening anchor by (target − cached balance).
  - Other accounts: adds a reconciliation dated today.
  - The cached balance is 0 until the first sync, so call it only after the sync.
- To move the opening anchor directly: `Account::OpeningBalanceManager.new(account).set_opening_balance(balance:, date:)`.
- `account.disable!` sets the account to disabled and keeps its history.

## Loans

- With `interest_rate`, `term_months`, `rate_type: fixed`, `initial_balance` and `start_date`, Sure shows an equal-payment schedule and a payoff projection.
  - Due dates are `start_date` plus one month each.
- Payments are not split into interest automatically.

## Rules

- Condition keys include `transaction_name` (like) and `transaction_merchant` (=, merchant id).
- Action keys include `set_transaction_category` and `set_transaction_merchant`.
- Rules apply only to transactions after `effective_date`.

## AI

- The LLM provider (URI base, token, model, context window, timeouts) is set in Settings > Self-hosting.
  - `OPENAI_*`, `LLM_*` and `AI_RESPONSE_TIMEOUT` variables lock those fields, so they were removed from the containers.
- Current settings: Open WebUI (`https://openwebui.ilnmors.com/api`), request timeout 600 s, response timeout 2400 s, context 8192.
- Chat attachments (the `+` button) are disabled ("coming soon") in 0.7.6.
- PDF statements go through Import.
- The MCP server (`POST /mcp`, tokens in Settings > MCP) lets agents read and create data directly.

## Security

- Active Record encryption keys (`ACTIVE_RECORD_ENCRYPTION_*`) are not set.
  - So the AI token and Sure API keys (`api_keys.display_key`) are stored in plaintext.
  - Set the keys and save those values again if this matters.
