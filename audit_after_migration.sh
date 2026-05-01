#!/usr/bin/env bash
set -u

cd ~/codeberg-migration || exit 1

echo "=== Repos with LFS files ==="
for repo_dir in *.git; do
  repo_name="${repo_dir%.git}"
  count="$(git --git-dir="$repo_dir" lfs ls-files 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$count" != "0" ]; then
    echo "$repo_name: $count LFS files"
  fi
done

echo
echo "=== Repos with submodules ==="
for repo_dir in *.git; do
  repo_name="${repo_dir%.git}"
  if git --git-dir="$repo_dir" show HEAD:.gitmodules >/dev/null 2>&1; then
    echo "$repo_name"
  fi
done

echo
echo "=== Repos using master but not main ==="
for repo_dir in *.git; do
  repo_name="${repo_dir%.git}"
  if ! git --git-dir="$repo_dir" show-ref --verify --quiet refs/heads/main \
     && git --git-dir="$repo_dir" show-ref --verify --quiet refs/heads/master; then
    echo "$repo_name"
  fi
done

echo
echo "=== Repos with gh-pages branch ==="
for repo_dir in *.git; do
  repo_name="${repo_dir%.git}"
  if git --git-dir="$repo_dir" show-ref --verify --quiet refs/heads/gh-pages; then
    echo "$repo_name"
  fi
done

echo
echo "=== Repos with GitHub Actions workflows ==="
for repo_dir in *.git; do
  repo_name="${repo_dir%.git}"
  if git --git-dir="$repo_dir" ls-tree -r HEAD --name-only 2>/dev/null | grep -q '^.github/workflows/'; then
    echo "$repo_name"
  fi
done
