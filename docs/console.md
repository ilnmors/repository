# Console

Console is the external control node for executing Ansible and managing infrastructure. Hardware drivers, desktop themes and Android applications belong to the separate Surface bundle, not this playbook.

## Composition and Scope

1. Initial environment: an existing Debian account, repository checkout, Ansible, SOPS, step-cli and access to encrypted secrets.
2. Operational environment: the nodes, packages and containers roles in [console.yaml](../ansible/playbooks/nodes/console.yaml).
3. Console services: code-server on loopback HTTP, Caddy with a fixed intermediate-signed certificate, localhost name resolution and port translation. Kopia is declared separately and is applied only when its role is run.

## Prerequisites

- Match the account and group in [nodes.yaml](../ansible/inventory/group_vars/repository/nodes.yaml): `console`, UID `3000`, `svadmins`, GID `2000`. Change an existing account only from a separate session.
- Use the repository path declared in that file and keep `/run/user/3000` available through the logged-in user session.
- Have sudo access and network access to the declared package and image sources.
- Preserve the existing encrypted secrets, age key and CA when reusing an installation. Do not generate replacements merely to bootstrap Ansible.

## Initializing an Ansible environment

### Installing essential packages

```bash
sudo apt update
sudo apt install --no-install-recommends \
    git python3 python3-yaml gnupg age curl jq openssl \
    ansible-core ansible-lint
export REPOSITORY_DIR="$HOME/workspace/repository"
```

Install SOPS and step-cli using the versions in [releases.yaml](../ansible/inventory/group_vars/repository/releases.yaml). Select the architecture of Console, not the architecture of VMM.

```bash
cd "$REPOSITORY_DIR"
SOPS_VER=$(python3 -c 'import yaml; print(yaml.safe_load(open("ansible/inventory/group_vars/repository/releases.yaml"))["releases"]["packages"]["sops"]["version"])')
STEP_VER=$(python3 -c 'import yaml; print(yaml.safe_load(open("ansible/inventory/group_vars/repository/releases.yaml"))["releases"]["packages"]["step"]["version"])')
PACKAGE_ARCH=$(dpkg --print-architecture)
curl --fail --location -o /tmp/sops.deb \
    "https://github.com/getsops/sops/releases/download/v${SOPS_VER}/sops_${SOPS_VER}_${PACKAGE_ARCH}.deb"
curl --fail --location -o /tmp/step.deb \
    "https://github.com/smallstep/cli/releases/download/v${STEP_VER}/step-cli_${STEP_VER}-1_${PACKAGE_ARCH}.deb"
sudo apt install /tmp/sops.deb /tmp/step.deb
rm /tmp/sops.deb /tmp/step.deb
cd "$REPOSITORY_DIR/ansible"
ansible-galaxy install -r requirements.yaml
```

### Managing secrets.yaml

The operational source is `ansible/roles/secrets/files/secrets.yaml`. It uses the repository schema; the encrypted age key is `age-key.gpg`, and the same age key is stored as `secrets_age_key` in Ansible Vault. The GPG passphrase and Vault password are separate inputs.

```bash
cd "$REPOSITORY_DIR/tools/scripts"
./edit_secret.sh
```

For a completely new repository only, create an age key in a private directory under `$XDG_RUNTIME_DIR`, configure its recipient in `.sops.yaml`, encrypt `secrets.yaml` with SOPS, encrypt the age key with `gpg --symmetric --cipher-algo AES256`, and store that same key with `ansible-vault encrypt_string --stdin-name secrets_age_key`. Remove plaintext copies after verification. Existing installations retain these files and recipients.

At minimum, supply `sudo.console.password` and the credentials required by the selected services. Restored application data requires its existing encryption keys, API/OIDC values and database/LDAP credentials.

## Configuring an operational environment

### Create PKI

Run these only when intentionally issuing or rotating the selected CA. The tags can replace certificates and keys; they are not a routine prerequisite for every Console run.

