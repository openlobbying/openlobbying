# Government Transparency returns

Government departments in the UK publish regular transparency returns covering ministers, special advisers, and senior officials. `config.yml` includes a list of these publications identified so far.

These returns mainly cover meetings with external organisations, gifts, hospitality, and travel. Some returns also cover receptions and outside employment.

## Collections not yet included

- [ ] [DHSC registers of board members' interests - GOV.UK](https://www.gov.uk/government/collections/dhsc-registers-of-board-members-interests) / [DWP register of board members’ interests - GOV.UK](https://www.gov.uk/government/collections/dwp-register-of-board-members-interests) / [Cabinet Office register of board members’ interests - GOV.UK](https://www.gov.uk/government/collections/cabinet-office-register-of-board-members-interests)
- [ ] [DESNZ: Ministerial gifts, hospitality, travel and meetings with external organisations - data.gov.uk](https://www.data.gov.uk/dataset/2673218b-0888-4617-a94e-9df90f75117f/ministerial-gifts-hospitality-travel-and-meetings-with-external-organisations)
- [ ] [Special advisers: gifts and hospitality - gov.scot](https://www.gov.scot/collections/special-advisers-gifts-and-hospitality/)
- [ ] [Register of Ministers’ Gifts and Hospitality - GOV.UK](https://www.gov.uk/government/collections/register-of-ministers-gifts-and-hospitality)

## File formats

The configured collections list about 11,000 source files (11,270 in the crawl of 15 Oct 2026). Downloaded attachments on disk on that date, by file extension:

| Extension | Files |
|---|---|
| `.csv` | 9,110 |
| `.pdf` | 1,442 |
| `.xlsx` | 305 |
| `.ods` | 163 |
| `.doc` | 85 |
| `.xls` | 60 |
| `.xlsm` | 27 |
| `.rtf` | 20 |
| `.odt` | 19 |
| `.docx`, `.xlt` | 3 |

HTML publications that contain tables are also sources; they are fetched as pages, not downloaded as files.

The crawler detects the format from the file's content before its extension (`normalise.py`). Files it can't read as a table, such as PDF and Word documents, are recorded as `unsupported` in the source trace and skipped.

- Some older files are served with Excel MIME types but are actually CSV files.
- File extension is more reliable than MIME type, but both can be wrong.

These files have a wide variety of internal structures, with many quirks and edge cases. Column names aren't consistent, date formats vary widely even within the same column.

Here are some examples of recurring structures:

- Single clean CSV table with a single header row
- CSVs with one file per activity type
- CSVs with one file per person and per activity type
- Old CSVs with month-level dates like `Oct-12`
- CSVs where rows are explicit `Nil Return`
- Workbooks with multiple sheets such as `Gifts`, `Hospitality`, `Meetings`, `Travel`
- Workbooks with a `Notes` sheet describing the meaning of the other sheets
- Workbooks where person names appear once and are blank on following rows
- Workbooks mixing exact dates, month names, and date ranges in one column
- Workbooks with unused helper sheets like `Sheet2`
- HTML publications with proper `<table>` markup
- HTML publications whose table represents a different transparency dataset type such as outside employment

## Types of data

This dataset covers several recurring transparency return types, including:

- meetings with external organisations, media, and stakeholders
- gifts given and received
- hospitality received
- overseas travel and domestic official visits
- official receptions and charity receptions
- guests at Chequers and other official hospitality guest lists
- outside employment and similar declaration-style tables in some HTML publications

These can appear as one-file-per-activity CSVs, mixed workbooks with multiple activity tabs, Prime Minister-specific layouts, special adviser returns, senior official returns, and older legacy templates with nil-only publications or explanatory note rows.

## Crawler model

The crawler supports these activity types:

- `meetings`
- `gifts`
- `hospitality`
- `travel`
- `outside_employment`

There is no generic `other` activity type.

For schema authoring details, see `AGENTS.md`. For the canonical mapping model, see `MAPPING.md`.

Downloaded attachments (every format except HTML) are fetched with `dataset.fetch_resource` and saved under `data/datasets/gb_gov_transparency/resources/`, where they never expire. HTML publications are fetched with `dataset.fetch_text`, which caches them in the working database's `cache` table.
