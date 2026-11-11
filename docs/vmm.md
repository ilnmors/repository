# VMM

VMM is the physical hypervisor. Console prepares its initial files and then runs Ansible over SSH to configure host networking, storage, operational packages and libvirt virtual machines.

## Composition and Scope

1. Initial environment: a fresh Debian installation and the generated VMM bootstrap bundle.
2. Operational environment: the nodes, packages and libvirt roles in [vmm.yaml](../ansible/playbooks/nodes/vmm.yaml).
3. Virtual machines: cloud-init seeds, disk images and domain registration declared by inventory. VM application services are applied by their own node playbooks.

## Prerequisites

- Complete [console.md](console.md), including collections, encrypted secrets and the intended CA hierarchy.
- Match the account and group in [nodes.yaml](../ansible/inventory/group_vars/repository/nodes.yaml): `vmm`, UID `2000`, `svadmins`, GID `2000`.
- Verify [hardwares.yaml](../ansible/inventory/group_vars/repository/hardwares.yaml), networks, NIC names, disk serials and passthrough devices before generating files.
- Prepare blank physical data/backup devices or devices already matching the declared filesystem and labels. A differently formatted nonempty device is not equivalent to a blank device.
- Keep backups outside disks that will be initialized. The generated bootstrap changes networking, firewall, SSH and boot configuration; use local console access for the first run.
- eGPU passthrough is not assumed to be configured or tested. Declare only devices that are actually present and intended for passthrough.

## Initializing a VMM environment

### Generate the bootstrap files on Console

```bash
cd "$REPOSITORY_DIR/ansible"
ansible-playbook playbooks/nodes/console.yaml --tags vmm-init
```

The explicitly tagged bootstrap play writes `tools/build/vmm/init/`. It is not included in an ordinary Console site run. Review the generated networkd, nftables, IOMMU/VFIO and SSH files against the physical host.

The bundle contains an initial password hash and SSH CA trust configuration. Treat it as sensitive operational material, keep its permissions restricted, and transfer the entire directory securely to VMM. It does not belong in the Surface hardware bundle.

### Execute the bootstrap on VMM

```bash
cd /path/to/transferred/init
sudo bash vmm-init.sh
```

The script prepares the declared user, installs hypervisor packages, deploys networking/firewall/SSH trust, and updates boot configuration. Follow its reboot instructions. Verify the host's management address and Console SSH access before continuing.

The bootstrap only sets the initial password when creating the VMM account. An existing account must already match the declaration; the script is not a general account migration tool.

## Configuring an operational environment

### Execute the VMM playbook

```bash
cd "$REPOSITORY_DIR/ansible"
ansible-playbook playbooks/nodes/vmm.yaml --syntax-check
ansible-playbook playbooks/nodes/vmm.yaml --tags init
```

The `init` tag permits the initial SSH connection without an established host-certificate trust entry. Use this only for the freshly prepared host whose identity you have checked. Subsequent normal runs use the configured SSH trust:

```bash
ansible-playbook playbooks/nodes/vmm.yaml
```

The playbook configures physical storage, management networking, routing/firewall, host packages, Kopia server and libvirt guests according to inventory. Disk initialization and passthrough are host-specific operations; a successful syntax check does not validate the physical disk selection.

### Validate the result

```bash
# On VMM
id vmm
ip address
findmnt
lsblk -f
sudo nft list ruleset
sudo virsh list --all
systemctl --failed
sudo journalctl -b -p err
```

Verify that storage labels and mounted paths match inventory, management access survives a reboot, and each expected VM has the declared cloud-init account and address. New VM UIDs come from inventory; they need not equal UIDs from the old installation.

### Configure VM services

After the guests have booted and SSH is available, apply their node playbooks from Console:

```bash
cd "$REPOSITORY_DIR/ansible"
ansible-playbook playbooks/nodes/infra.yaml
ansible-playbook playbooks/nodes/auth.yaml
ansible-playbook playbooks/nodes/app.yaml
```

Restore existing application data only with its compatible database passwords, LDAP credentials, encryption keys and external API values. Root CA retention, new subordinate certificates and the new SSH CA are separate migration choices. Do not copy the old secrets file wholesale into the new schema.

## Operational notes

- Console's master Kopia identity has full repository management ACLs. Configure its workspace backup client separately when desired; it was not enabled on the current Surface during preparation.
- The generated bootstrap and Ansible roles are the source of deployment configuration. Existing host state is evidence for migration, not a substitute for inventory.
- A clean installation does not remove the need to check actual NICs, disk serials, account IDs, certificate trust and runtime paths.
