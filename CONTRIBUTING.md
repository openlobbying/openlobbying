# Contributing to openlobbying

Setup is in the [README](README.md): Prerequisites, then Quickstart.

## Branches and releases

- `develop` is the default branch and where work is integrated. Branch from `develop` and open pull requests into `develop`. Name branches `<type>/<short-name>`, with types `feature/`, `fix/`, `perf/`, `test/`, `ci/`, `docs/`, `data/` (a new or changed crawler) and `release/`.
- `main` is protected and only changes through pull requests. It holds released checkpoints.
- A release is a pull request from `develop` into `main`, merged with a merge commit (not squashed). muckrake is released first, since this repo depends on it, and `main` always pins a muckrake release (see [muckrake](#muckrake)).
- Hotfixes are not used while the current production site is frozen: fixes go through `develop`. Once the replacement is live, hotfixes branch from `main`, merge into `main`, and are then merged back into `develop`.

## muckrake

This repo installs a muckrake release pinned in `pyproject.toml`:

```toml
dependencies = [
    "muckrake==0.5.1",
]
```

`uv.lock` records the release with its file hashes, so `uv sync --locked` installs exactly that release in CI and on every machine.

### Framework and project development

| Mode | What you're changing | Where muckrake comes from | Run commands with |
|---|---|---|---|
| Project development | This repo only | The pinned release | `uv run <command>` |
| Framework development | muckrake, usually alongside this repo | Your local `../muckrake` checkout | `uv run --with-editable ../muckrake <command>` |

Only framework development uses your local muckrake. CI, staging and ingests use the pinned release.

For framework development, clone muckrake next to this repo and run commands from this repo:

```sh
uv run --with-editable ../muckrake pytest
uv run --with-editable ../muckrake muckrake crawl gb_prca
```

Edits in `../muckrake` apply on the next command. `pyproject.toml` and `uv.lock` don't change, so there is nothing to undo: a plain `uv run` uses the pinned release again. An alias saves typing, for example `alias uvf='uv run --with-editable ../muckrake'`. `uv sync` and your editor's interpreter still see the pinned release.

The umbrella stack in undertheinfluence has a runner for each mode:

```sh
docker compose run --build --rm openlobbying <command>   # project development: the pinned release
docker compose run --build --rm muckrake <command>       # framework development: your local ../muckrake
```

`openlobbying` is built from this repo's `Dockerfile.pipeline`, which installs `uv.lock`. `muckrake` is built from `../muckrake`. `--build` picks up a changed lock or changed muckrake source, and is quick when nothing changed.

### Releasing a change that spans both repos

Framework first, then project:

1. Merge the muckrake change into muckrake's `develop` and release it, as in [muckrake's CONTRIBUTING](https://github.com/openlobbying/muckrake/blob/develop/CONTRIBUTING.md#releases).
2. In this repo, open a pull request that bumps the pin and includes the changes that use it. Set `muckrake==X.Y.Z` in `pyproject.toml`, run `uv lock`, and link the muckrake changelog entry in the pull request.

This repo's pull request can't merge first: CI installs the pinned release, which doesn't have the muckrake change yet.

To use a merged muckrake change on `develop` before it's released, pin the commit and run `uv lock`:

```toml
[tool.uv.sources]
muckrake = { git = "https://github.com/openlobbying/muckrake", rev = "<full commit SHA>" }
```

While the override is in place, uv installs that commit and ignores the `muckrake==` version. Replace the override with a release before `develop` is released to `main`: `main` always pins a muckrake release.

### Moving from the `../muckrake` checkout

Until 26 November 2026, this repo installed muckrake from `../muckrake` as an editable path dependency ([Pin muckrake to a PyPI release instead of the ../muckrake checkout](https://github.com/openlobbying/openlobbying/issues/75)).

| | Before | After |
|---|---|---|
| Where muckrake comes from | The `../muckrake` checkout, on whatever branch it was | The release pinned in `pyproject.toml` |
| How a muckrake change reaches this repo | Straight away | Through a pull request that bumps the pin |
| CI | Checked out the muckrake branch matching the pull request's target | Installs the pinned release |
| The `../muckrake` checkout | Required | Only for framework development |

To move an existing checkout:

1. Pull `develop`.
2. Run `uv sync`. It replaces the editable muckrake with the pinned release.
3. For framework development, run commands with `uv run --with-editable ../muckrake`.

Real pipeline runs in the umbrella stack move from the `muckrake` service to the new `openlobbying` service ([Build the umbrella pipeline runner from openlobbying's lock (pinned muckrake)](https://github.com/openlobbying/undertheinfluence/issues/11)). Not changed: `ops/deploy_to_vps.sh`, which still copies `../muckrake` to the server. The current production site is frozen, so the script is left as it is.

## In this repo

- Before pushing:
  - `uv run pytest` (crawler tests live in `tests/`)
  - `uv run ruff check .`, `uv run ruff format --check .` and `uv run mypy src datasets tests scripts` (or `uv run pre-commit install` once, so ruff runs on each commit)
  - `npm run check` for any frontend change
  - `uv run python scripts/gen_api_docs.py` if you changed an API route (a test fails when `docs/api.md` is stale)
  - keep the README Quickstart and `scripts/quickstart.sh` in step; the Quickstart workflow runs the script on pull requests into `develop` and `main`
- **Crawlers** follow the contract in [`datasets/AGENTS.md`](datasets/AGENTS.md): stable IDs via `dataset.make_id`, fetch through `dataset.fetch_*`, never emit a guessed value. Some datasets have their own `AGENTS.md`; read it before changing them.
- **FtM schema extensions** live in `ftm_schema_ext/`. Anything using FtM must `import muckrake` first.
- **Deploying:** the current production site is frozen while its replacement is built, so don't run `ops/deploy_to_vps.sh`. For reference, that script copies your working tree (not a branch or tag) to the server. See [`ops/README.md`](ops/README.md).
