# History

How the homelab reached its current shape, in five generations. Each generation kept what worked in the previous one and replaced what did not.

## Summary

| Generation | Period | Form | In one line |
| --- | --- | --- | --- |
| 0 | 2025-04 – 2025-06 | Design documents | A Proxmox, OPNsense and FreeIPA plan modelled on an enterprise network. |
| 1 | 2025-07 – 2025-12 | Markdown runbooks, built by hand | Debian with libvirt, OPNsense and five VMs, rootless Podman quadlets. |
| 2 | 2026-01 – 2026-10 | Ansible monorepo, one role per node | A single-node IaaS where everything but the hypervisor install is code. |
| 3 | 2026-09 – 2026-10 | Ansible rewrite, roles by concern | Data-driven inventory; the firewall VM folded into the hypervisor. |
| 4 | 2026-11 – | This repository | Backup VM folded into the hypervisor, console as an external controller, every stack ported. |

Four threads run through all of them:

1. **Documents to code.** Early generations were their documentation. From generation 2 the code became the source, and documents shrank to decisions and operating notes.
2. **Appliances to plain Linux.** Proxmox became Debian with libvirt, OPNsense became nftables, FreeIPA became step-ca, LLDAP and Authelia, Open vSwitch became systemd-networkd.
3. **Fewer machines, merged roles.** More than ten planned VMs and containers became six, then five, four and finally three VMs.
4. **Repetition to data.** Copy-pasted per-service tasks gave way to `services`, `releases` and `nodes` declarations from which everything else is computed.

## Generation 0: design (2025-04 – 2025-06)

A NAS had reached its limits and hid too much behind its own abstractions, so the plan was to build a server that could be understood and controlled end to end, modelled on an enterprise network with segmentation, redundancy and tested restores.

- Three options were weighed: separate servers, a single OS running Docker, or a hypervisor with virtual machines. The hypervisor won; a single Docker host was rejected as too easy to copy-paste into and poor for learning internal network security.
- A low-power N150 mini PC was chosen for 24/7 operation.
- The design: Proxmox VE, OPNsense as the LAN router, VLANs, FreeIPA for LDAP, Kerberos, CA and DNS, AdGuard, Nginx with oauth2-proxy and Keycloak, Prometheus and Loki, Kopia backups to the NAS and an encrypted cloud copy, btrfs RAID10.
- Only the start was built: the Proxmox install, a temporary Debian VM and a Cloudflare DDNS script.

What survived into every later generation: a fixed UID/GID matrix for service accounts, no root SSH and default-deny firewalls, management only from a console, split-horizon DNS, no DMZ, ISO 8601 dates and change logs in documents, and the DDNS script.

## Generation 1: built by hand (2025-07 – 2025-12)

- Proxmox was replaced by Debian 13 with KVM/libvirt, KSM and Open vSwitch.
- VMs: OPNsense (Suricata IPS, CrowdSec, Kea, ACME, WireGuard), net (DDNS, BIND, AdGuard Home), auth (step-ca, Caddy, LLDAP, Authelia after a try with Authentik), dev (PostgreSQL, code-server) and app (SATA controller passthrough, btrfs RAID10).
- Patterns that are still in use: locally administered MAC addresses, the client and server subnets, rootless Podman with quadlets and lingering users, redirects from privileged to unprivileged ports, step-ca ACME with DNS-01 against BIND, Caddy re-encrypting to per-host Caddy instances with `X-Forwarded-Host`, SOPS with age and GPG, and split PostgreSQL schema and data dumps.
- Every step was typed by hand from the runbooks, VM boot order was held together by user units, and the application layer stopped at storage. The runbooks closed with the next goal: Ansible, for idempotence.

## Generation 2: Ansible IaaS (2026-01 – 2026-10)

The whole system was rebuilt with Ansible and running before it went into git in March 2026. Recovery was measured at about 1.5 hours for the hypervisor and VMs, and about 2.5 hours including hardware, with a 24-hour recovery point.

Recorded decisions:

