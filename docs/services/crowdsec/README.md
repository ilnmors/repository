# crowdsec

| Item | Value |
| --- | --- |
| Host | LAPI on vmm; agents on vmm, infra, auth, app |
| Version (2026-11-17) | 1.4.6 (Debian package) |

## Notes

- Ban notifications (2026-11-17): the LAPI profiles send every IP or range remediation to `notifications/discord.yaml` (http plugin), batched per 30 s or 10 alerts, as "CrowdSec". About 50 local bans a day reach Discord; CAPI (community blocklist) decisions do not go through the profiles.
- Debian installs the notification plugins as `/usr/lib/crowdsec/plugins/<type>`, but crowdsec only loads `notification-<type>` and refuses to start the LAPI once a profile uses notifications. `plugin_dir` therefore points to `/usr/local/lib/crowdsec/plugins/`, which holds `notification-http` as a link to the packaged binary.
- Test a notification with `cscli notifications reinject <alert id>` (root). cscli starts its own plugin process for this, so a `plugin process exited` line afterwards is that process, not the LAPI plugin.
- On a normal stop 1.4.6 logs `level=fatal msg="while serving local API: http: Server closed"` to stderr. Alloy files it as info, so it does not raise `FatalLogged`.

## Notification secrets

Webhooks and bot credentials live under `notification` in secrets.yaml, by channel and then by service:

```yaml
notification:
  discord:
    default: <webhook>     # used when a service has no own entry
    crowdsec: <webhook>    # optional, per service (grafana, crowdsec, ...)
  telegram:
    default:
      token: null
      id: null
```

Templates look up `notification.<channel>.<service>` first and fall back to `notification.<channel>.default`.
