# mail

| Item | Value |
| --- | --- |
| Host | infra (submission 587 → 2587, IMAPS 993 → 2993) |
| Version (2026-11-15) | Postfix 3.10.13 (built on Debian 13), Dovecot 2.4.5 |
| Names | `smtp.ilnmors.internal`, `imap.ilnmors.internal` |

## Notes

- Replaced maddy on 2026-11-14. The 25 mailbox messages of `il` and `morsalin` were moved into Dovecot with their dates and flags; the 2 messages of `test` stay in the maddy backup only, as that account has no mailbox group.
- Users come from LLDAP through the `mail` service account. Mailboxes exist for the `admins` and `users` groups; the `services` group can authenticate and send but has no mailbox.
- Postfix delivers to Dovecot over LMTP and authenticates through the Dovecot auth socket (shared `~/containers/mail/sockets`).
- There is no outbound relay: mail to external domains is rejected at submission. `postmaster@` is an alias of `il`.
- Postfix map files hold the LDAP bind password. They are mounted root-only at `maps-src` and copied as `root:postfix 0640` when the container starts, because proxymap reads them as the postfix user. The root CA is world-readable for the same reason.
- Postfix listens on IPv4 and IPv6 (`inet_protocols = all`); clients reach the forwarded port over IPv6.
- Authelia sends its notifications as `authelia` and runs its startup check against `postmaster@`, since service accounts have no mailbox.
- Every sending service uses its own `services` account and its own address (`<uid>@ilnmors.internal`), so a leaked password can only send as that service (`reject_authenticated_sender_login_mismatch`). Senders: `authelia`, `grafana` (its LDAP bind account), `vaultwarden` (SMTP only, no LDAP read rights). There is no shared no-reply account.
- Clients trust the postfix certificate through the internal root CA: Grafana reads it from `SSL_CERT_DIR`, Vaultwarden (OpenSSL) from `SSL_CERT_FILE`; the public CAs still come from `/etc/ssl/certs`.
