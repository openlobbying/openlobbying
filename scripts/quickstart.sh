#!/usr/bin/env bash
# The README Quickstart as a script: crawl one small dataset into SQLite, build and
# publish an ingest, start the API on it and query it.
#
# CI runs this on every PR (.github/workflows/quickstart.yml), so it is the tested
# version of the README's Quickstart section. Change both together.
#
# Prerequisites: muckrake cloned next to this repo (../muckrake) and `uv sync` done.
# It writes only to data/ in this checkout. The database URLs are set here, so a
# Postgres URL in your .env is ignored (exported variables win over .env).
#
# Usage: scripts/quickstart.sh            (API on port 8000)
#        PORT=8078 scripts/quickstart.sh
set -euo pipefail
cd "$(dirname "$0")/.."

DATASET=gb_firs
PORT="${PORT:-8000}"
API="http://127.0.0.1:$PORT"

# Working DB (crawl, load, release-build) and published DB (release-publish, API).
# release-publish refuses to run unless they are different databases.
export MUCKRAKE_DATABASE_URL=sqlite:///data/muckrake.db
export MUCKRAKE_PUBLISHED_DATABASE_URL=sqlite:///data/published.db

mkdir -p data

echo "== Datasets"
uv run muckrake list

echo "== Crawl and load $DATASET"
uv run muckrake -v crawl "$DATASET"
uv run muckrake -v load "$DATASET"

echo "== Build and publish an ingest"
release_id=$(uv run muckrake release-build "$DATASET" | sed -n 's/^Built release //p')
echo "built ingest $release_id"
uv run muckrake -v release-publish "$release_id"

echo "== Start the API on $API"
uv run openlobbying server --port "$PORT" &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
for _ in $(seq 90); do
  curl -sf "$API/" >/dev/null && break
  kill -0 "$server_pid" 2>/dev/null || { echo "API exited before it was ready" >&2; exit 1; }
  sleep 1
done
curl -sf "$API/" >/dev/null || { echo "API did not start within 90s" >&2; exit 1; }

echo "== Query it"
# Search for the first word of one published company's name, then open its profile.
name=$(curl -sf "$API/entities?schema=Company&limit=1" \
  | uv run python -c 'import json, sys; print(json.load(sys.stdin)["results"][0]["caption"])')
term=${name%% *}
search=$(curl -sf --get "$API/search" --data-urlencode "q=$term")
entity_id=$(echo "$search" \
  | uv run python -c 'import json, sys; r = json.load(sys.stdin)["results"]; assert r, "search returned nothing"; print(r[0]["id"])')
echo "/search?q=$term -> $entity_id"
curl -sf "$API/profile/$entity_id" \
  | uv run python -c 'import json, sys; p = json.load(sys.stdin); assert p["id"] and p["caption"], p; print("/profile ->", p["caption"])'

echo "== Quickstart OK"
