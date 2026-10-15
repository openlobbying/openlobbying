# Electoral Commission donations and loans

The UK Electoral Commission publishes a [searchable database](https://search.electoralcommission.org.uk/) of donations and loans to political parties, regulated individuals and campaign groups. The crawler downloads the donations and loans CSV exports (`api/csv/Donations` and `api/csv/Loans`) with `dataset.fetch_resource`, and maps both with the same donor and recipient rules (`common.py`). `spending.py` exists but is not called.

## To do

- [ ] Incorporate [these deduplications](https://donation.watch/en/unitedkingdom/transparency#sec-aggregated-donors)

## Recipients

The recipient is the regulated entity (`RegulatedEntityId`, `RegulatedEntityName`). Its schema comes from `recipient_schema`:

- `Organization` when `RegulatedEntityType` is "Political Party" or `RegulatedDoneeType` is "Members Association".
- `Person` when `RegulatedDoneeType` is an individual's role: MP, MSP, MEP, Welsh Assembly or Senedd Member, London Assembly Member, MLA, councillor, mayor, Police and Crime Commissioner, party member, leadership candidate or candidate (`PERSON_DONEE_TYPES`).
- `LegalEntity` when the row has no `RegulatedDoneeType` (third parties, permitted participants and all loans). It merges with the specific schema another row supplies.
- Any other `RegulatedDoneeType` raises an error.

Properties:

- `Thing:name` → `RegulatedEntityName`
- `Thing:topics` → "pol.party" for political parties; "role.pep" for MPs, MSPs, Senedd Members, councillors and MLAs
- `LegalEntity:jurisdiction` → from `RegulatedDoneeType` ("gb-sct" for MSPs, "gb-wls" for Senedd Members, "gb-nir" for MLAs, "gb" for MPs and councillors) and from `RegisterName` ("gb" for Great Britain, "gb-nir" for Northern Ireland). A recipient can carry both values.

## Donors and lenders

The donor (`DonorId`, `DonorStatus`) or lender (`LoanParticipantId`, `LoanParticipantType`) schema comes from `donor_schema_for_status`:

| Status | Schema |
|---|---|
| Individual | `Person` |
| Company, Limited Liability Partnership | `Company` |
| Registered Political Party, Unincorporated Association, Trade Union, Trust, Friendly Society | `Organization` |
| Public Fund | `PublicBody` |
| anything else | `LegalEntity` |

The Commission sometimes gives one donor different statuses on different rows. When those statuses map to schemata that can't merge, the donor is emitted as `LegalEntity` (`donor_schema_overrides`).

Properties:

- `Thing:name` → `DonorName` or `LoanParticipantName`
- `Thing:address` → `Postcode`
- `LegalEntity:registrationNumber` → `CompanyRegistrationNumber`, as `GB-COH-<number>`. It also makes the ID an org-id. The `donor_reg_nr` lookup in `config.yml` supplies missing numbers by donor name.
- `Thing:topics` → "pol.party" (Registered Political Party), "gov" (Public Fund), "pol.union" (Trade Union)
- `LegalEntity:legalForm` → the status, for Limited Liability Partnership, Unincorporated Association, Friendly Society and Trust
- `LegalEntity:jurisdiction` → "gb" or "gb-nir" from `RegisterName`

## Donations

Each donation row becomes a `Donation`, an OpenLobbying schema extension of `Payment` (`ftm_schema_ext/Donation.yaml`):

- `Payment:payer` → the donor
- `Payment:beneficiary` → the recipient
- `Interval:recordId` → `ECRef`
- `Interval:date` → `AcceptedDate`
- `Value:amount` → `Value`
- `Value:currency` → "GBP"
- `Payment:programme` → "Donation"
- `Thing:summary` → `DonationType`
- `Payment:purpose` → `NatureOfDonation`, or `PurposeOfVisit` when there is no nature
- `Thing:description` → "Purpose of Visit: … | Nature of Donation: …", from whichever of the two are present
- `Thing:sourceUrl` → `https://search.electoralcommission.org.uk/English/Donations/{ECRef}`

## Loans

Each loan row becomes a `Payment`:

- `Payment:payer` → the lender
- `Payment:beneficiary` → the recipient
- `Interval:recordId` → `ECRef`
- `Interval:date` → `StartDate`
- `Value:amount` → `Value`
- `Value:currency` → "GBP"
- `Payment:programme` → "Loan"
- `Thing:summary` → "Political Loan", followed by `LoanStatus` in brackets when present
- `Payment:purpose` → `LoanType`
- `Thing:description` → "Type: … | Interest: … | Repaid: £… | Converted: £… | Outstanding: £… | End date: …", from `LoanType`, `RateOfInterestDescription`, `AmountRepaid`, `AmountConverted`, `AmountOutstanding` and `EndDate` where present
- `Thing:sourceUrl` → `https://search.electoralcommission.org.uk/English/Loans/{ECRef}`
