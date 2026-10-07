# Contributing to openlobbying

Read the shared guide first: [openlobbying/docs CONTRIBUTING.md](https://github.com/openlobbying/docs/blob/main/CONTRIBUTING.md). It covers the repos, branching (`develop` → `main`), releases and environments.

## In this repo

- Branch from `develop` and open PRs into `develop`. Use `dataset/<name>` branches for crawler work.
- This repo runs muckrake from `../muckrake`. Keep that checkout on the same branch: `develop` for dev work, `main` for production.
- Before pushing:
  - `uv run pytest` (crawler tests live in `tests/`)
  - `npm run check` for any frontend change
- **Crawlers** follow the contract in [`datasets/AGENTS.md`](datasets/AGENTS.md): stable IDs via `dataset.make_id`, fetch through `dataset.fetch_*`, never emit a guessed value. Some datasets have their own `AGENTS.md`; read it before changing them.
- **FtM schema extensions** live in `ftm_schema_ext/`. Anything using FtM must `import muckrake` first.
- **Deploying:** `ops/deploy_to_vps.sh` copies your working tree, so check out `main` in both this repo and `../muckrake` before deploying production. See [`ops/README.md`](ops/README.md).
