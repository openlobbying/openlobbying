import csv
import importlib.util
import sys
from pathlib import Path

COMMON_PATH = Path("datasets/gb/political_finance/common.py")
COMMON_SPEC = importlib.util.spec_from_file_location("political_finance_common", COMMON_PATH)
assert COMMON_SPEC is not None
assert COMMON_SPEC.loader is not None
COMMON = importlib.util.module_from_spec(COMMON_SPEC)
sys.modules[COMMON_SPEC.name] = COMMON
COMMON_SPEC.loader.exec_module(COMMON)

donor_schema_for_status = COMMON.donor_schema_for_status
donor_schema_overrides = COMMON.donor_schema_overrides


def write_csv(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["DonorId", "DonorStatus"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_status_schema_mapping():
    assert donor_schema_for_status("Individual") == "Person"
    assert donor_schema_for_status("Company") == "Company"
    assert donor_schema_for_status("Limited Liability Partnership") == "Company"
    assert donor_schema_for_status("Trade Union") == "Organization"
    assert donor_schema_for_status("Public Fund") == "PublicBody"
    assert donor_schema_for_status("Unidentifiable Donor") == "LegalEntity"
    assert donor_schema_for_status(None) == "LegalEntity"


def test_incompatible_statuses_get_legal_entity_override(tmp_path):
    # The openlobbying#30 case: a company recorded as Individual on some rows.
    path = write_csv(tmp_path / "donations.csv", [
        {"DonorId": "83", "DonorStatus": "Individual"},
        {"DonorId": "83", "DonorStatus": "Individual"},
        {"DonorId": "83", "DonorStatus": "Company"},
        {"DonorId": "99", "DonorStatus": "Individual"},
    ])
    overrides = donor_schema_overrides([(path, "DonorId", "DonorStatus")])
    assert overrides == {"83": "LegalEntity"}


def test_compatible_statuses_do_not_override(tmp_path):
    path = write_csv(tmp_path / "donations.csv", [
        # Company + LLP → both Company
        {"DonorId": "1", "DonorStatus": "Company"},
        {"DonorId": "1", "DonorStatus": "Limited Liability Partnership"},
        # Person + LegalEntity merge cleanly (ancestor/descendant)
        {"DonorId": "2", "DonorStatus": "Individual"},
        {"DonorId": "2", "DonorStatus": "Unidentifiable Donor"},
        # Company + Organization merge cleanly (Company extends Organization)
        {"DonorId": "3", "DonorStatus": "Company"},
        {"DonorId": "3", "DonorStatus": "Trade Union"},
    ])
    assert donor_schema_overrides([(path, "DonorId", "DonorStatus")]) == {}


def test_conflicts_detected_across_files(tmp_path):
    donations = write_csv(tmp_path / "donations.csv", [
        {"DonorId": "7", "DonorStatus": "Individual"},
    ])
    loans = write_csv(tmp_path / "loans.csv", [
        {"DonorId": "7", "DonorStatus": "Trade Union"},
    ])
    overrides = donor_schema_overrides([
        (donations, "DonorId", "DonorStatus"),
        (loans, "DonorId", "DonorStatus"),
    ])
    assert overrides == {"7": "LegalEntity"}
