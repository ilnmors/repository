# oxicloud

| Item | Value |
| --- | --- |
| Host | app (8007 → 8086) |
| Version (2026-11-13) | 0.10.0 (`docker.io/diocrafts/oxicloud`) |

## Notes

- Domain `oxicloud.ilnmors.com`; storage `~/data/containers/oxicloud/storage` (container UID 1001 → subuid 101000); database `oxicloud_db` with a daily backup timer.
- The image listens on 127.0.0.1 by default, so `OXICLOUD_SERVER_HOST=0.0.0.0` is required (in the container template).
- OIDC: client `oxicloud`, `client_secret_post`, PKCE S256, scopes `openid profile email groups`, redirect `/api/auth/oidc/callback`, `OXICLOUD_OIDC_AUTO_PROVISION=true`, `OXICLOUD_OIDC_ADMIN_GROUPS=admins`.
- OIDC provisioning in 0.10.x turns user names shorter than 3 characters into `user_<sub>`; after the first login rename `auth.users.username` to the LDAP id (renamed accounts keep working for login, app passwords and CardDAV).
- Upstream fix: PR #880 (`fix(auth): accept two-character usernames in setup and OIDC JIT`, merge `8dfda52`, merged 2026-11-21). It lowers the minimum to 2 in first-admin setup and OIDC JIT provisioning, matching `validate_username` and the `users_username_shape_v2` check. It is not in a release yet (latest v0.10.1, 2026-11-18); once a release contains it, new 2-character LDAP ids such as `il` are provisioned as-is and the rename step is no longer needed.
- Still open upstream: the admin "create user" form keeps a client-side 3-character check (`minlength="3"`), although the backend accepts 2.
- DAV (WebDAV, CalDAV, CardDAV) uses app passwords from Profile > App Passwords (DAVx5, Console DAV). They are stored only as argon2id hashes in `auth.app_passwords` and cannot be shown again; the Console DAV password is in the console's GNOME Online Accounts keyring.
- Nextcloud calendars and contacts were moved here on 2026-11-12.
- Nextcloud and Group-Office user files were moved into il's drive on 2026-11-13 under `Nextcloud/<user>/` and `GroupOffice/`, without the Nextcloud sample files. Files were checked by reading them back and comparing SHA-256.
- The WebDAV `blob_hash` in `storage.files` is not SHA-256; large uploads are stored as ~1 MiB chunks listed in `storage.chunk_manifests`.
- Copying multi-GB files through a GNOME (gvfs) WebDAV mount fails: gvfs buffers the whole upload in memory. Use the web UI or a streamed client.
- Collabora now serves only OxiCloud (single aliasgroup).
- Collabora: WOPI discovery `http://host.containers.internal:9980/hosting/discovery`; Collabora's aliasgroup must include `https://oxicloud.ilnmors.com`.

## Login

`OXICLOUD_AUTH_METHODS=oidc`.
