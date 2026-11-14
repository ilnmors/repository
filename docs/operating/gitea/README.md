# gitea

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | 28.3.0 |

## Notes

- Retired on 2026-11-14, replaced by [forgejo](../forgejo/README.md).
- 1.27 was followed by 28. Since 28, Git network operations (mirrors, migrations) go through an internal proxy and Actions has `RUN_RETENTION_DAYS`. The archived homelab repository's remote is this Gitea.

## Login

`GITEA__service__ENABLE_PASSWORD_SIGNIN_FORM=false`. Passkeys stay enabled: with no password form, no passkey and a single OAuth source, Gitea redirects straight to the provider.
