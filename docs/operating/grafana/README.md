# grafana

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 13.3.1 |

## Notes

- `grafana.ilnmors.internal` with LDAP login (not OIDC). The startup errors about missing provisioning `plugins`/`alerting` directories are harmless.
- btrfs alerts (repository, 2026-11-14): Prometheus `btrfs` group (`<host>_btrfs_metrics_missing`, `app_btrfs_raid_degraded`, `BtrfsDeviceErrors`) and Loki `BtrfsKernelError` on kernel logs (`job="kernel"`). They show in Grafana Alerting as data-source rules; there is no Alertmanager. Alloy enables the btrfs collector. Device error counters need an ioctl that the unprivileged `alloy` user may not get, so the kernel-log rule is the backstop.
