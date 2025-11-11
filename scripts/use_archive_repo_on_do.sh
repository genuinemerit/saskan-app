#!/usr/bin/env bash

# This script is to set Digital Ocean apt repo to archive version.
# Stog-gap measure before migrating to a more stable Ubuntu LTS.

set -euo pipefail

BACKUP_DIR="/root/apt-backups-$(date +%Y%m%dT%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "1) Backing up apt sources to $BACKUP_DIR ..."
cp -a /etc/apt/sources.list "$BACKUP_DIR/sources.list.bak" || true
mkdir -p "$BACKUP_DIR/sources.list.d"
cp -a /etc/apt/sources.list.d/*.list "$BACKUP_DIR/sources.list.d/" 2>/dev/null || true
cp -a /var/lib/apt/lists "$BACKUP_DIR/apt-lists.bak" 2>/dev/null || true

echo "2) Searching for files mentioning 'oracular' or DO mirrors..."
grep -R --line-number "oracular\|mirrors.digitalocean.com\|security.ubuntu.com" /etc/apt || true

echo "3) Replacing DO/Ubuntu mirrors with old-releases.ubuntu.com in sources.list and .list files..."
# create per-file .bak via sed so we can inspect originals
for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do
  [ -f "$f" ] || continue
  echo " - editing $f"
  sed -n '1,120p' "$f" | sed 's/^/    /'
  sudo sed -i.bak \
    -e 's|http://mirrors.digitalocean.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' \
    -e 's|https://mirrors.digitalocean.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' \
    -e 's|http://security.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' \
    "$f"
done

echo
echo "4) Confirming files now point to old-releases..."
grep -R --line-number "old-releases.ubuntu.com" /etc/apt || true

echo
echo "5) Running apt update (only). Inspect the output carefully."
# run update but keep verbose logging to stdout and also write to a temp file
TMPLOG="/tmp/apt-update-$(date +%s).log"
sudo apt update 2>&1 | tee "$TMPLOG"

echo
echo "---- First 80 lines of apt update output (for quick inspection) ----"
head -n 80 "$TMPLOG" || true
echo "---- End preview ----"

cat <<'EOF'

NEXT STEPS (you choose):
- If apt update looks good (no Release/404 errors), run:
    sudo apt -y full-upgrade
  or upgrade only specific packages:
    sudo apt install <package-name>

- To revert the sources to the originals from the backup created by this script:
    sudo cp "$BACKUP_DIR/sources.list.bak" /etc/apt/sources.list
    sudo cp -a "$BACKUP_DIR/sources.list.d/"* /etc/apt/sources.list.d/ 2>/dev/null || true
    sudo apt update

Notes:
- This script does NOT perform a full-upgrade automatically.
- If you have any third-party .list files that point to other hosts, check them manually.
EOF
