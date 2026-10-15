"""Common entity creation functions for Electoral Commission data."""

import csv
from functools import reduce
from pathlib import Path

from followthemoney import model
from followthemoney.exc import InvalidData
from muckrake.utils import normalize_gb_coh


def donor_schema_for_status(donor_status: str | None) -> str:
    if donor_status == "Individual":
        return "Person"
    if donor_status in ("Company", "Limited Liability Partnership"):
        return "Company"
    if donor_status in (
        "Registered Political Party",
        "Unincorporated Association",
        "Trade Union",
        "Trust",
        "Friendly Society",
    ):
        return "Organization"
    if donor_status == "Public Fund":
        return "PublicBody"
    return "LegalEntity"


def donor_schema_overrides(sources: list[tuple[Path, str, str]]) -> dict[str, str]:
    """Map donor ids whose rows imply FtM-incompatible schemata to LegalEntity.

    The EC registers sometimes type the same donor inconsistently across rows
    (e.g. a company recorded as "Individual" on some donations). Emitting both
    Person and Organization statements under one entity id poisons the store —
    assembly crashes stages later with "No common schema" (openlobbying#30).
    Pre-scan the CSVs and, where the mapped schemata cannot merge, fall back
    to their common ancestor. Sources are (path, id_field, status_field).
    """
    schemata_by_donor: dict[str, set[str]] = {}
    for path, id_field, status_field in sources:
        with open(path, encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                donor_id = row.get(id_field)
                if not donor_id:
                    continue
                schema = donor_schema_for_status(row.get(status_field))
                schemata_by_donor.setdefault(donor_id, set()).add(schema)

    overrides: dict[str, str] = {}
    for donor_id, names in schemata_by_donor.items():
        if len(names) < 2:
            continue
        schemata = [model.get(name) for name in sorted(names)]
        try:
            reduce(model.common_schema, schemata)
        except InvalidData:
            overrides[donor_id] = "LegalEntity"
    return overrides


def make_donor(
    dataset,
    donor_id: str | None,
    donor_name: str | None,
    donor_status: str | None,
    donor_reg_nr: str | None,
    donor_postcode: str | None,
    register_name: str | None,
    schema_override: str | None = None,
):
    """Create a donor/lender entity with proper schema and properties."""
    # Apply manual corrections from datapatch lookups
    if donor_name:
        result = dataset.lookup("donor_reg_nr", donor_name)
        if result is not None:
            donor_reg_nr = result.value

    donor_schema = schema_override or donor_schema_for_status(donor_status)

    donor = dataset.make(donor_schema)
    # donor.id = dataset.make_id('donor', donor_id or donor_name)
    if donor_reg_nr:
        donor_reg_nr = normalize_gb_coh(donor_reg_nr)

    donor.id = dataset.make_id("donor", donor_id, reg_nr=donor_reg_nr, register="GB-COH")

    if donor_reg_nr:
        donor.add("registrationNumber", f"GB-COH-{normalize_gb_coh(donor_reg_nr)}")

    donor.add("name", donor_name)
    donor.add("address", donor_postcode)

    if donor_status:
        if donor_status == "Registered Political Party":
            donor.add("topics", "pol.party")
        elif donor_status == "Public Fund":
            donor.add("topics", "gov")
        elif donor_status == "Trade Union":
            donor.add("topics", "pol.union")
        elif donor_status in (
            "Limited Liability Partnership",
            "Unincorporated Association",
            "Friendly Society",
            "Trust",
        ):
            donor.add("legalForm", donor_status)

    if register_name == "Great Britain":
        donor.add("jurisdiction", "gb")
    elif register_name == "Northern Ireland":
        donor.add("jurisdiction", "gb-nir")

    return donor


# Regulated donee types that are always an individual holding an office or role.
PERSON_DONEE_TYPES = {
    "MP - Member of Parliament",
    "MSP - Member of the Scottish Parliament",
    "MEP - Member of the European Parliament",
    "AM - Member of the National Assembly for Wales",
    "GLA - Assembly Member (Greater London)",
    "MLA - Member of the Legislative Authority of Northern Ireland",
    "Senedd Member",
    "Cllr. - Member of a Local Authority",
    "Mayor",
    "Police and Crime Commissioner",
    "Member of Registered Political Party",
    "Leadership Candidate",
    "Candidate",
}


def recipient_schema(recipient_type: str | None, donee_type: str | None) -> str:
    """The FtM schema for a regulated entity, from what the EC row tells us about it.

    When the row doesn't say whether the recipient is a person or an organisation
    (third parties, permitted participants, and loans, which carry no donee type),
    use LegalEntity: it merges with whichever specific schema another row supplies,
    rather than guessing Person and colliding with Organization.
    """
    if recipient_type == "Political Party" or donee_type == "Members Association":
        return "Organization"
    if donee_type in PERSON_DONEE_TYPES:
        return "Person"
    if donee_type:
        raise ValueError(f"Unknown EC regulated donee type: {donee_type!r}")
    return "LegalEntity"


def create_recipient_entity(
    dataset,
    recipient_id: str | None,
    recipient_name: str | None,
    recipient_type: str | None,
    recipient_donnee_type: str | None,
    register_name: str | None,
):
    """Create a recipient entity (political party or other regulated entity)."""
    recipient = dataset.make(recipient_schema(recipient_type, recipient_donnee_type))
    recipient.id = dataset.make_id("recipient", recipient_id)
    recipient.add("name", recipient_name)

    if recipient_type == "Political Party":
        recipient.add("topics", "pol.party")

    if recipient_donnee_type in (
        "MSP - Member of the Scottish Parliament",
        "MP - Member of Parliament",
        "Senedd Member",
        "Cllr. - Member of a Local Authority",
        "MLA - Member of the Legislative Authority of Northern Ireland",
    ):
        recipient.add("topics", "role.pep")

    if recipient_donnee_type == "MSP - Member of the Scottish Parliament":
        recipient.add("jurisdiction", "gb-sct")
    elif recipient_donnee_type == "Senedd Member":
        recipient.add("jurisdiction", "gb-wls")
    elif recipient_donnee_type == "MLA - Member of the Legislative Authority of Northern Ireland":
        recipient.add("jurisdiction", "gb-nir")
    elif recipient_donnee_type in (
        "MP - Member of Parliament",
        "Cllr. - Member of a Local Authority",
    ):
        recipient.add("jurisdiction", "gb")

    if register_name == "Great Britain":
        recipient.add("jurisdiction", "gb")
    elif register_name == "Northern Ireland":
        recipient.add("jurisdiction", "gb-nir")

    return recipient
