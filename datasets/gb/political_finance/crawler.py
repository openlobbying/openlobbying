"""
UK Electoral Commission political donations and loans crawler.

This module serves as the entry point for crawling both donations
and loans data from the Electoral Commission.
"""
from .common import donor_schema_overrides
from .donations import fetch_donations, process_donations
from .loans import fetch_loans, process_loans

# TODO: Probably worth splitting into two datasets

def crawl(dataset):
    """Main crawler entry point - crawls both donations and loans."""
    donations_path = fetch_donations(dataset)
    loans_path = fetch_loans(dataset)

    # The EC sometimes types the same donor inconsistently across rows; where
    # the implied FtM schemata cannot merge, emit the donor as LegalEntity so
    # one entity id never carries incompatible schemata (openlobbying#30).
    schema_overrides = donor_schema_overrides([
        (donations_path, "DonorId", "DonorStatus"),
        (loans_path, "LoanParticipantId", "LoanParticipantType"),
    ])
    if schema_overrides:
        dataset.log.warning(
            f"{len(schema_overrides)} donor(s) with conflicting EC status types; emitting as LegalEntity"
        )

    process_donations(dataset, donations_path, schema_overrides)
    process_loans(dataset, loans_path, schema_overrides)
