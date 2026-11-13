# nextcloud

| Item | Value |
| --- | --- |
| Host | app |
| Status | Stopped (2026-11-13) |
| Version (2026-11-13) | 35.0.2 |

## Notes

- Stopped on 2026-11-13. User files (without the Nextcloud sample files) were copied to OxiCloud under `Nextcloud/<user>/`; calendars and contacts had moved on 2026-11-12. Data stays on app until it is removed.
- The 34 → 35 upgrade disabled dashboard, photos and music for compatibility; they were enabled again. Calendars and contacts moved to OxiCloud.

## Login

`hide_login_form=true` (user_oidc). The local admin signs in at `/login?direct=1`.
