#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <server-ip-or-hostname> [ssh-key-path]"
  exit 1
fi

SERVER="$1"
KEY_PATH="${2:-$HOME/.ssh/id_ed25519}"

echo "[1/4] Sync OpenLobbying code to VPS"
rsync -az --delete \
  --exclude ".git" \
  --exclude ".env" \
  --exclude ".venv" \
  --exclude "data" \
  --exclude "node_modules" \
  --exclude ".svelte-kit" \
  --exclude "build" \
  -e "ssh -i $KEY_PATH" \
  ./ "deploy@$SERVER:/home/deploy/openlobbying/"

echo "[2/4] Sync sibling muckrake dependency"
rsync -az --delete \
  --exclude ".git" \
  --exclude ".env" \
  --exclude ".venv" \
  --exclude "data" \
  -e "ssh -i $KEY_PATH" \
  ../muckrake/ "deploy@$SERVER:/home/deploy/muckrake/"

echo "[3/4] Install deps, build frontend, restart services"
ssh -i "$KEY_PATH" "deploy@$SERVER" '
  set -e
  cd /home/deploy/openlobbying
  /home/deploy/.local/bin/uv sync
  npm ci
  npm run build
  sudo systemctl restart openlobbying-api openlobbying-web caddy
'

echo "[4/4] Done"
echo "Open: https://openlobbying.org"
