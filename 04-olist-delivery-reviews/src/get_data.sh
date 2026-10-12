#!/usr/bin/env bash
# Downloads the Olist CSVs into data/raw/.
# Source of record: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# This script uses a public GitHub mirror so no Kaggle login is needed.
set -euo pipefail
cd "$(dirname "$0")/.."
tmp="$(mktemp -d)"
git clone --depth 1 -q https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist "$tmp/olist"
mkdir -p data/raw
cp "$tmp"/olist/files/*.csv data/raw/
rm -rf "$tmp"
ls -1 data/raw
