# Deployment

The current production site is frozen while its replacement is built: don't run `deploy_to_vps.sh` against it. This README describes the existing setup for reference.

- `ops/deploy_to_vps.sh`: app deploy script. It rsyncs the local working trees of this repo and `../muckrake` (not a branch or tag), so check out `main` in both first.
- `ops/systemd/`: service templates.
- `ops/caddy/openlobbying.org.Caddyfile`: reverse proxy config.
- `ops/hetzner/`: Hetzner bootstrap notes and templates.

Production env must live on the server under `/etc/openlobbying/app.env`. The systemd units load it with `EnvironmentFile=`. muckrake also reads a repo-root `.env` unless `ENVIRONMENT=production` is set.

The current deployment keeps both repositories side by side on the server:

- `/home/deploy/openlobbying`
- `/home/deploy/muckrake`

## Settings

- Shared required settings: `MUCKRAKE_DATABASE_URL`, `MUCKRAKE_PUBLISHED_DATABASE_URL` (a different database from the working one), `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`. Better Auth needs `MUCKRAKE_DATABASE_URL` to be Postgres. The API reads the published DB, and its admin dedupe routes also write the working DB.
- Web runtime settings: `HOST`, `PORT`, `ORIGIN`, `NODE_ENV`.
- Optional shared settings: `OPENLOBBYING_API_URL`, `OPENLOBBYING_ADMIN_API_SECRET`, `MUCKRAKE_DATA_PATH`, `MUCKRAKE_ARTIFACT_PATH`, `MUCKRAKE_DATASET_PATHS`, `MUCKRAKE_HTTP_MIN_INTERVAL`, `LLM_MODEL`, `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`, `NER_LLM_PROMPT_FILE`, `LOGFIRE_TOKEN`.
- `deploy_to_vps.sh` intentionally does not sync local `.env` files to the VPS.

Known issue: `openlobbying-api.service` runs `/home/deploy/openlobbying/.venv/bin/uv`, while `deploy_to_vps.sh` runs `/home/deploy/.local/bin/uv` ([Deploy safety: systemd/deploy uv path mismatch; API CORS allows *](https://github.com/openlobbying/openlobbying/issues/36)).

Server bootstrap (Hetzner VPS, cloud-init, firewall) is in `ops/hetzner/README.md`.
