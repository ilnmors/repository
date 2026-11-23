# Getting started on your own hardware

This repository describes one specific homelab. Everything that is specific to it lives in the inventory under `ansible/inventory/`, so adapting it to your own environment means changing those files, creating your own secrets and certificate authorities, and then running the same playbooks. This guide walks through that in order. The existing guides ([console.md](console.md), [vmm.md](vmm.md)) cover each step in more detail.

## What you need

- **A control machine** (the "console"): any Debian or Debian-based machine you keep with you. It holds the repository, the encrypted secrets and the CA keys, and runs Ansible.
- **One physical server** (the "vmm") that becomes both the hypervisor and the router: CPU virtualization (VT-x/AMD-V, IOMMU for passthrough), at least one NIC for the WAN and one for the LAN, an SSD for the system and VM images, and optionally HDDs for the application data RAID1.
- **A VLAN-capable switch** if you want the client, server and user networks separated as declared in `networks.yaml`.
- **A public domain on Cloudflare** for services reachable from the internet. The vmm keeps its records current through the Cloudflare API (`ddns`), and the auth VM serves HTTPS on ports 80/443 of your WAN address. A private domain for internal names (for example `home.internal`) is served by the vmm's own BIND.
- Fresh Debian installations: on the vmm by hand; the VMs are created from cloud images by the playbooks.

## 1. Fork and inspect

```bash
git clone https://github.com/ilnmors/repository.git
cd repository/ansible
```

The inventory is the single source of truth:

| File | What you change |
| --- | --- |
| `group_vars/repository/site.yaml` | Organization name, public and internal domains, LDAP base DN, timezone, CA file names. |
| `group_vars/repository/hardwares.yaml` | Your physical machine: CPU, NIC names, disks by serial, passthrough GPUs. |
| `group_vars/repository/networks.yaml` | VLAN IDs, subnets, gateways, DHCP pools and the fixed address of every host. |
| `group_vars/repository/nodes.yaml` | Accounts and UIDs per host, VM sizes (vCPU, memory, root and data disks), data paths and mount options. |
| `group_vars/repository/services.yaml` | Which services run where, their ports, domains and dependencies. |
| `group_vars/repository/releases.yaml` | Pinned versions of every package and container image. |
| `hosts.ini` | Host names Ansible connects to (`<host>.<internal domain>`). |

After editing, search for leftovers of the original site and replace them:

```bash
grep -rn "ilnmors" . ../docs | grep -v "^../docs/archives"
```

## 2. Adapt the inventory

Work through the files in this order, because later files refer to earlier ones.

1. **site.yaml**: set `site.domain.public`, `site.domain.internal`, `site.org`, `site.directory.base_dn` and `site.timezone`. The CA file names may stay as they are or follow your organization name.
2. **hardwares.yaml**: describe your server. Disks are matched by serial (`lsblk -o NAME,SERIAL`), NICs by the names the kernel gives them. Declare a passthrough device only if it exists and is meant for a VM.
3. **networks.yaml**: choose subnets and VLAN IDs, then give every host a fixed address under `segments.<segment>.hosts`. The DNS forwarder can stay on Cloudflare or point elsewhere.
4. **nodes.yaml**: keep the account names or rename them, and size each VM. A VM without a physical data disk gets a sparse raw image on the vmm SSD (`data.type: file`); `block` uses the disks listed in `hardwares.yaml`.
5. **services.yaml**: to leave a service out, set its `hosts` to `[]`. Everything derived from it (database account, OIDC client, Caddy route, backups) is then skipped as well. Keep the platform services (`caddy`, `step-ca`, `postgresql`, `ldap`, `authelia`) unless you replace them yourself.
6. **releases.yaml**: the pins work as they are. Update them when you want newer versions.

## 3. Create your own secrets and certificate authorities

