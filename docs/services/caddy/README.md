# caddy

| Item | Value |
| --- | --- |
| Host | infra, auth, app |
| Version (2026-11-13) | 2.11.9 with rfc2136, built locally on each host |

## Notes

- Request path: auth Caddy (CrowdSec) → `<service>.app.ilnmors.internal` (app Caddy) → `host.containers.internal:<port>`.
- Build: change the version in `~/containers/caddy/build/Containerfile` and run `podman build -t ilnmors.internal/<host>/caddy:<version>`.
- Since 2.11.6: request headers are limited to 16 KiB, idle reads and writes time out after 1 minute, header names containing `.` are dropped, and a wildcard site's `client_auth` no longer covers more specific sites.
