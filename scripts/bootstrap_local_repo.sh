#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/bootstrap_local_repo.sh /path/to/cloned/progress-engine
#
# This script copies the repo-ready starter contents into an already cloned
# GitHub repository. Run it from the extracted starter package root.

TARGET_DIR="${1:-}"
if [[ -z "$TARGET_DIR" ]]; then
  echo "Usage: $0 /path/to/cloned/progress-engine" >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR/.git" ]]; then
  echo "Target must be a cloned git repository: $TARGET_DIR" >&2
  exit 1
fi

rsync -av --exclude='.git' ./ "$TARGET_DIR"/
cd "$TARGET_DIR"
python3 scripts/check_repo.py || true

echo "
Next steps:"
echo "  git status"
echo "  git add ."
echo "  git commit -m 'docs: bootstrap ProgressEngine project state'"
echo "  git push origin main"
