# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is the **OpenLobbying application repo** (openlobbying.org): the UK lobbying dataset crawlers, the FastAPI API, and the SvelteKit frontend. The pipeline engine is `muckrake`, consumed as an **editable path dependency** from the sibling checkout (`../muckrake`) — changes there apply here immediately. Repo-agnostic pipeline logic belongs in muckrake; anything OpenLobbying-specific belongs here. The parent directory's `CLAUDE.md` carries the cross-repo programme context (the muckrake × UTI merge).

## Commands

Always run Python via `uv` (never `python`/`python3`/`pip` directly). Run muckrake CLI commands **from this repo** so dataset discovery (`./datasets/`) and `.env` loading use this checkout.

- `uv sync` — Python deps (includes editable muckrake). `npm install` — frontend deps.
- `uv run openlobbying server --reload` — FastAPI API on `127.0.0.1:8000`.
- `npm run dev` — SvelteKit dev server at `:5173`; Vite proxies `/api/*` to `OPENLOBBYING_API_URL` (default `http://127.0.0.1:8000`).
- `npm run check` — Svelte/TS type-check. `npm run build` / `npm run preview` — production build (adapter-node; production runtime is `node build`).
- `uv run muckrake list` / `crawl <name>` / `ner-extract` / `load <name>` / `xref` / `dedupe` / `dedupe-edges` / `release-build` / `release-publish <id>` — the pipeline over this repo's datasets. Never `load` directly into the published DB; go through releases.
- `uv run pytest` — tests (crawler/dataset tests live here, e.g. `tests/test_gov_transparency_*`). Single test: `uv run pytest tests/test_foo.py::test_bar`.

## Layout

- `datasets/<country>/<name>/` — crawlers (`config.yml` + `crawler.py`). **Read `datasets/AGENTS.md` for the entity-creation contract before writing or changing a crawler**; some datasets have their own `AGENTS.md` (e.g. `datasets/gb/orcl/` documents the Salesforce Visualforce/AJAX postback flow — direct URL fetches can't replicate it). The dataset backlog is GitHub project board 1 ("Datasets") with issues in this repo.
- `src/openlobbying/api/` — FastAPI app (`server.py`, `graph_logic.py`, `serialization.py`, `view.py`). Reads only from the published DB (`MUCKRAKE_PUBLISHED_DATABASE_URL`).
- `src/` (rest) — SvelteKit frontend: `routes/`, `lib/`, `hooks.server.ts`.
- `ops/` — deployment: `deploy_to_vps.sh`, systemd templates, Caddy config, Hetzner bootstrap. Runbook in `ops/README.md`.
- `tests/fixtures/` — crawler test fixtures.

## Crawler conventions (summary — full contract in `datasets/AGENTS.md`)

- Stable IDs: `dataset.make("Schema")` + `dataset.make_id(...)`; prefer registration numbers (`make_id(reg_nr=..., register='GB-COH')` uses org-id) over name-based hashes.
- Check FtM schema docs for valid properties before adding fields: https://followthemoney.tech/explorer/schemata/
- `gb/` datasets set `jurisdiction=gb` (`gb-sct` for Scottish); categorise with `topics` (`role.lobby`, `role.pep`, `gov`, …).
- Fetch via `dataset.fetch_text/json/html` with `cache_days=N`. Crash loudly on ambiguous data — never emit a guessed value. Prefer `rigour`/`followthemoney`/`nomenklatura` helpers over hand-rolled normalisation.
- New crawlers are typed Python; be conservative about adding dependencies.

## Frontend

Svelte 5 + SvelteKit + TypeScript (strict) + Tailwind + shadcn-svelte. Use `$lib/...` imports, Svelte 5 runes (`$props`, `$derived`), `+page.ts` loaders fetching the API at runtime. `AGENTS.md` documents the Svelte MCP tool workflow (list-sections → get-documentation; run svelte-autofixer on written Svelte code) and shadcn-svelte usage.

Auth is `better-auth` (email/password; Kysely + `pg` against `MUCKRAKE_DATABASE_URL`): routes on `/auth/*` (kept off `/api/*` to avoid the proxy), login at `/login`, admin panel at `/admin` with role-based `user`/`admin`, protected example at `/account`. `BETTER_AUTH_SECRET`/`BETTER_AUTH_URL` required in production (dev falls back to a fixed local secret).

**Merge context for frontend work:** per the muckrake × UTI merge (decision [docs#3](https://github.com/openlobbying/docs/issues/3)), the public site moves to the fresh `undertheinfluence` repo (Astro/DRF/Wagtail); this SvelteKit app becomes the **internal data-review/admin tool** (it already hosts the dedupe web review). Weight frontend investment here toward internal review/curation tooling, not public-facing features.

## Environment

Repo-root `.env` (template `.env.example`), shared by Python and the frontend; muckrake discovers it automatically when run from here. Key vars: `MUCKRAKE_DATABASE_URL` (working DB), `MUCKRAKE_PUBLISHED_DATABASE_URL` (serving DB — keep separate when testing releases), `OPENLOBBYING_API_URL`, `BETTER_AUTH_*`, `OPENROUTER_API_KEY` + `LLM_MODEL` for LLM NER. Production env lives on the server at `/etc/openlobbying/app.env`; `ops/deploy_to_vps.sh` does **not** sync local `.env`. The server keeps this repo and muckrake side by side (`/home/deploy/{openlobbying,muckrake}`). The app serves a runtime sitemap index at `/sitemap.xml` backed by the API.

## Conventions

- Code style: simple and tidy — no speculative abstractions, no backwards-compat shims, no defensive handling of conditions that don't occur.
- Keep README.md / AGENTS.md accurate when changing behaviour.
- Don't commit, push, or open PRs unless asked. `gh` CLI is available for read-only GitHub interactions.
