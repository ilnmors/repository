# Operating Notes

Facts and decisions for running the homelab stacks, one directory per stack (`<stack>/README.md`). The configuration itself lives in `ansible/`. These notes describe the running servers as of 2026-11-15. The servers are still deployed from the archived homelab repository, whose stacks now match this repository's versions and layouts.

## Stacks

| Host | Stacks |
| --- | --- |
| infra | [postgresql](postgresql/README.md), [mariadb](mariadb/README.md), [lldap](lldap/README.md), [step-ca](step-ca/README.md), [rustfs](rustfs/README.md), [prometheus](prometheus/README.md), [loki](loki/README.md), [grafana](grafana/README.md), [x509-exporter](x509-exporter/README.md), [mail](mail/README.md), [caddy](caddy/README.md) |
| auth | [authelia](authelia/README.md), [caddy](caddy/README.md) |
| vmm | [crowdsec](crowdsec/README.md) (LAPI; agents on every host) |
| app | [oxicloud](oxicloud/README.md), [collabora](collabora/README.md), [sure](sure/README.md), [immich](immich/README.md), [outline](outline/README.md), [bookstack](bookstack/README.md), [kaneo](kaneo/README.md), [linkding](linkding/README.md), [vaultwarden](vaultwarden/README.md), [forgejo](forgejo/README.md), [mastodon](mastodon/README.md), [openwebui](openwebui/README.md), [quartermaster](quartermaster/README.md), [homepage](homepage/README.md), [readur](readur/README.md), [tandoor](tandoor/README.md), [snappymail](snappymail/README.md), [valkey](valkey/README.md), [caddy](caddy/README.md) |
| app, not in this repository | [homebox](homebox/README.md), [tandoor](tandoor/README.md) |
| retired 2026-11-14 | [gitea](gitea/README.md) (→ forgejo), [maddy](maddy/README.md) (→ mail), [llama](llama/README.md) and [stablediffusion](stablediffusion/README.md) (→ quartermaster) |
| stopped 2026-11-13 | [papra](papra/README.md), [nextcloud](nextcloud/README.md), [groupoffice](groupoffice/README.md) |

- The 2026-11-13 container upgrade is summarized in `.agent-workspace/upgrade-2026-11-13/index.html` (not tracked).
- `releases.yaml` was updated to the latest stable releases the same day.

## Hosts and Request Path

- Containers run as rootless Podman quadlets per user (`~/.config/containers/systemd/*.container`).
- External requests: auth Caddy → `<service>.app.ilnmors.internal` (app Caddy) → `host.containers.internal:<port>`.
- Inside a container `host.containers.internal` resolves to `169.254.1.2`; Podman adds it, so no host-gateway entry is needed.
- Public names `<service>.ilnmors.com` are reachable from inside containers through the auth host.

## Access from the Console

- Away from home, the WireGuard connection `ilnmors` must be up (`nmcli con up ilnmors`); it can drop when the Wi-Fi network changes.
- SSH uses `id_console` with its certificate. Trust the host CA after checking its fingerprint `SHA256:6tqfzyeeEgf6XkSgjrbMqQnzlvIrAF2XN640prQ4PYw` (`@cert-authority app,infra,auth,vmm <CA public key>`). Users: `app@app.ilnmors.internal`, `infra@infra.ilnmors.internal`, `auth@auth.ilnmors.internal`.
- The OxiCloud WebDAV share is registered in GNOME Online Accounts; mount that volume again from Files or GIO when it drops.

## Working Rules

- Never take passwords or keys in chat. Read them through a hidden-input terminal into a 0600 file under `$XDG_RUNTIME_DIR` and `shred -u` it afterwards.
- Do not print secret values or personal financial data; report counts and match results only.
- Back up before changes that are hard to undo. Database scripts run in one transaction, as a dry run (rolled back) first.
- Push only on an explicit request. The archived homelab repository is not pushed.

## Backups and Rollback

- Regular backups: the PostgreSQL and MariaDB timers (see [postgresql](postgresql/README.md), [mariadb](mariadb/README.md)).
- Backups taken before the 2026-11-13 work:

  | Work | Location |
  | --- | --- |
  | Container upgrade | `~/backups-20261113-upgrade/` on each host (quadlets, Caddy and PostgreSQL build files) plus database dumps from the same time |
  | Login pages | app `~/backups-20261113-oidc-login/`, infra `~/backups-20261113-oidc-login/immich-system-config.json` |
  | Sure AI variables | app `~/backups-20261113-sure-ai/` |
  | Sure Banksalad import | infra `~/data/containers/postgresql/backups/sure/pg_sure_2026-11-13_pre-banksalad.sql` |
  | Papra to Readur migration | app `~/backups-20261113-papra-to-readur/papra-full-20261113.tgz` (Papra documents, database and its backups); infra `~/data/containers/postgresql/backups/readur/pg_readur_2026-11-13_pre-{dates,rename}.sql` |

- Backups taken before the 2026-11-14 work:

  | Work | Location |
  | --- | --- |
  | Redis to Valkey | app `~/backups-20261114-valkey/` |
  | Gitea to Forgejo | app `~/backups-20261114-forgejo/` |
  | llama and stablediffusion to Quartermaster | app `~/backups-20261114-quartermaster/` |
  | maddy to Postfix and Dovecot | infra `~/backups-20261114-mail/` (maddy data); infra `~/data/containers/postgresql/backups/maddy/pg_maddy_2026-11-14_pre-dovecot.sql` |
  | step-ca, Prometheus and Loki moved to DATA | infra `~/backups-20261114-paths/ca-db.tgz` |

- Container rollback: restore the quadlet backup, then `systemctl --user daemon-reload` and restart the unit; the previous image is still on the host.
- Database rollback: stop the service and restore the dump.
