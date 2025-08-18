#!/usr/bin/env bash
set -euo pipefail

: "${SASKAN_REPO:?Set SASKAN_REPO to <owner>/<repo>, e.g. export SASKAN_REPO=org/saskan-app}"
DRY_RUN="${DRY_RUN:-0}"   # set to 1 to preview without changes

# name | description | hex color
read -r -d '' LABELS <<'EOF'
feat|New features|#2EA043
fix|Bug fixes|#D73A4A
hotfix|Emergency production fixes|#B60205
perf|Performance improvements|#FBCA04
refactor|Code refactoring / internal|#A371F7
docs|Documentation updates|#0075CA
chore|Maintenance / housekeeping|#8C959F
build|Build system changes|#6E7781
ci|Continuous integration config|#1D76DB
dependencies|Dependency updates (manual)|#94D3A2
deps|Automated dependency updates (bots)|#C2E0C6
security|Security-related changes|#B60205
breaking-change|Backward-incompatible change|#000000
skip-changelog|Exclude from release notes|#E4E669
EOF

echo "Target repo: $SASKAN_REPO"
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY RUN] Will create/update the following labels:"
fi

# Ensure gh is available
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) not found. Install: https://cli.github.com/"
  exit 1
fi

# Validate repo access
if ! gh repo view "$SASKAN_REPO" >/dev/null 2>&1; then
  echo "ERROR: Cannot access repo $SASKAN_REPO. Check auth and SASKAN_REPO value."
  exit 1
fi

# Create/update labels
while IFS='|' read -r name desc color; do
  [[ -z "$name" ]] && continue
  color="${color#\#}"  # strip leading '#'
  if [[ "$DRY_RUN" == "1" ]]; then
    printf " - %-16s | %s | %s\n" "$name" "$desc" "$color"
  else
    gh label create "$name" \
      --repo "$SASKAN_REPO" \
      --description "$desc" \
      --color "$color" \
      --force \
      >/dev/null
    echo "Upserted label: $name"
  fi
done <<< "$LABELS"

echo "Done."
