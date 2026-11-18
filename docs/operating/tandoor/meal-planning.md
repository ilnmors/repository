# Meal Planning Agent

Tandoor is the meal database; an agent outside Tandoor plans meals through the REST API. People decide only whether they like the plan, shop, cook and give feedback. Budget, household and taste details are kept outside Git in `.agent-workspace/operating/tandoor-private.md`.

## Roles

| Part | Holds or does |
| --- | --- |
| Tandoor | Recipes, foods, units, supermarket categories, meal plans, shopping lists, cook log |
| Agent | Weekly plan, shopping list, budget check, adjusting the next plan from feedback and prices |
| Sure | Actual grocery spending (`Food > Groceries`), read-only for the agent |
| People | Approve or change the draft plan, shop, cook, rate meals |

Tandoor's own automations only normalize food names and recipe imports. Planning is not a Tandoor feature; it is the external agent.

## Data in Tandoor

- **Space:** one household space. The agent works only in that space.
- **Foods:** one canonical English name per ingredient, with the Korean or Arabic name as an alias or description where it helps shopping. Use Tandoor automations (food alias) to merge duplicates instead of creating new foods.
- **Supermarket categories:** follow the store layout so the shopping list groups by aisle.
- **Recipes:** keywords for cuisine (`korean`, `iraqi`, `mixed`), effort (`quick`, `batch`, `one-pot`) and course. Servings are set so scaling works.
- **Prices:** a per-food cost property (property type such as `Price per 100 g`) holding the latest paid unit price. Confirm on the server how 2.7.3 stores food properties before relying on them.
- **Meal types:** breakfast, lunch, dinner, snack.
- **Feedback:** recipe rating and cook-log comments after a meal ("liked", "leftovers", "too much work").

## Weekly Cycle

1. **Collect (agent):** last week's cook log and ratings, leftovers noted by people, this month's grocery spending from Sure, remaining budget.
2. **Draft (agent):** next week's meal plan as a draft in a separate note or plan list, not yet in the shared meal plan. Balance cuisines, reuse ingredients across meals, prefer low-effort and batch recipes, and stay inside the weekly budget share.
3. **Review (people):** approve, swap or drop meals.
4. **Apply (agent):** create the approved meal plan entries and add only the missing ingredients to the shopping list (pantry items marked as on hand are skipped).
5. **Shop (people):** check items off; note real prices for new or changed items.
6. **Update (agent):** write the paid prices back to the foods, and compare the week's grocery spending in Sure with the plan.

## Agent Access

- Use a dedicated Tandoor user in the household space and its API token. Never an administrator token.
- Start read-only plus shopping-list write. Give meal-plan write only after a few reviewed weeks.
- Run on Tandoor 2.7.3 or later (API permission fixes) before any token gets write access.
- Sure access is read-only (transactions in `Food` categories), never imports or edits.
- Keep the token outside Git (secrets.yaml or `.agent-workspace`), and revoke it when the agent setup changes.

## Data Quality

The plan is only as good as the data:

- Food names must stay unique; review new foods the agent proposes before creating them.
- Prices come from real receipts, not estimates. Unknown prices are flagged, not guessed.
- Pantry and fridge state comes from people; the agent asks instead of assuming.

## Phases

1. Upgrade the homelab Tandoor to 2.7.3; create the household space layout (supermarket categories, meal types, keywords).
2. Enter the regularly cooked recipes and their foods. Agent proposes, people confirm.
3. Agent read-only: weekly plan draft and budget check in chat, no writes.
4. Shopping-list write.
5. Meal-plan write after approval in chat.
6. Price feedback loop from receipts and Sure.

## Example Instruction

```text
Read docs/operating/tandoor and .agent-workspace/operating/tandoor-private.md in the repository.
Draft next week's meal plan from Tandoor and this month's grocery spending in Sure.
Show me the draft and the shopping list before writing anything to Tandoor.
```
