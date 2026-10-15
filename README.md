## OpenLobbying

OpenLobbying is a mixed Python + Svelte application repo built on top of the reusable [muckrake](https://github.com/openlobbying/muckrake) data pipeline.

This repo owns:

- the OpenLobbying dataset crawlers under `datasets/`
- the OpenLobbying FastAPI app under `src/openlobbying/api/`
- the Svelte frontend under `src/`
- deployment assets under `ops/`

Work is tracked in this repo's issues and on the maintainers' [project board](https://github.com/orgs/openlobbying/projects/3) (private).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (it installs the Python version the project needs) and Node 24 with npm.
- **muckrake cloned next to this repo.** `pyproject.toml` uses `../muckrake` as an editable path dependency, so `uv sync` fails without it:

  ```sh
  git clone https://github.com/openlobbying/muckrake.git
  git clone https://github.com/openlobbying/openlobbying.git
  ```

- **ICU and pkg-config**, which `pyicu` (via nomenklatura and rigour) compiles against:
  - macOS: `brew install pkg-config icu4c`, then `export PKG_CONFIG_PATH="$(brew --prefix icu4c)/lib/pkgconfig"` before `uv sync` (Homebrew's `icu4c` is keg-only, so pkg-config can't find it otherwise).
  - Debian/Ubuntu: `sudo apt-get install pkg-config libicu-dev libleveldb-dev`.
- **LevelDB** (`plyvel`) is needed only by `muckrake xref`, `dedupe`, `dedupe-edges` and `export`. It builds on Linux with `libleveldb-dev`. On macOS the `plyvel` build doesn't load against Homebrew's leveldb, so run those four commands on Linux or in the muckrake Docker image. Everything else, including the tests, runs natively.

## Quickstart

These steps crawl one small dataset, build and publish an ingest from it, and start the API on it. They use SQLite only (no Docker or Postgres). [`scripts/quickstart.sh`](scripts/quickstart.sh) runs the same pipeline steps; for its API checks it searches for the first company in the published data instead of a fixed name. The [`.github/workflows/quickstart.yml`](.github/workflows/quickstart.yml) workflow runs the script on pull requests into `develop` and `main`, so if you change the steps here, change the script too.

```sh
cd openlobbying
uv sync                                   # macOS: export PKG_CONFIG_PATH first (see above)
scripts/quickstart.sh                     # or follow the steps below by hand
```

By hand:

```sh
export MUCKRAKE_DATABASE_URL=sqlite:///data/muckrake.db              # working DB (the default)
export MUCKRAKE_PUBLISHED_DATABASE_URL=sqlite:///data/published.db   # serving DB; must be separate
mkdir -p data

uv run muckrake list                      # the datasets in datasets/
uv run muckrake -v crawl gb_firs          # a small dataset: a few seconds, ~190 statements
uv run muckrake -v load gb_firs
uv run muckrake release-build gb_firs     # prints "Built release N" (an ingest)
uv run muckrake -v release-publish N      # copies ingest N into the published DB

uv run openlobbying server --port 8000
curl 'http://127.0.0.1:8000/search?q=FGS'
curl 'http://127.0.0.1:8000/profile/GB-COH-02956243'
```

Notes:

- Without `-v`, `crawl` and `load` print nothing on success.
- `release-build` with no dataset names builds from **every** dataset and fails unless each one has a successful crawl, so name the datasets you crawled.
- `release-publish` refuses to run when the published DB is the working DB.
- The API reads the published DB. The `/admin/*` dedupe routes also read and write the working DB.
- Some datasets are large: `gb_gov_transparency` downloads about 11,000 files and a full crawl takes over ten minutes.

## Developing

Install Python dependencies with `uv sync`. Run the tests with `uv run pytest` (a cold first run takes about 90 seconds, mostly imports).

Install frontend dependencies with `npm ci`.

Start the API server:

```sh
uv run openlobbying server --reload            # 127.0.0.1:8000; --port/-p and --host/-h to change
```

The endpoints are listed in [`docs/api.md`](docs/api.md), which is generated from the app by `uv run python scripts/gen_api_docs.py` (a test fails when it is stale). With the server running, `/docs` serves the interactive OpenAPI version.

Start the Svelte development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

Frontend calls use relative `/api/*` routes. In local development, Vite proxies `/api` to `OPENLOBBYING_API_URL` (from your shell or `.env`), or `http://127.0.0.1:8000` by default.

**The frontend needs Postgres.** Better Auth stores accounts in the database at `MUCKRAKE_DATABASE_URL`, and this app connects to it with the Postgres driver (`pg`) only, so with the SQLite default every page returns a 500 (`MUCKRAKE_DATABASE_URL must be set to configure Better Auth`). The simplest local Postgres is muckrake's standalone stack: run `docker compose up -d db` in `../muckrake` (Postgres on port 5433 with `muckrake` and `muckrake_published` databases), then set the Postgres URLs shown in `.env.example`.

Local environment variables live in the repo-root `.env`. Use `.env.example` as the template: it explains the SQLite and Postgres setups. `muckrake` discovers this `.env` automatically when run from the OpenLobbying repo. Variables already set in your shell take precedence. muckrake (and so the API) skips the file when `ENVIRONMENT=production`; the Vite dev server reads it regardless.

## Datasets

OpenLobbying-specific crawlers live in `datasets/`; see [`datasets/AGENTS.md`](datasets/AGENTS.md) for how to write one.

```sh
uv run muckrake list
uv run muckrake crawl gb_committees
uv run muckrake load gb_committees
```

A full pipeline run also uses NER extraction, deduplication and releases. LLM extraction results are paid for and committed in `ner/`, so restore them before extracting anything new (see [`ner/README.md`](ner/README.md)):

```sh
uv run muckrake ner-import ner/candidates.jsonl.gz
uv run muckrake ner-extract <dataset> --extractor llm
uv run muckrake xref                      # LevelDB: Linux or Docker (see Prerequisites)
uv run muckrake dedupe                    # review TUI; the web review is at /admin/dedupe
uv run muckrake release-build <dataset>...
uv run muckrake release-publish <id>
```

See the [muckrake README](https://github.com/openlobbying/muckrake#readme) for the full command reference.

## Authentication

This app uses Better Auth for email/password login.

- Auth tables are created automatically in the database pointed to by `MUCKRAKE_DATABASE_URL`, which must be Postgres.
- Better Auth uses `BETTER_AUTH_SECRET` and `BETTER_AUTH_URL`.
- Admin API calls use `OPENLOBBYING_ADMIN_API_SECRET` if set, otherwise they fall back to `BETTER_AUTH_SECRET`.
- Set `BETTER_AUTH_SECRET` in production. In development only, the app falls back to a fixed local secret.
- Better Auth runs on `/auth/*` so it does not clash with the existing `/api/*` FastAPI proxy in development.
- Better Auth's admin plugin is enabled, and the admin panel lives at `/admin`.
- Admin access is role-based using Better Auth's built-in `user` and `admin` roles.
- Admins can be promoted or demoted from `/admin`.
- The login page is at `/login`.
- `/account` is a page that requires login.

## Building

Build the frontend for production:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

## Deployment notes

- This app uses `@sveltejs/adapter-node`.
- Production runtime command is `node build`.
- In production we expect a reverse proxy (Caddy/Nginx) in front of the Node process.
- Production env comes from `/etc/openlobbying/app.env`.
- The app serves a runtime sitemap index at `/sitemap.xml`, with profile sitemap shards backed by the FastAPI API.

See `ops/README.md` for the deployment runbook and `ops/` for service templates and proxy config used by this project.
