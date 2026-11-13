# mariadb

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 13.0.2 |

## Notes

- Upgraded 12.3 → 13 on 2026-11-13. The container has no `MARIADB_AUTO_UPGRADE`, so `mariadb-upgrade` was run by hand.
- Used by BookStack and Group-Office; backups run from `mariadb-data-backup@<service>.timer`. Going back to 12 means restoring a dump.
