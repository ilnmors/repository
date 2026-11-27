# lldap

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | v0.6.3 |

## Notes

- Source of users and groups (`admins`, `users`). No change on 2026-11-13.
- Web UI theme: `ansible/roles/containers/templates/ldap/style/style.css` is mounted read-only over the image's `/app/app/static/style.css`. `releases.yaml` keeps the SHA256 of the upstream file it replaces, and the deploy stops when the image's copy differs (`ansible/roles/containers/tasks/check-patches.yaml`), so a new tag forces the theme to be checked.
