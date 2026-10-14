import importlib.util
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "muckrake.crawler.gb.political_finance.common",
    Path("datasets/gb/political_finance/common.py"),
)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
COMMON.__package__ = "muckrake.crawler.gb.political_finance"
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


@pytest.mark.parametrize(
    ("recipient_type", "donee_type", "schema"),
    [
        ("Political Party", "", "Organization"),
        ("Regulated Donee", "Members Association", "Organization"),
        ("Regulated Donee", "MP - Member of Parliament", "Person"),
        ("Regulated Donee", "Mayor", "Person"),
        ("Third Party", "", "LegalEntity"),
        ("Permitted Participant", "", "LegalEntity"),
        # Loans carry no donee type: a Regulated Donee there may be a members
        # association (e.g. Labour Tomorrow Ltd), so it must not be guessed as Person.
        ("Regulated Donee", None, "LegalEntity"),
    ],
)
def test_recipient_schema(recipient_type, donee_type, schema):
    assert COMMON.recipient_schema(recipient_type, donee_type) == schema


def test_unknown_donee_type_raises():
    with pytest.raises(ValueError, match="Unknown EC regulated donee type"):
        COMMON.recipient_schema("Regulated Donee", "Galactic Emperor")
