# prometheus

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | v3.16.0 |

## Notes

- `--log.level` is deprecated; set `runtime.log_level` in the configuration instead.
- Retention: 180 days, capped at 20GB (`--storage.tsdb.retention.time/size`), on `/data/infra` (decided 2026-11-14). The running homelab server keeps 30 days and 15GB until the rebuild.
