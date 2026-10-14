import os
import subprocess
import sys
from pathlib import Path

# Each check runs in a fresh interpreter, without the FTM_MODEL_PATH and database
# settings conftest's `import muckrake` has already applied to this one.


def _run(code: str, tmp_path: Path) -> None:
    db_url = f"sqlite:///{tmp_path / 'published.db'}"
    env = {
        **{k: v for k, v in os.environ.items() if k != "FTM_MODEL_PATH"},
        "MUCKRAKE_DATABASE_URL": db_url,
        "MUCKRAKE_PUBLISHED_DATABASE_URL": db_url,
    }
    subprocess.run([sys.executable, "-c", code], env=env, check=True)


def test_server_loads_ftm_schema_extensions(tmp_path: Path) -> None:
    _run(
        "from openlobbying.api import server\n"
        "from followthemoney import model\n"
        "assert model.get('Donation') is not None\n",
        tmp_path,
    )


def test_profile_activities_sql_pagination(tmp_path: Path) -> None:
    _run(
        "from openlobbying.api import server\n"
        "page = server._paginate_profile_activities_sql('missing', 10, 0)\n"
        "assert page['total'] == 0 and page['results'] == []\n",
        tmp_path,
    )
