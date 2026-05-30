## OpenLobbying

OpenLobbying is a mixed Python + Svelte application repo built on top of the reusable `../muckrake` core.

This repo owns:

- the OpenLobbying dataset crawlers under `datasets/`
- the OpenLobbying FastAPI app under `src/openlobbying/api/`
- the Svelte frontend under `src/`
- deployment assets under `ops/`

## Developing

Install Python dependencies with `uv sync`.

Install frontend dependencies with `npm install`.

Start the API server:

```sh
uv run openlobbying server --reload
```

Start the Svelte development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

Frontend calls use relative `/api/*` routes. In local development, Vite proxies `/api` to `OPENLOBBYING_API_URL` or `http://127.0.0.1:8000` by default.

Local environment variables live in the repo-root `.env`.

Use `.env.example` as the template. `muckrake` will also discover this `.env` automatically when run from the OpenLobbying repo.

## Datasets

OpenLobbying-specific crawlers live in `datasets/`.

Examples:

```sh
uv run muckrake list
uv run muckrake crawl gb_gov_transparency
uv run muckrake load gb_gov_transparency
```

## Authentication

This app uses Better Auth for email/password login.

- Auth tables are created automatically in the database pointed to by `MUCKRAKE_DATABASE_URL`.
- Better Auth uses `BETTER_AUTH_SECRET` and `BETTER_AUTH_URL`.
- Admin API calls use `OPENLOBBYING_ADMIN_API_SECRET` if set, otherwise they fall back to `BETTER_AUTH_SECRET`.
- Set `BETTER_AUTH_SECRET` in production. In development only, the app falls back to a fixed local secret.
- Better Auth runs on `/auth/*` so it does not clash with the existing `/api/*` FastAPI proxy in development.
- Better Auth's admin plugin is enabled, and the admin panel lives at `/admin`.
- Admin access is role-based using Better Auth's built-in `user` and `admin` roles.
- Admins can be promoted or demoted from `/admin`.
- The login page is at `/login`.
- The protected example page is at `/account`.

## Building

To create a production version of your app:

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
