# Office of the Registrar of Consultant Lobbyists (ORCL)

The Office of the Registrar of Consultant Lobbyists maintains a [searchable register](https://orcl.my.site.com/CLR_Search) of consultant lobbyists and their clients. This includes details about lobbyists such as addresses and contact details, as well as lists of clients for each quarter. When searching for clients, it shows the hired lobbyist for each quarter.

Implementation details for the Salesforce/AJAX scraper are documented in [`AGENTS.md`](AGENTS.md).

This register excludes [in-house lobbyists](https://publications.parliament.uk/pa/cm201314/cmselect/cmpolcon/601/60103.htm), [foreign lobbyists that don’t have a UK VAT registration](https://www.spotlightcorruption.org/vat-exemption-lobbying-transparency/), the [lobbying of senior civil servants and special advisers](https://publications.parliament.uk/pa/cm201314/cmselect/cmpolcon/601/60103.htm), and [lobbying done over WhatsApp](https://publications.parliament.uk/pa/cm5804/cmselect/cmpubadm/203/summary.html) or other “non-corporate communication channels.”

## Mapping

For each lobbying firm, create a [`LegalEntity`](https://followthemoney.tech/explorer/schemata/LegalEntity/) with:

- `name` set to the firm's name.
- `address` set to the firm's address, when the profile gives one.
- `registrationNumber` set to the firm's company number as `GB-COH-<number>`, when the profile gives one. The company number also makes the ID an org-id (`make_id(..., reg_nr=..., register="GB-COH")`); without one the ID is a hash of the name.
- `jurisdiction` set to "gb", `topics` set to "role.lobby" and `sourceUrl` set to the ORCL profile page.

For each client, create a [`LegalEntity`](https://followthemoney.tech/explorer/schemata/LegalEntity/) with `name` set to the client's name and `jurisdiction` set to "gb".

Then, for each client in each quarter, create a [`Representation`](https://followthemoney.tech/explorer/schemata/Representation/) entity, with:

- `Representation:agent` → the lobbying firm
- `Representation:client` → the client
- `Interest:role` → "Lobbyist"
- `Interval:startDate` → the start month of the quarter
- `Interval:endDate` → the end month of the quarter
- `Thing:sourceUrl` → the ORCL profile page

## To do

- [ ] Add breaches: [Suspensions of Dannatt and Evans reveal persistent vulnerabilities in Britains' defence-linked Parliamentary lobbying - AOAV](https://aoav.org.uk/2025/suspensions-of-dannatt-and-evans-reveal-persistent-vulnerabilities-in-defence-linked-lobbying/)
