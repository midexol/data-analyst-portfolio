#!/usr/bin/env bash
# Downloads Our World in Data's energy dataset into data/raw/.
# Pinned to the exact version I used, so the numbers match the write-up.
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION=f8de88a4f6f9cab44f1cf606047cbd6c4414042c
tmp="$(mktemp -d)"
git clone -q https://github.com/owid/energy-data "$tmp/energy-data"
git -C "$tmp/energy-data" checkout -q "$VERSION"
mkdir -p data/raw
cp "$tmp/energy-data/owid-energy-data.csv" "$tmp/energy-data/owid-energy-codebook.csv" data/raw/
rm -rf "$tmp"
ls -1 data/raw
