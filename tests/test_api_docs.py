import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_api_docs_are_current(tmp_path: Path) -> None:
    # Fresh interpreter, as in test_api_server.py: conftest's `import muckrake` has
    # already applied FTM_MODEL_PATH and the database settings to this one.
    db_url = f"sqlite:///{tmp_path / 'published.db'}"
    env = {
        **{k: v for k, v in os.environ.items() if k != "FTM_MODEL_PATH"},
        "MUCKRAKE_DATABASE_URL": db_url,
        "MUCKRAKE_PUBLISHED_DATABASE_URL": db_url,
    }
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gen_api_docs.py"), "--check"],
        env=env,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
