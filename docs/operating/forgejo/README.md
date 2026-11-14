# forgejo

| Item | Value |
| --- | --- |
| Host | app (3001) |
| Version (2026-11-15) | 17.0.1 |

## Notes

- Replaced Gitea on 2026-11-14. Only the git data was moved: the repositories were adopted, issues and pull requests were not used.
- The Authelia login source lives in the database; the playbook adds it when missing and updates it otherwise.
- `ENABLE_AUTO_REGISTRATION=true` with `ACCOUNT_LINKING=auto`: the first Authelia login creates the account or links it to an existing one with the same name.

## Login

`ENABLE_INTERNAL_SIGNIN=false`. The first visit shows the button; a remember-me cookie restores the session with `prompt=none`.
