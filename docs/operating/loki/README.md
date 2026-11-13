# loki

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 3.7.9 |

## Notes

- 3.7.9 fixes inconsistent WAL record order from concurrent appends.
- Retention: 180 days (`limits_config.retention_period`, enforced by the compactor) on the local filesystem under `/data/infra`; S3 (RustFS) was considered and not used (decided 2026-11-14). The running homelab server keeps 30 days until the rebuild.
