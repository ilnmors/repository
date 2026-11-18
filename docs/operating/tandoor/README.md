# tandoor

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | 2.7.2 |
| Version (repository, 2026-11-17) | 2.7.3 |

Household recipe and meal database. An external agent plans meals through the API: see [meal-planning.md](meal-planning.md). Budget and household details are kept outside Git in `.agent-workspace/operating/tandoor-private.md`.

## Notes

- 2.7 dropped `HIDE_LOGIN_FORM`; the new login page reads `SOCIALACCOUNT_ONLY`.
- Promoted from `docs/archives` into `ansible/` on 2026-11-17. The homelab `app` host still runs 2.7.2.
- Database: PostgreSQL `tandoor_db` (owner `tandoor`), daily `postgresql-data-backup@tandoor.timer`. Recipe images: `~/data/containers/tandoor/mediafiles`.
- Secrets: `tandoor.secret_key` (generated on first deploy), `tandoor.oidc.{secret,hash}`, `postgresql.password.tandoor`.

## Login

`SOCIALACCOUNT_ONLY=1`. Break-glass sign-in: `/accounts/login/?form=1` (per upstream docs).

First OIDC login creates a user in the `user` group with access to the default space (`SOCIAL_DEFAULT_ACCESS=1`, `SOCIAL_DEFAULT_GROUP=user`).

## API

REST API at `/api/` (recipes, meal plans, shopping lists, foods). An external agent should use the token of a dedicated user in the household space, not an administrator token. 2.7.3 contains API permission fixes; keep at least that version before giving a token write access.
