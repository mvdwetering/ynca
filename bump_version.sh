#!/usr/bin/env bash
set -euo pipefail

# bump_version.sh - trigger the GitHub Actions Release workflow
# Requires the GitHub CLI (gh) to be installed and authenticated.

WORKTREE_ROOT="$(cd "$(dirname "$0")" && pwd)"
PYPROJECT="$WORKTREE_ROOT/pyproject.toml"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required but not found in PATH" >&2
  echo "Install it from https://cli.github.com/" >&2
  exit 2
fi

CURRENT_VERSION=$(grep -E '^version\s*=\s*"[0-9]+' "$PYPROJECT" | head -n1 \
  | sed -E 's/.*version\s*=\s*"([^"]+)".*/\1/')

if [ -z "$CURRENT_VERSION" ]; then
  echo "Could not determine current version from $PYPROJECT" >&2
  exit 2
fi

echo "Current version: $CURRENT_VERSION"
read -r -p "Enter new version: " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
  echo "No version entered. Aborting." >&2
  exit 1
fi

# Validate semver format
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Version '$NEW_VERSION' is not valid semver (expected X.Y.Z). Aborting." >&2
  exit 1
fi

# Validate new > current
version_key() {
  echo "$1" | awk -F. '{ printf "%05d%05d%05d", $1, $2, $3 }'
}

if [ "$(version_key "$NEW_VERSION")" -le "$(version_key "$CURRENT_VERSION")" ]; then
  echo "New version ($NEW_VERSION) is not greater than current version ($CURRENT_VERSION). Aborting." >&2
  exit 1
fi

echo "Triggering Release workflow for v$NEW_VERSION ..."
gh workflow run release.yml --field "version=$NEW_VERSION"

echo ""
echo "Workflow triggered. Follow progress at:"
echo "  https://github.com/mvdwetering/ynca/actions/workflows/release.yml"
