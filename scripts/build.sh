#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

temp_dist="dist_tmp"
final_dist="dist"
binary_name="NotifyMe"

rm -rf "$temp_dist"

echo "Building NotifyMe for Linux..."
export PYSTRAY_BACKEND="${PYSTRAY_BACKEND:-gtk}"
if command -v uv >/dev/null 2>&1; then
  uv run pyinstaller --distpath "$temp_dist" -y NotifyMe_linux.spec
elif [[ -x "./.venv/bin/python" ]]; then
  ./.venv/bin/python -m PyInstaller --distpath "$temp_dist" -y NotifyMe_linux.spec
else
  python -m PyInstaller --distpath "$temp_dist" -y NotifyMe_linux.spec
fi

if [[ ! -f "$temp_dist/$binary_name" ]]; then
  echo "Build failed: executable not created in $temp_dist" >&2
  exit 1
fi

mkdir -p "$final_dist"
mv -f "$temp_dist/$binary_name" "$final_dist/$binary_name"
rm -rf "$temp_dist"

sha256sum "$final_dist/$binary_name" > "$final_dist/SHA256SUMS.txt"

echo "Executable created at: $final_dist/$binary_name"
echo "SHA256 written to: $final_dist/SHA256SUMS.txt"
