# Deployment

- `ops/deploy_to_vps.sh`: app deploy script.
- `ops/systemd/`: service templates.
- `ops/caddy/openlobbying.org.Caddyfile`: reverse proxy config.
- `ops/hetzner/`: Hetzner bootstrap notes and templates.

Production env must live on the server under `/etc/openlobbying/app.env`.

The current deployment keeps both repositories side by side on the server:

- `/home/deploy/openlobbying`
- `/home/deploy/muckrake`

- Shared required settings: `MUCKRAKE_DATABASE_URL`, `MUCKRAKE_PUBLISHED_DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`.
- Web runtime settings: `HOST`, `PORT`, `ORIGIN`, `NODE_ENV`.
- Optional shared settings: `OPENLOBBYING_API_URL`, `OPENLOBBYING_ADMIN_API_SECRET`, `MUCKRAKE_DATA_PATH`, `MUCKRAKE_ARTIFACT_PATH`, `MUCKRAKE_DATASET_PATHS`, `OPENROUTER_API_KEY`, `LLM_MODEL`, `NER_LLM_PROMPT_FILE`, `LOGFIRE_TOKEN`.
- `deploy_to_vps.sh` intentionally does not sync local `.env` files to the VPS.

For the full runbook, see `ops/hetzner/README.md`.
