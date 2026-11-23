# ilnmors homelab

Infrastructure as code for a single-node homelab: one physical hypervisor, three virtual machines and a separate console that drives everything with Ansible. From blank disks to running services, every step except the operating system install on the hypervisor is declared here.

## Layout

| Path | Contents |
| --- | --- |
| `ansible/inventory/group_vars/repository/` | The whole system as data: `site`, `hardwares`, `nodes`, `networks`, `services`, `releases`. |
| `ansible/roles/` | Five roles split by concern: `secrets`, `nodes`, `packages`, `libvirt`, `containers`. |
| `ansible/playbooks/` | `site.yaml`, `pki.yaml` and one playbook per node under `nodes/`. |
| `docs/` | Bring-up guides, operating notes, archived stacks and the project history. |
| `tools/` | Helper scripts (secrets editing) and generated bootstrap files (`tools/build/`, not tracked). |

## Hosts

| Host | Role |
| --- | --- |
| console | External controller. Holds the repository and the encrypted secrets, runs Ansible, serves code-server locally. |
| vmm | Physical hypervisor (Debian, KVM/libvirt). Also the router and firewall (nftables, VLANs), DNS (BIND), DHCP (Kea), IDS (Suricata) with CrowdSec, WireGuard, NTP, and the Kopia backup server with rclone off-site copies. |
| infra | Shared platform: step-ca, PostgreSQL, MariaDB, LLDAP, RustFS (S3), Prometheus, Loki, Grafana, x509-exporter, Postfix and Dovecot. |
| auth | Public entry point: Caddy with the CrowdSec bouncer, and Authelia for single sign-on (OIDC and forward auth). |
| app | User applications behind their own Caddy, listed below. |

Applications on app: BookStack, Collabora, Forgejo, Homepage, Immich, Kaneo, Linkding, Mastodon, Open WebUI, Outline, OxiCloud, Quartermaster (local LLM and image models), Readur, SnappyMail, Sure, Tandoor, Vaultwarden.

Every container runs as a rootless Podman quadlet under a per-host service account.

## Design

- **The inventory is the source of truth.** A service is declared once in `services.yaml` (hosts, ports, domain, dependencies) and pinned once in `releases.yaml`. Database accounts, OIDC clients, S3 buckets and policies, Caddy routes, certificates and backup targets are derived from those declarations instead of being listed again per service.
- **Hardware and roles are separate.** `hardwares.yaml` describes the physical machine (NICs, disks by serial, passthrough devices); `nodes.yaml` assigns them to hosts by role. Replacing a disk or a NIC changes one file.
- **Names.** `site.domain.public` is the public zone and `site.domain.internal` the private one. A unit's `domain.public` is published through auth; its `domain.internal` is the private name, either `<service>.<host>` for applications or a fixed name for shared endpoints such as `ldap` or `postgresql`.
- **TLS everywhere except loopback.** An offline root CA signs an intermediate held by step-ca. Applications get ACME certificates over DNS-01 against BIND; shared endpoints get leaf certificates issued by the `pki.yaml` playbook and watched by x509-exporter. SSH uses host and user certificates from a separate SSH CA.
- **Secrets stay encrypted.** `secrets.yaml` is encrypted with SOPS and age; the age key is itself encrypted with a passphrase. Plays decrypt secrets into memory only.
- **Creation is automatic, destruction is manual.** Playbooks create, update and grow resources. They refuse to format a disk that holds another filesystem, and CA material is only generated through explicitly tagged runs.
- **Data volumes are btrfs.** infra and auth keep their data on raw images on the hypervisor SSD; app uses an HDD RAID1. Backups take a read-only snapshot first, so every file in a backup comes from the same moment.

## Getting started

To run this on your own hardware, follow [docs/getting-started.md](docs/getting-started.md): what to change in the inventory, how to create your own secrets and CAs, and the playbook order. The steps for this site:

1. Prepare the console: [docs/console.md](docs/console.md) (collections, secrets, CA hierarchy).
2. Bring up the hypervisor and the virtual machines: [docs/vmm.md](docs/vmm.md).
3. Apply each node: `ansible-playbook playbooks/nodes/<node>.yaml`, or everything with `playbooks/site.yaml`.

Day-to-day notes for each running stack are in [docs/services](docs/services/README.md). Stacks that were retired, with the reason for each, are in [docs/archives](docs/archives/README.md). How the project got to its current shape is in [docs/history.md](docs/history.md). Issues and pull requests sent upstream for these stacks are in [docs/external-contributions.md](docs/external-contributions.md).

## License

GPL-3.0-or-later (see [LICENSE](LICENSE)).
