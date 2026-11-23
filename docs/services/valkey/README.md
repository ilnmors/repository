# valkey

| Item | Value |
| --- | --- |
| Host | app (one sidecar per service) |
| Repository | `docker.io/valkey/valkey` 9.1.3, `ansible/roles/containers/tasks/valkey.yaml` |
| Running now (2026-11-13) | `docker.io/library/redis` 8.10.3, deployed from the archived homelab repository |

## Notes

- The repository defines these sidecars as Valkey (`units.valkey` in `services.yaml`). The app host still runs the homelab Redis units (`redis_<service>.service`, data in `~/containers/redis/<service>/`); they are replaced when app is deployed from this repository.
- Running sidecars: Mastodon, Sure, Outline and Immich.
- The Nextcloud sidecar (`redis_nextcloud`) was stopped with Nextcloud on 2026-11-13.
- Naming rule: use Valkey names (variables, units, paths, comments) wherever the client accepts them; keep Redis names only where the application reads nothing else.
- Checked against the pinned sources on 2026-11-14, every active client only accepts Redis names, so these stay as they are:

| Service | Variables read | URL schemes accepted |
| --- | --- | --- |
| Immich v3.4.1 | `REDIS_HOSTNAME`, `REDIS_PORT`, `REDIS_DBINDEX`, `REDIS_URL` (`server/src/repositories/config.repository.ts`) | host/port, or `ioredis://` (ioredis: `redis://`, `rediss://`) |
| Mastodon v4.7.5 | `REDIS_*`, `SIDEKIQ_REDIS_*`, `CACHE_REDIS_*` (`lib/mastodon/redis_configuration.rb`, `streaming/redis.js`) | redis-client 0.30.1 and ioredis: `redis://`, `rediss://`, `unix://` |
| Outline 1.12.0 | `REDIS_URL`, `REDIS_COLLABORATION_URL` (`server/env.ts`) | ioredis: `redis://`, `rediss://`, `ioredis://` |
| Sure 0.7.6 | `REDIS_URL`, `REDIS_SENTINEL_HOSTS` (`config/initializers/sidekiq.rb`, `config/cable.yml`) | redis-client 0.25.0: `redis://`, `rediss://`, `unix://` |
