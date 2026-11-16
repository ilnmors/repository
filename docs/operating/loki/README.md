# loki

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 3.7.9 |

## Notes

- 3.7.9 fixes inconsistent WAL record order from concurrent appends.
- No ruler: alert rules are evaluated by Grafana. `discover_log_levels` is off because Alloy sets `level`.
- Labels (Alloy, 2026-11-16): `instance` (host), `job` (systemd unit without `.service`, the container's quadlet unit, `kernel`, `systemd`, `systemd-user`, or the syslog identifier), `level` (debug, info, warn, error, fatal) and `stream` for second log files (`job="caddy", stream="access"`, `job="suricata", stream="eve"`). Suricata keeps `event_type`, Caddy keeps `host`, podman health events keep `health_status`. Status, method, URI, client IP, duration, SSH user and Suricata severity are structured metadata (`| status=~"5.."`).
- Levels: host services use the journald priority. Containers start at info (journald files all stderr as error) and take the level from the message: `level=`/`"level":` (pino numbers too) or a level word among the first tokens. Panics, segfaults and OOM kills are fatal on any stream. Lines a program logs as error or fatal on a normal shutdown (`http: Server closed`, crowdsec 1.4 LAPI) are set back to info.
- Retention: 180 days (`limits_config.retention_period`, enforced by the compactor) on the local filesystem under `/data/infra`; S3 (RustFS) was considered and not used (decided 2026-11-14). The running homelab server keeps 30 days until the rebuild.
