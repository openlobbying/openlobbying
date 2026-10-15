# Foreign Influence Registration Scheme (FIRS)

The UK requires "the registration of arrangements to carry out political influence activities in the UK at the direction of a foreign power". [The public register](https://foreign-influence-registration-scheme.service.gov.uk/public-register) started in 2025 and has few entries.

It is the smallest dataset here (a few seconds to crawl, about 190 statements), which is why the README Quickstart uses it.

## Mapping

We create a [`Company`](https://followthemoney.tech/explorer/schemata/Company/) entity for each registrant, with:

- `Thing:name` → Registrant / Name
- `Thing:previousName` → Registrant / Previous names
- `Thing:country` → Registrant / Country or territory of incorporation or main office
- `LegalEntity:registrationNumber` → Registrant / Company registration number, as `GB-COH-<number>` (when present, it also makes the ID an org-id)
- `Thing:address` → Registrant / Registered or main address
- `Thing:topics` → "role.lobby"

For each arrangement, we create a [`PublicBody`](https://followthemoney.tech/explorer/schemata/PublicBody/) entity for the foreign power:

- `Thing:name` → Arrangement / Name of foreign power
- `Thing:country` → Arrangement / Country or territory of foreign power
- `Thing:topics` → "gov"

Then, we link them with a [`Representation`](https://followthemoney.tech/explorer/schemata/Representation/) entity, with:

- `Representation:agent` → the registrant (`Company`)
- `Representation:client` → the foreign power (`PublicBody`)
- `Interest:role` → "Lobbyist"
- `Interval:summary` → Activity overview / Aim
- `Interval:startDate` → Activity overview / Start date
- `Interval:endDate` → Activity overview / End date (if present)
- `Thing:sourceUrl` → the registration's URL

For [some entries](https://foreign-influence-registration-scheme.service.gov.uk/article/1200/Walk-Through-Walls-OTTG-Ltd), there is an additional "Organisations involved" section. For each organisation in it we create:

- a `Company` with `Thing:name` → Organisations involved / Name and `Thing:topics` → "role.lobby";
- a `Representation` between it and the foreign power, with the same role, dates and source URL as above;
- an [`UnknownLink`](https://followthemoney.tech/explorer/schemata/UnknownLink/) from the registrant (`subject`) to the organisation (`object`), with `role` "Consultant" and the same dates and source URL.
