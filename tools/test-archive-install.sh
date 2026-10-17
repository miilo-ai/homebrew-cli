#!/usr/bin/env bash
set -euo pipefail
miilo_executable=${1:-miilo}
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
printf '%s\n' 'Synthetic installed compression smoke test.' > "$stage/input"
for codec in gzip brotli zstd; do
  "$miilo_executable" archive export "$stage/input" "$stage/$codec.miilo" --codec "$codec"
  "$miilo_executable" archive inspect "$stage/$codec.miilo"
  "$miilo_executable" archive restore "$stage/$codec.miilo" "$stage/$codec.restored"
  cmp "$stage/input" "$stage/$codec.restored"
  if "$miilo_executable" archive restore "$stage/$codec.miilo" "$stage/$codec.restored"; then
    echo 'ERROR: existing output was overwritten' >&2
    exit 1
  fi
  cmp "$stage/input" "$stage/$codec.restored"
done
