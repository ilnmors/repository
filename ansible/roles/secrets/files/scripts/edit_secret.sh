#!/bin/bash
set -e -o pipefail

# Get real path (POSIX.1-2024)
SCRIPT_PATH=$(realpath -e "$0") || exit 1
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

# Variables
RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$UID}"
KEY_FILE="$SCRIPT_DIR/../age-key.gpg"
SECRET_FILE="$SCRIPT_DIR/../secrets.yaml"


# Usage function
usage() {
    echo "Usage: $0" >&2
    echo "./scripts/edit_secret.sh"
    echo "./age-key.gpg and ./secrets.yaml are required"
    exit 1
}

# Log function
log() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local level="$1"
    local msg="$2"
    if [ "$level" == "error" ]; then
        echo "time=\"$timestamp\" level=\"$level\" msg=\"$msg\" source=\"edit_secret.sh\"">&2
    else
        echo "time=\"$timestamp\" level=\"$level\" msg=\"$msg\" source=\"edit_secret.sh\"">&1
    fi
}

# Secret file check
if [ -z "$SECRET_FILE" -o ! -f "$SECRET_FILE" ]; then
    log "error" "Secret file path is required"
    usage
    exit 1
fi

# age-key file check
if [ ! -f "$KEY_FILE" ]; then
    log "error" "age key path is required"
    exit 1
fi

# Dependency check
if ! command -v sops >/dev/null; then
    log "error" "sops is required"
    exit 1
fi

if ! command -v gpg >/dev/null; then
    log "error" "gnupg is required"
    exit 1
fi

TMP_PATH=$(mktemp -d "$RUNTIME_DIR/age-key.XXXXXXXX") || exit 1

# Cleanup function for trap
cleanup() {
    if [ -f "$TMP_PATH/age-key" ]; then
        rm -f "$TMP_PATH/age-key"
        log "info" "age key is deleted"
    fi
    if [ -d "$TMP_PATH" ]; then
        rmdir "$TMP_PATH"
    fi
}

# Trap
trap cleanup EXIT

# Get GPG password from prompt
echo -n "Enter GPG passphrase: " >&1
IFS= read -rs GPG_PASSPHRASE
echo "" >&1

# Decrypt age-key on the tmpfs (memory)
echo "$GPG_PASSPHRASE" | \
gpg --batch \
--yes \
--pinentry-mode loopback \
--no-symkey-cache \
--passphrase-fd 0 \
--output "$TMP_PATH/age-key" \
--decrypt "$KEY_FILE"

chmod 600 "$TMP_PATH/age-key"

# Unset environment Variables
unset GPG_PASSPHRASE

# Check the key on memory
if [ ! -f "$TMP_PATH/age-key" ]; then
    log "error" "age key does not exist"
    exit 1
fi

# Open sops editor and delete the key
SOPS_AGE_KEY_FILE="$TMP_PATH/age-key" sops "$SECRET_FILE"

exit 0
