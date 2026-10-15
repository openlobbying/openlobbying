# OpenLobbying API reference

Generated from the FastAPI app by `scripts/gen_api_docs.py`; don't edit by hand.
Run the API with `uv run openlobbying server` and open `/docs` for the interactive
OpenAPI version with parameters and response shapes.

The API reads the published database (`MUCKRAKE_PUBLISHED_DATABASE_URL`). The
`/admin/*` routes are the exception: they need the `X-Admin-Secret` header and read
and write dedupe judgements in the **working** database (`MUCKRAKE_DATABASE_URL`).

| Method | Path | Summary |
|---|---|---|
| GET | `/` | Root |
| GET | `/datasets` | List all available datasets with metadata. |
| GET | `/admin/dedupe/next` | Get admin dedupe candidate |
| POST | `/admin/dedupe/judge` | Judge admin dedupe candidate |
| GET | `/admin/dedupe-clusters/next` | Get admin dedupe cluster |
| POST | `/admin/dedupe-clusters/judge` | Judge admin dedupe cluster |
| GET | `/entities` | List entities |
| GET | `/profile/{id}` | Endpoint for actor profiles, includes adjacency (timeline). |
| GET | `/profile/{id}/activities` | Get profile activities |
| GET | `/sitemaps/profiles` | List actor profile paths for sitemap generation. |
| GET | `/statement/{id}` | Endpoint for statements/events, simple view. |
| GET | `/search` | Search entities |
| GET | `/stats` | Get stats |
| GET | `/entities/{id}/graph` | Get aggregated 1st-degree connections for graph visualization. |
