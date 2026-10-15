"""Generate docs/api.md, the API endpoint reference, from the FastAPI app.

    uv run python scripts/gen_api_docs.py          # rewrite docs/api.md
    uv run python scripts/gen_api_docs.py --check  # exit 1 if docs/api.md is stale

tests/test_api_docs.py runs the check, so regenerate after changing a route.
"""

import sys
from pathlib import Path

import muckrake  # noqa: F401  (configures the FtM schema extensions first)
from fastapi.routing import APIRoute

from openlobbying.api.server import app

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "api.md"

HEADER = """# OpenLobbying API reference

Generated from the FastAPI app by `scripts/gen_api_docs.py`; don't edit by hand.
Run the API with `uv run openlobbying server` and open `/docs` for the interactive
OpenAPI version with parameters and response shapes.

The API reads the published database (`MUCKRAKE_PUBLISHED_DATABASE_URL`). The
`/admin/*` routes are the exception: they need the `X-Admin-Secret` header and read
and write dedupe judgements in the **working** database (`MUCKRAKE_DATABASE_URL`).

| Method | Path | Summary |
|---|---|---|
"""


def summary(route: APIRoute) -> str:
    doc = (route.endpoint.__doc__ or "").strip()
    if doc:
        return doc.splitlines()[0]
    return route.name.replace("_", " ").capitalize()


def render() -> str:
    rows = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in sorted(route.methods):
            rows.append(f"| {method} | `{route.path}` | {summary(route)} |")
    return HEADER + "\n".join(rows) + "\n"


def main() -> None:
    text = render()
    if "--check" in sys.argv[1:]:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            sys.exit(f"{OUTPUT} is stale: run `uv run python scripts/gen_api_docs.py`")
        return
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
