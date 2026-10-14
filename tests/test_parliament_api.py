import importlib.util
import logging
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("parliament_util", Path("datasets/gb/parliament/util.py"))
assert SPEC is not None and SPEC.loader is not None
UTIL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UTIL)

URL = "https://example.parliament.uk/api/Things"


class PagedDataset:
    """Serves skip/take pages from a fixed list of items, as the Parliament APIs do."""

    def __init__(self, items, total, short_after=None):
        self.items = items
        self.total = total
        self.short_after = short_after  # stop returning items from this skip on
        self.incomplete = []
        self.log = logging.getLogger("test_parliament_api")

    def fetch_json(self, url, params, cache_days):
        skip, take = params["skip"], params["take"]
        if self.short_after is not None and skip >= self.short_after:
            return {"items": [], "totalResults": self.total}
        return {"items": self.items[skip : skip + take], "totalResults": self.total}

    def warn_incomplete(self, reason, **context):
        self.incomplete.append({"reason": reason, **context})


def test_iter_api_items_pages_through_everything():
    dataset = PagedDataset(list(range(7)), total=7)
    assert list(UTIL.iter_api_items(dataset, URL, {"skip": 0, "take": 3})) == list(range(7))
    assert dataset.incomplete == []


def test_iter_api_items_warns_when_pages_stop_early():
    dataset = PagedDataset(list(range(7)), total=7, short_after=3)
    assert list(UTIL.iter_api_items(dataset, URL, {"skip": 0, "take": 3})) == [0, 1, 2]
    assert dataset.incomplete == [
        {"reason": "fewer API items than totalResults", "url": URL, "received": 3, "total": 7}
    ]


def test_iter_api_items_does_not_mutate_params():
    params = {"skip": 0, "take": 3}
    list(UTIL.iter_api_items(PagedDataset(list(range(4)), total=4), URL, params))
    assert params == {"skip": 0, "take": 3}


class IdDataset:
    def make_id(self, *parts, reg_nr=None, register=None):
        return "-".join(str(p) for p in (*parts, reg_nr, register) if p)


def test_person_and_organization_with_same_name_get_different_ids():
    ds = IdDataset()
    person = UTIL.legal_entity_id(ds, "Person", "Results UK")
    org = UTIL.legal_entity_id(ds, "Organization", "Results UK")
    assert person != org
    assert org == UTIL.legal_entity_id(ds, "LegalEntity", "Results UK")
