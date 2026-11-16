# vaultwarden

| Item | Value |
| --- | --- |
| Host | app |
| Version (2026-11-13) | 1.37.5 |

## Notes

- 1.37.4 fixed seven security advisories; rotate the organization API key if any organization admin is not fully trusted. `IP_HEADER` handling changed.

- Mail (2026-11-16): through postfix as the `vaultwarden` LDAP account (`services` group, password `ldap.password.services.vaultwarden`). OpenSSL trusts the internal CA through `SSL_CERT_FILE`; without it STARTTLS fails with `unable to get local issuer certificate`. Users have `@ilnmors.internal` addresses, so internal delivery is enough.

## Login

No OIDC (SSO would still leave the email and master password on Bitwarden clients).
