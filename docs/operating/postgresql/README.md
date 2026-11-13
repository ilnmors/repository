# postgresql

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 18.7 with VectorChord 1.1.1 (`ilnmors.internal/infra/postgres:pg18.7-vectorchord1.1.1`) |

## Notes

- Build: change `ARG PG_VER` in `~/containers/postgresql/build/Containerfile` and rebuild.
- Query: `podman exec -i postgresql psql -U postgres -d <db>` on infra.
- Backups: `postgresql-cluster-backup.timer` and `postgresql-data-backup@<service>.timer` run daily. Dumps go to `~/data/containers/postgresql/backups/<service>/pg_<service>_YYYY-MM-DD.sql`; a second run on the same day overwrites the file, so copy a dump under another name before risky work. Manual run: `systemctl --user start postgresql-data-backup@<service>.service`.