- Debian and libvirt with rootless Podman; no Kubernetes for a single node; Ansible only.
- OPNsense replaced by nftables, with client, server, user and VPN zones, IPv6 ULA with NAT66 and global addresses for the user network.
- A ten-year offline root CA, a five-year intermediate in step-ca, an SSH CA; ACME for applications and long-lived manual leaf certificates for infrastructure, watched for expiry. Rotation replaces the intermediate rather than revoking.
- BIND as the authoritative server with Blocky as resolver.
- Suricata in IDS mode with CrowdSec as the IPS (nftables bouncer and Caddy at layer 7).
- SOPS and age instead of Vault or Infisical, with the age key protected twice.
- Git in three places, data through Kopia to the NAS and the cloud (3-2-1). A silently failing backup led to a weekly restore check.
- The hypervisor only virtualizes; privileged services run natively, everything else in containers.
- Creation is automated; deletion, formatting and CA work are manual.
- TLS on every hop except loopback; no mTLS.

VMs were fw (firewall, IDS, DNS, DHCP, NTP, DDNS, WireGuard), infra (CA, databases, LDAP, mail, object storage, monitoring), auth (Caddy and Authelia), app (up to 23 applications) and later bk (Kopia server and off-site copies).

The code was organized by node: roles `common`, `vmm`, `fw`, `infra`, `auth`, `app`, `bk`, `console`, with templates in a separate `config/` tree. It used `.init` markers, validation commands before reloads, offline archives of every container image, and automatic restores from database dumps and Kopia snapshots when a data directory was empty.

The repository went through four phases: numbered releases per service, then Conventional Commits with fine-grained changes, then a baseline in June that moved most documents into archives and reflected new hardware (a 12-thread CPU, two RJ45 and two SFP+ ports, disks owned by the hypervisor as btrfs instead of SATA passthrough), and finally large dated commits adding MariaDB, RustFS and local AI. Sixteen applications were tried and archived over its lifetime, each with a recorded reason.

Its weak points were the ones that shaped the next generations: adding a service touched about ten files, there was no alert delivery, and the running system drifted ahead of the last commit.

## Generation 3: roles by concern (2026-09 – 2026-10)

- Five roles by concern: `secrets`, `nodes`, `packages`, `libvirt`, `containers`.
- An inventory of six files: `site`, `nodes`, `hardwares`, `networks`, `services`, `releases`. Services became `services.<packages|containers>.<service>.units.<unit>` with hosts, domain, ports and dependencies; versions moved to `releases`.
- Package lists, leaf certificates, VM definitions and libvirt networks were computed from the inventory.
- The fw VM was removed: the hypervisor became router and firewall on VLAN subinterfaces. Blocky was removed in favour of BIND alone.
- The PKI was automated with step-cli from the console, kept behind explicit tags. Database accounts were created idempotently. Image handling moved into one shared deploy task, and failed handlers were surfaced by the playbooks.
- The port reached the platform containers but not the authentication and application layers.

## Generation 4: this repository (2026-11 –)

- The bk VM was removed: the Kopia server and rclone moved to the hypervisor, with the backup disk mounted there.
- The console became an external controller with its own account; code-server runs on it.
- Service accounts were renumbered per host, and hardware entries gained a role (root, swap, data, backup) that nodes select by.
- All roles were ported, including every authentication and application stack. Shared pieces became includes: PostgreSQL and MariaDB accounts, Authelia OIDC clients, RustFS buckets and policies, Valkey sidecars, Podman secrets and image deployment.
- Stacks were consolidated while porting:
  - Redis became Valkey, used under the Redis name only where an application accepts nothing else.
  - Gitea became Forgejo, with the Authelia login source registered by the playbook.
  - maddy became Postfix with Dovecot, both reading users from LLDAP.
  - Separate llama.cpp and stable-diffusion.cpp servers became Quartermaster, which routes and keeps the local models loaded. Its image is rebuilt on a newer Ubuntu with Mesa and a newer sd-server, because the bundled one rendered noise on the integrated GPU.
  - Nextcloud, Group-Office and Papra were retired in favour of OxiCloud, Collabora and Readur.
- infra and auth gained btrfs data disks on raw images on the hypervisor SSD; backups now snapshot the data volume first, and btrfs errors and degraded RAID raise alerts.
- Metrics and logs are kept for 180 days.

The previous repository is kept as an archive. Its last running stacks were brought in line with this repository's versions and layouts before the move, so that the rebuild only has to restore data.
