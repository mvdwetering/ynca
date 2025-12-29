#!/usr/bin/env bash
set -euo pipefail

# bump_version.sh - bump version in pyproject.toml, commit, tag and optionally push

WORKTREE_ROOT="$(cd "$(dirname "$0")" && pwd)"
PYPROJECT="$WORKTREE_ROOT/pyproject.toml"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but not found in PATH" >&2
  exit 2
fi

if [ ! -f "$PYPROJECT" ]; then
  echo "pyproject.toml not found at $PYPROJECT" >&2
  exit 2
fi

cd "$WORKTREE_ROOT"

# Ensure we are on the master branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "master" ]; then
  echo "Error: You must be on the master branch to bump the version. Current branch: $CURRENT_BRANCH" >&2
  exit 1
fi

echo "Checking git status..."
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree is not clean. Please commit or stash changes before running this script." >&2
  git status --porcelain
  exit 1
fi

CURRENT_VERSION=$(grep -E '^version\s*=\s*"[0-9]+' "$PYPROJECT" | head -n1 | sed -E 's/.*version\s*=\s*"([^"]+)".*/\1/')
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

# Compare semantic versions by splitting into components
version_to_array() {
  IFS='.' read -r -a parts <<< "$1"
  # pad to 3 components
  for i in {0..2}; do
    parts[$i]=${parts[$i]:-0}
  done
  printf "%03d%03d%03d" "${parts[0]}" "${parts[1]}" "${parts[2]}"
}

CUR_KEY=$(version_to_array "$CURRENT_VERSION")
NEW_KEY=$(version_to_array "$NEW_VERSION")

if [ "$NEW_KEY" -le "$CUR_KEY" ]; then
  echo "New version ($NEW_VERSION) is not greater than current version ($CURRENT_VERSION). Aborting." >&2
  exit 1
fi

echo "Updating $PYPROJECT: $CURRENT_VERSION -> $NEW_VERSION"

# Use a safe inplace edit that preserves permissions; use awk to replace the first version occurrence in [project] section
awk -v newver="$NEW_VERSION" '
  BEGIN{inproj=0;done=0}
  /^\[project\]/{inproj=1}
  inproj && !done && /version\s*=/{sub(/version\s*=\s*"[^"]+"/, "version = \"" newver "\""); done=1}
  {print}
' "$PYPROJECT" > "$PYPROJECT.tmp" && mv "$PYPROJECT.tmp" "$PYPROJECT"

git add "$PYPROJECT"
git commit -m "Bump ynca version to $NEW_VERSION"

TAG="v$NEW_VERSION"
echo "Creating git tag $TAG"
git tag -a "$TAG" -m "Version $NEW_VERSION"

read -r -p "Push commit and tag to remote? [y/N]: " PUSH_ANS
if [[ "$PUSH_ANS" =~ ^[Yy]$ ]]; then
  git push
  git push origin "$TAG"
  echo "Pushed commit and tag $TAG"
else
  echo "Skipped pushing. You can push later with: git push && git push origin $TAG"
fi

echo "Done."
