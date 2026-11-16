# prometheus

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | v3.16.0 |

## Notes

- `--log.level` is deprecated; set `runtime.log_level` in the configuration instead.
- Only Prometheus itself is scraped; Alloy remote-writes everything else. No rule files: alert rules are evaluated by Grafana.
- Jobs (Alloy, 2026-11-16): `node` (host metrics, systemd units without `.service`), `smart-exporter` (smartctl_* on vmm), `postgresql`, `caddy`, `crowdsec`, `x509-exporter`, `prometheus`. Every series has `instance=<host>`.
- Retention: 180 days, capped at 20GB (`--storage.tsdb.retention.time/size`), on `/data/infra` (decided 2026-11-14). The running homelab server keeps 30 days and 15GB until the rebuild.
