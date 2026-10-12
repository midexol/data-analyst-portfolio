#!/usr/bin/env bash
# Runs every query in sql/ against Stellar's public Hubble dataset and saves CSVs to outputs/.
# Needs: gcloud auth login, a project with billing enabled (queries are billed to YOU).
# Set a budget alert in the Cloud console before the first run.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${GCP_PROJECT:?set GCP_PROJECT to your Google Cloud project id}"
MAX_BYTES="${MAX_BYTES:-200000000000}"   # refuse any query that would scan more than ~200 GB
mkdir -p outputs
for f in sql/*.sql; do
  name="$(basename "$f" .sql)"
  echo "== $name: dry run"
  bq --project_id="$GCP_PROJECT" query --use_legacy_sql=false --dry_run < "$f"
  echo "== $name: running"
  bq --project_id="$GCP_PROJECT" query --use_legacy_sql=false --format=csv --max_rows=100000 \
     --maximum_bytes_billed="$MAX_BYTES" < "$f" > "outputs/$name.csv"
done
ls -1 outputs
