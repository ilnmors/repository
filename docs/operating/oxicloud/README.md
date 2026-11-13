# oxicloud

| Item | Value |
| --- | --- |
| Host | app (8007 → 8086) |
| Version (2026-11-13) | 0.10.0 (`docker.io/diocrafts/oxicloud`) |

## Notes

- Domain `oxicloud.ilnmors.com`; storage `~/data/containers/oxicloud/storage` (container UID 1001 → subuid 101000); database `oxicloud_db` with a daily backup timer.
- The image listens on 127.0.0.1 by default, so `OXICLOUD_SERVER_HOST=0.0.0.0` is required (in the container template).
- OIDC: client `oxicloud`, `client_secret_post`, PKCE S256, scopes `openid profile email groups`, redirect `/api/auth/oidc/callback`, `OXICLOUD_OIDC_AUTO_PROVISION=true`, `OXICLOUD_OIDC_ADMIN_GROUPS=admins`.
- OIDC provisioning turns user names shorter than 3 characters into `user_<sub>`; after the first login rename `auth.users.username` to the LDAP id. Upstream PR #880.
- DAV (WebDAV, CalDAV, CardDAV) uses app passwords from Profile > App Passwords (DAVx5, Console DAV). They are stored only as argon2id hashes in `auth.app_passwords` and cannot be shown again; the Console DAV password is in the console's GNOME Online Accounts keyring.
- Nextcloud calendars and contacts were moved here on 2026-11-12.
- Collabora: WOPI discovery `http://host.containers.internal:9980/hosting/discovery`; Collabora's aliasgroup must include `https://oxicloud.ilnmors.com`.

## Login

`OXICLOUD_AUTH_METHODS=oidc`.
