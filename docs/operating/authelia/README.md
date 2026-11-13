# authelia

| Item | Value |
| --- | --- |
| Host | auth |
| Version (2026-11-13) | 4.39.28 |

## Notes

- OIDC provider for every public app (`authelia.ilnmors.com`); clients are under `identity_providers.oidc.clients`.
- Login page policy: each app shows only the Authelia button and goes to Authelia only when it is pressed (no auto redirect). The per-app settings are in each stack's Login section.
- Apps without OIDC: Vaultwarden (no OIDC yet), Grafana (LDAP, internal only), SnappyMail and Group-Office (IMAP authentication).
