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


def test_admin_dedupe_judgements_record_openlobbying_user_prefix(tmp_path: Path) -> None:
    # Judgements made in the admin UI are stored as `openlobbying:<user_id>[:name]`.
    _run(
        "from fastapi.testclient import TestClient\n"
        "from openlobbying.api import server\n"
        "calls = []\n"
        "def record(*args, **kwargs):\n"
        "    calls.append(kwargs)\n"
        "    return 'canonical'\n"
        "server.record_dedupe_judgement = record\n"
        "server.record_dedupe_cluster_judgement = record\n"
        "client = TestClient(server.app)\n"
        "headers = {'X-Admin-Secret': server.get_admin_api_secret()}\n"
        "r = client.post('/admin/dedupe/judge', headers=headers, json={\n"
        "    'left_id': 'a', 'right_id': 'b', 'judgement': 'positive', 'user_id': 'u1'})\n"
        "assert r.status_code == 200, r.text\n"
        "r = client.post('/admin/dedupe-clusters/judge', headers=headers, json={\n"
        "    'entity_ids': ['a', 'b'], 'selected_ids': ['a', 'b'],\n"
        "    'locked_pairs': [{'left_id': 'a', 'right_id': 'b'}],\n"
        "    'intent': 'match', 'user_id': 'u1'})\n"
        "assert r.status_code == 200, r.text\n"
        "assert [c['user_prefix'] for c in calls] == ['openlobbying', 'openlobbying'], calls\n",
        tmp_path,
    )
