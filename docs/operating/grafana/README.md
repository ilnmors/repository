# grafana

| Item | Value |
| --- | --- |
| Host | infra |
| Version (2026-11-13) | 13.3.1 |

## Notes

- `grafana.ilnmors.internal` with LDAP login (not OIDC). The startup error about the missing provisioning `plugins` directory is harmless.

## Alerting (2026-11-16)

- Grafana evaluates every alert rule; Prometheus has no rule files, Loki runs no ruler and there is no Alertmanager.
- Rules live in `templates/grafana/etc/rules/{prometheus,loki}.yaml.j2` in Prometheus rule format and are converted by `provisioning/alerting/rules.yaml.j2` (folder `Alerts`): query A runs the expression as an instant query, condition B fires for every series it returns. No data is OK; a query error raises a `DatasourceError` alert, which also covers Prometheus or Loki being down.
- Datasource UIDs are fixed in `datasources.yaml` (`PBFA97CFB590B2093`, `P8E80F9AEF21F6940`) because the rules reference them.
- Contact point `homelab` (Discord webhook + mail to `il@`) and the notification policy live in the Grafana database, not in the repository. The Discord webhook is `notification.discord.grafana` in secrets.yaml if set, otherwise `notification.discord.default`; Grafana sends as "Grafana" (`use_discord_username: false`). Mail goes through postfix as `grafana@`, using the LDAP bind password (`[smtp]` in `grafana.ini`).
- Device error counters need an ioctl that the unprivileged `alloy` user may not get, so `BtrfsKernelError` on kernel logs is the backstop for `BtrfsDeviceErrors`.
- `MemoryPressure` uses PSI (full stall), not usage: vmm keeps guest RAM allocated and always looks about 97% used. Suricata alerts are only raised for internal sources (`SuricataInternalSource`); inbound scans are constant noise.

## Dashboards

- `Metrics` and `Loki` live in the Grafana database (no dashboard provisioning). Their source is `.agent-workspace/grafana-dashboards/build.py`; `--labels homelab` builds the variant for the old Alloy labels.
