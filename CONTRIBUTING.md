# Contributing to openlobbying

Setup is in the [README](README.md): Prerequisites, then Quickstart.

## Branches and releases

- `develop` is the default branch and where work is integrated. Branch from `develop` and open pull requests into `develop`. Name branches `<type>/<short-name>`, with types `feature/`, `fix/`, `perf/`, `test/`, `ci/`, `docs/`, `data/` (a new or changed crawler) and `release/`.
- `main` is protected and only changes through pull requests. It holds released checkpoints.
- A release is a pull request from `develop` into `main`, merged with a merge commit (not squashed). muckrake is released first, since this repo depends on it.
- Hotfixes are not used while the current production site is frozen: fixes go through `develop`. Once the replacement is live, hotfixes branch from `main`, merge into `main`, and are then merged back into `develop`.

## In this repo

- This repo runs muckrake from `../muckrake`. Keep that checkout on the matching branch: `develop` for dev work, `main` for a release. CI checks out the muckrake branch with the same name as your PR's target.
- Before pushing:
  - `uv run pytest` (crawler tests live in `tests/`)
  - `uv run ruff check .`, `uv run ruff format --check .` and `uv run mypy src datasets tests scripts` (or `uv run pre-commit install` once, so ruff runs on each commit)
  - `npm run check` for any frontend change
  - `uv run python scripts/gen_api_docs.py` if you changed an API route (a test fails when `docs/api.md` is stale)
  - keep the README Quickstart and `scripts/quickstart.sh` in step; the Quickstart workflow runs the script on pull requests into `develop` and `main`
- **Crawlers** follow the contract in [`datasets/AGENTS.md`](datasets/AGENTS.md): stable IDs via `dataset.make_id`, fetch through `dataset.fetch_*`, never emit a guessed value. Some datasets have their own `AGENTS.md`; read it before changing them.
- **FtM schema extensions** live in `ftm_schema_ext/`. Anything using FtM must `import muckrake` first.
- **Deploying:** the current production site is frozen while its replacement is built, so don't run `ops/deploy_to_vps.sh`. For reference, that script copies your working tree (not a branch or tag) to the server. See [`ops/README.md`](ops/README.md).