Never reuse the encrypted files in this repository: they are bound to the original age key. Create new ones on the console (details in [console.md](console.md#managing-secretsyaml)):

1. Install the tools listed in console.md (`ansible-core`, `sops`, `step-cli`, `age`, `gnupg`) and run `ansible-galaxy install -r requirements.yaml`.
2. Generate an age key in a private directory under `$XDG_RUNTIME_DIR` and put its public recipient into `roles/secrets/files/.sops.yaml`.
3. Write a new `roles/secrets/files/secrets.yaml`. SOPS keeps the key names in plain text, so the existing encrypted file shows the expected structure. At minimum fill in `sudo.<host>.password` for every host and the external values you need (`ddns` Cloudflare token and zone, mail relay, API keys). Most service passwords and OIDC client secrets that are missing are generated and written back by the playbooks on first use.
4. Encrypt it with `sops --encrypt --in-place`, encrypt the age key with `gpg --symmetric --cipher-algo AES256` into `roles/secrets/files/age-key.gpg`, and store the same key with `ansible-vault encrypt_string --stdin-name secrets_age_key` into `roles/secrets/vars/main.yaml`. Remove the plaintext copies afterwards.
5. Create the certificate authorities: `ansible-playbook playbooks/pki.yaml --tags root,ssh`. This makes an offline root CA, an intermediate for step-ca and an SSH CA. Keep the root key off the servers.

Every playbook run asks for the Vault password; the GPG passphrase is asked when the age key is decrypted. Use a long passphrase: the encrypted files are meant to be safe in a public fork.

## 4. Bring up the console

```bash
ansible-playbook playbooks/nodes/console.yaml --syntax-check
ansible-playbook playbooks/nodes/console.yaml --tags site
```

This prepares the console account, local tools and, if declared, code-server behind a local Caddy.

## 5. Bring up the hypervisor

1. Install Debian on the server with the account declared for `vmm` in `nodes.yaml`.
2. Generate the bootstrap bundle on the console and copy it to the server over a trusted channel (it contains a password hash and SSH CA trust):

   ```bash
   ansible-playbook playbooks/nodes/console.yaml --tags vmm-init
   # writes tools/build/vmm/init/
   ```

3. On the server, from a local console session (networking and SSH change):

   ```bash
   sudo bash vmm-init.sh
   ```

4. Back on the console, the first run accepts the new host key; later runs use the SSH CA:

   ```bash
   ansible-playbook playbooks/nodes/vmm.yaml --tags init
   ansible-playbook playbooks/nodes/vmm.yaml
   ```

The vmm now routes and firewalls the VLANs, serves DNS and DHCP, runs WireGuard and the backup server, and has created the VMs from cloud images. Check the result with the commands in [vmm.md](vmm.md#validate-the-result).

## 6. Bring up the virtual machines

Apply them in dependency order. The first run of each uses `--tags init` for the same host-key reason:

```bash
ansible-playbook playbooks/nodes/infra.yaml --tags init   # step-ca, PostgreSQL, MariaDB, LDAP, S3, monitoring, mail
ansible-playbook playbooks/nodes/auth.yaml --tags init    # public Caddy, CrowdSec bouncer, Authelia
ansible-playbook playbooks/nodes/app.yaml --tags init     # applications
```

Afterwards run them without tags, or a single service with `--tags <service>` (for example `--tags immich`). `playbooks/site.yaml` applies everything.

## 7. Open it to the internet

- Make sure ports 80 and 443 on your WAN address reach the auth VM (the vmm firewall forwards them as declared) and that the `ddns` values point at your Cloudflare zone.
- Each service with `domain.public` is published as `<name>.<public domain>` through auth, behind Authelia.
- Sign in to LLDAP with the admin password from your secrets, create your users and groups, then log in to the applications through Authelia.

## 8. Day to day

- Change a service: edit `services.yaml` or `releases.yaml` and run `ansible-playbook playbooks/nodes/<host>.yaml --tags <service>`.
- Add a service: declare it in `services.yaml`, pin it in `releases.yaml`, add its task and templates under `roles/containers/`, and include it from `roles/containers/tasks/main.yaml`. Database accounts and OIDC clients are registered per service through `postgresql-register.yaml` and `authelia-register.yaml`.
- Edit secrets with `tools/scripts/edit_secret.sh`.
- Per-service notes are in [docs/services](services/README.md).

Playbooks create and grow resources but never format a disk that already holds another filesystem and never regenerate CA material unless you run the tagged PKI play. Destructive changes stay manual.
