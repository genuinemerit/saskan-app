#!/usr/bin/env bash
# Exit on failure, undefined vars, or pipe errors so deployments fail fast.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# default to <repo>/assets unless overridden
LOCAL_ASSETS_DIR="${LOCAL_ASSETS_DIR:-$REPO_ROOT/assets}"
WEB_ROOT="${WEB_ROOT:-/usr/share/nginx/html/sfp}"
REMOTE_ASSETS_DIR="${REMOTE_ASSETS_DIR:-$WEB_ROOT/saskan/assets}"

# sanity check before rsync
if [[ ! -d "$LOCAL_ASSETS_DIR" ]]; then
  echo "Local assets dir not found: $LOCAL_ASSETS_DIR" >&2
  echo "Set LOCAL_ASSETS_DIR=… or create $REPO_ROOT/assets/" >&2
  exit 2
fi

# --------- How to use -------
# First preview (no changes on server)
#  DRY_RUN=1 infra/deploy/push-assets.sh
# Real push + reload
#  infra/deploy/push-assets.sh
# Push and also check a specific asset URL
#  CHECK_ASSET_REL=/saskan/assets/v0/images/barbican.6f8b1c2.webp infra/deploy/push-assets.sh
# ------------------------------------

# --- Config (defaults; override via env if needed) -----------------------
# Most knobs can be adjusted via env vars so CI or local machines can reuse the
# script without editing it. Power users run `VAR=value ./push-assets.sh`.
REMOTE="${REMOTE:-saskan}"                               # SSH alias (from ~/.ssh/config)
WEB_ROOT="${WEB_ROOT:-/usr/share/nginx/html/sfp}"        # your site root on the server
REMOTE_ASSETS_DIR="${REMOTE_ASSETS_DIR:-$WEB_ROOT/saskan/assets}"
LOCAL_ASSETS_DIR="${LOCAL_ASSETS_DIR:-assets}"           # repo-local assets/
BASE_URL="${BASE_URL:-https://sfp.genuinemerit.org}"     # public base
CHECK_ASSET_REL="${CHECK_ASSET_REL:-}"                   # e.g., /saskan/assets/v0/images/barbican.6f8b1c2.webp

# Dry run: set DRY_RUN=1 to preview rsync without changing remote
if [[ "${DRY_RUN:-0}" == "1" ]]; then
  RSYNC_FLAGS="-avzn"    # n = --dry-run
  DO_RELOAD=0
  echo "DRY RUN mode: will NOT reload nginx."
else
  RSYNC_FLAGS="-avz"
  DO_RELOAD=1
fi

# Fail if any publishable asset exceeds 1MB
# (Build tooling should enforce this already; we re-check before syncing.)
big=$(find "$LOCAL_ASSETS_DIR/v0" -type f -size +1048576c -printf '%P\n' || true)
if [[ -n "$big" ]]; then
  echo "❌ Assets over 1MB (publishable only):" >&2
  echo "$big" >&2
  exit 4
fi

# --- Warm up the Control Master (avoid having enter pwd multiple times)
# This is a no-op if multiplexing is disabled; otherwise it pre-opens SSH.
ssh -fN saskan 2>/dev/null || true

# --- Ensure target dir exists -------------------------------------------
ssh "$REMOTE" "mkdir -p '$REMOTE_ASSETS_DIR'"

# --- Push assets (trailing slash on source = sync contents, not folder) --
rsync $RSYNC_FLAGS --delete \
  --exclude 'local/**' \
  --exclude 'thumbs/**' \
  --exclude '.DS_Store' --exclude 'Thumbs.db' \
  "$LOCAL_ASSETS_DIR/" "$REMOTE:$REMOTE_ASSETS_DIR/"

# --- Reload nginx on remote (skip in dry-run) ---------------------------
if [[ "$DO_RELOAD" -eq 1 ]]; then
  ssh "$REMOTE" 'nginx -t && systemctl reload nginx'
fi

# --- Quick HEAD checks ---------------------------------------------------
# Spot-check manifest (and optionally a specific asset) to confirm headers
# and cache-control values look right from the public endpoint.
echo "— manifest.json —"
curl -sI "$BASE_URL/saskan/assets/manifest.json" | sed -n '1p;/Cache-Control/p;/Access-Control-Allow-Origin/p'

if [[ -n "$CHECK_ASSET_REL" ]]; then
  echo "— asset: $CHECK_ASSET_REL —"
  curl -sI "$BASE_URL$CHECK_ASSET_REL" | sed -n '1p;/Cache-Control/p;/Access-Control-Allow-Origin/p'
fi

echo "✅ Done."
