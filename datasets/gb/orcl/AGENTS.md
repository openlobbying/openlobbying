## What makes this dataset tricky

The ORCL site is a Salesforce Visualforce application with A4J AJAX controls.

- Search pagination (`Next Page`) is AJAX-driven.
- Quarter selection links in "Previous client lists" are AJAX-driven.
- Some quarter client lists have internal pagination (`Next clients` / `Previous clients`).
- Responses include updated Visualforce viewstate fields that must be reused for follow-up actions.

Direct URL requests are not enough for full extraction; you must simulate these postbacks.

## Crawl steps

The crawler:

1. Crawls search result pages via AJAX `Next Page` postbacks.
2. Loads each profile page.
3. Extracts all quarter snapshots (current + previous links).
4. For each quarter snapshot, follows internal client pagination to collect all clients.
5. Emits `Representation` records with quarter `startDate`/`endDate`.

## Caching: what is cached and what is not

### Cached

- Profile HTML pages are cached via `context.fetch_resource(...)` under:
  - `data/datasets/orcl/resources/profile_<salesforce_id>.html`
- Extracted quarter snapshots are cached as JSON under:
  - `data/datasets/orcl/resources/profile_<salesforce_id>_snapshots.json`

This means reruns should avoid re-doing the expensive AJAX workflow for profiles that are already cached. Neither cache expires, so a re-crawl serves stale client lists until the files are removed: [orcl: profile and quarter-snapshot caches never expire, so re-crawls serve stale client lists](https://github.com/openlobbying/openlobbying/issues/46).

### Not cached by HTTP layer

- AJAX postbacks (quarter links and next-clients pages) are not directly cached by `fetch_text`/`fetch_json`.
- Instead, their *result* is captured in the snapshots JSON cache above.

If you want a full refresh, delete those snapshot JSON files (or `data/datasets/orcl/resources/`).

## Key helper functions

- `parse_ajax_submit(onclick)`
  - Parses A4J `onclick` handlers to extract form id + trigger parameter.
- `hidden_inputs_payload(soup)`
  - Rebuilds payload from hidden fields (includes ViewState fields).
- `post_ajax(session, url, payload)`
  - Sends ORCL-compatible AJAX request headers.
- `fetch_all_clients_from_form(...)`
  - Walks `Next clients` pages for a quarter until completion.

## Data caveats

- Some cells include structured text like:
  - `All Party Parliamentary Group on Customer Service`
  - `Funded by`
  - `Institute of Customer Service (ICS)`
- The parser drops the `Funded by` token and keeps the two names.
- If ORCL changes table markup, review `extract_clients_from_table` first.

## Failure handling

- Client lists are paged until there is no "Next clients" link. This replaced a 10-page cap, which one large firm's profile hit in the July 2026 ingest baseline. The first "Next clients" postback on a profile page returns page 1 again, so one repeated page is expected; two pages in a row without new clients stops paging with a completeness warning (`dataset.warn_incomplete`) instead of looping.
- The first register page is fetched with `raise_for_status()`, so a failure there stops the crawl.
- A failed fetch of a later register page, a client page or a previous quarter keeps what was fetched and records a completeness warning, so the run finishes `partial`.
- The quarter snapshots of a profile are written to the snapshot cache even when one of those fetches failed. Later crawls reuse the shortened client list from the cache and record no warning.
- An unrecognised "Next Page" click handler on the register raises and stops the crawl.
- Within a profile, an unrecognised "Next clients" or previous-quarter click handler, or a client page missing its form, also raises. `process_lobbyist` catches every exception and only logs it, so that profile is skipped, nothing is recorded as a failure or completeness warning, and the run can still finish `succeeded`. A profile page that returns a non-200 status is skipped the same way. This is [orcl: a failing lobbyist profile is logged and skipped, not reported](https://github.com/openlobbying/openlobbying/issues/56).

## Debugging a broken extraction

1. Reproduce with one known profile URL.
2. Capture browser `curl` for the failing click (like `Next clients`).
3. Compare payload fields to `hidden_inputs_payload(...)` output.
4. Confirm `AJAXREQUEST` + trigger parameter pair matches the clicked control.
5. Verify updated ViewState values are present in response and reused on subsequent requests.
