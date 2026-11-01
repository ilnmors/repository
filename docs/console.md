# Console

Console is the external control node in this repository for executing Ansible and managing infrastructure.

This document describes the process to set up an initial environment for using Ansible and then configure standard operational settings using the Console playbook.

> <Notice>
> This example has been tested on Debian/Ubuntu environments.

## Composition and Scope

1. Initial environment for using Ansible
    - Method: Executing manual commands or a bootstrap script.
    - Purpose:
        - Setting the repository root directory
        - Installing Ansible, git, python, gnupg, sops
        - Creating `secrets.yaml`
        - Installing Ansible collections
2. Operational environment for the repository
    - Method: Executing ansible-playbook
    - Purpose:
        - Installing operational tools
        - Setting permissions
        - etc.

## Prerequisites

- A user account for tasks on Console
    - Set the UID, GID, and other settings in [nodes.yaml](../ansible/inventory/group_vars/repository/nodes.yaml)
- `sudo` privileges for installing system packages and changing settings
- Network access to package repositories and download links.

## Initializing an Ansible environment

### Installing essential packages

```bash
# Debian/Ubuntu
# APT packages
sudo apt update && sudo apt upgrade
sudo apt install \
    git \
    gnupg \
    age \
    curl \
    jq \
    openssl
sudo apt install \
    ansible-core \
    ansible-lint \
    --no-install-recommends

# SOPS
SOPS_VER="VERSION" # Change version
SOPS_ARCH="[arm64|amd64]" # Select architecture
curl -L -C - -o ./sops_${SOPS_VER}.deb \
    "https://github.com/getsops/sops/releases/download/v${SOPS_VER}/sops_${SOPS_VER}_${SOPS_ARCH}.deb"
sudo apt install ./sops_${SOPS_VER}.deb
rm -rf ./sops_${SOPS_VER}.deb

# step-cli
STEP_VER="VERSION" # Change version
STEP_ARCH="[arm64|amd64]" # Select architecture
curl -L -C - -o ./step_${STEP_VER}.deb \
    "https://dl.smallstep.com/gh-release/cli/gh-release-header/v${STEP_VER}/step-cli_${STEP_VER}-1_${STEP_ARCH}.deb"
sudo apt install ./step_${STEP_VER}.deb
rm -rf ./step_${STEP_VER}.deb
```

### Creating secrets.yaml

```bash
cd ${REPOSITORY_DIR}/ansible/roles/secrets/files
# Create age-key
mkdir -p /tmp/console
chmod 700 /tmp/console
age-keygen -o /tmp/console/age-key
AGE_RECIPIENT=$(age-keygen -y /tmp/console/age-key)
chmod 600 /tmp/console/*

# Create .sops.yaml
cat << EOF > .sops.yaml
creation_rules:
  - path_regex: secrets\.yaml$
    age: ${AGE_RECIPIENT}
EOF
# Create secrets.yaml
SOPS_AGE_KEY_FILE=/tmp/console/age-key \
    sops edit secrets.yaml

# --- secrets.yaml ---
# sudo:
#   console:
#       password: $CONSOLE_SUDO_PASSWORD
# ------

# Check secrets.yaml
SOPS_AGE_KEY_FILE=/tmp/console/age-key \
    sops decrypt secrets.yaml > /dev/null

# Encrypt age-key (gpg)
gpg --symmetric --cipher-algo AES256 \
    --output ./age-key.gpg \
    /tmp/console/age-key
# password: $PASSWORD
# Check age-key.gpg
gpg --decrypt age-key.gpg > /dev/null

# Encrypt age-key (ansible-vault)
cd ../vars
grep '^AGE-SECRET-KEY-' /tmp/console/age-key |
    ansible-vault encrypt_string --stdin-name secrets_age_key
nano main.yaml
# --- main.yaml ---
# ---
# secrets_age_key: !vault |
#   $ANSIBLE_VAULT;1.1;AES256
#   ...
# ------

# Remove plain age-key
rm /tmp/console/age-key
unset SOPS_AGE_KEY_FILE

# Create script symbolic link
cd ${REPOSITORY_DIR}/tools/scripts
ln -s ../../ansible/roles/secrets/files/scripts/edit_secret.sh \
    ./edit_secret.sh
```

### Installing Ansible collections

```bash
cd ${REPOSITORY_DIR}/ansible
ansible-galaxy install -r requirements.yaml
```

## Configuring an operational environment

### Create PKI

```bash
# Create passwords for the private keys of the root and intermediate CAs
openssl rand -base64 32
openssl rand -base64 32
cd ${REPOSITORY_DIR}/tools/scripts
./edit_secret.sh
# --- secrets.yaml ---
# ---
# ...
# ca:
#   x509:
#       root:
#           password: $BASE64_PASSWORD_ROOT
#       intermediate:
#           password: $BASE64_PASSWORD_INTERMEDIATE
# ---

# Create the root and intermediate CAs
cd ${REPOSITORY_DIR}/ansible
ansible-playbook playbooks/pki.yaml --tags "root, intermediate, ssh"
```

### Execute a console playbook

<!-- WIP -->
