# postgresql

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-23) | 18.7 with VectorChord 1.1.1 (`ilnmors.internal/infra/postgresql:18.7`) |

## Notes

- Build: configured via `releases.yaml` (`containers.postgresql.tag` and `build.vectorchord.tag`) using `templates/postgresql/build/Containerfile.j2`, which installs `postgresql-${PG_MAJOR}-pgvector` and downloads `postgresql-${PG_MAJOR}-vchord` from `tensorchord/VectorChord`.
- Query: `podman exec -i postgresql psql -U postgres -d <db>` on infra.
- Backups: `postgresql-cluster-backup.timer` and `postgresql-data-backup@<service>.timer` run daily. Dumps go to `~/data/containers/postgresql/backups/<service>/pg_<service>_YYYY-MM-DD.sql`; a second run on the same day overwrites the file, so copy a dump under another name before risky work. Manual run: `systemctl --user start postgresql-data-backup@<service>.service`.
- PostgreSQL 19 hold (checked 2026-11-23): `postgres:19.0` and `postgresql-19-pgvector` (`trixie-pgdg`) exist, but `tensorchord/VectorChord` (`1.1.1`) does not publish `postgresql-19-vchord` `.deb` packages yet (builds stop at PG 18). Because `postgresql.conf` preloads `vchord.so` and `immich_db` uses `vchord`, upgrading to 19 fails at image build time. Re-check once VectorChord ships PG 19 packages and Immich confirms PG 19 support.
- Major version upgrades: PG 18 stores data under `/var/lib/postgresql/18/docker` (`~/containers/postgresql/data/18`), while PG 19 uses `/var/lib/postgresql/19/docker`. A tag change alone will not migrate existing data; take a fresh separate copy of all SQL dumps (cluster + every database) first, then migrate via `pg_upgrade` or a full restore into an empty `data/` directory (with `.init` removed).