```bash
cd "$REPOSITORY_DIR/ansible"
# Entirely new PKI only
ansible-playbook playbooks/pki.yaml --tags root,ssh
# Keep an existing root but replace subordinate certificates
ansible-playbook playbooks/pki.yaml --tags intermediate
# Replace only leaf certificates
ansible-playbook playbooks/pki.yaml --tags leaf
```

The current migration preserves the root CA and uses newly issued intermediate, leaf and SSH CAs for the future deployment. The operational SSH key under `workspace/homelab-ssh` still uses the old deployment's CA; keep it until that deployment is replaced. Its certificate was renewed through 2027-11-11.

### Execute a Console playbook

```bash
cd "$REPOSITORY_DIR/ansible"
ansible-playbook playbooks/nodes/console.yaml --syntax-check
ansible-playbook playbooks/nodes/console.yaml --tags site
```

Run as the Console user. The playbook loads encrypted secrets, reads the declared sudo password, and configures the account's operational services. Node templates replace their managed configuration files; this is not a snapshot of every manual desktop setting.

### Local code-server

- [services.yaml](../ansible/inventory/group_vars/repository/services.yaml) declares `code`, its web/PKI dependency and HTTP backend.
- The nodes role maps `code.ilnmors.internal` to `127.0.0.1` and translates localhost TCP `80 → 2080`, `443 → 2443` using a dedicated nftables table.
- The packages role runs code-server at `127.0.0.1:8081` and installs missing Ansible, YAML, Python and Git Graph extensions. Core Git support is built in.
- The existing containers/Caddy role selects hosted services with `dependency.web.status: true`. Console uses fixed leaf/full-chain files; servers retain ACME. PKI services use the existing `dependency.pki.cert: true` convention.
- Caddy uses host networking and binds loopback only. It does not request ACME certificates or depend on step-ca on Console. Linger keeps user services available after logout.

```bash
getent hosts code.ilnmors.internal
curl -I http://code.ilnmors.internal
curl -I https://code.ilnmors.internal
systemctl --user status code-server caddy
sudo nft list table inet console
```

Open `https://code.ilnmors.internal`. The backend has no separate authentication and is intentionally restricted to localhost. Do not expose it externally without adding authentication.

### Kopia

Console is declared as both a backup client and the existing full-management identity `console@console.ilnmors.internal`. The server role grants `FULL` access to snapshot, policy, user, ACL and content operations; the existing encrypted Console password is retained.

Console snapshots `nodes.console.paths.workspace`; other clients retain their data paths. When the data path sits on a btrfs data volume (infra, auth, app), the client first takes a read-only snapshot of the volume (`/data/.kopia-snapshot`), backs up the data path inside it with `--override-source=<data path>` so the snapshot history continues under the same source, and deletes the snapshot afterwards. All files in one backup then come from the same moment (RustFS objects, database dumps, metrics). All clients use the existing daily `00:00` timer, up to five minutes of randomized delay and `Persistent=true`. Failed jobs retry after five minutes. The Console declaration was added without installing or running Kopia on this Surface.

Apply the VMM Kopia server configuration before enabling new client access. When intentionally deploying the client:

```bash
cd "$REPOSITORY_DIR/ansible"
ansible-playbook playbooks/nodes/console.yaml --tags kopia
sudo systemctl list-timers kopia-client.timer
sudo journalctl -u kopia-client.service
```

## Next step

Prepare the physical hypervisor using [vmm.md](vmm.md). Keep the Surface hardware bundle separate from infrastructure secrets and server bootstrap material.

Python environment discovery: the packages role repairs missing native PET files in universal Open VSX Python Environments builds, using the matching version's native Microsoft extension archive. The helper verifies package identity and ELF architecture, preserves third-party notices and caches the archive/hash outside Git. It runs during setup and before the user service starts; an unavailable repair download does not prevent the editor starting. Reload the editor after an initial repair.
