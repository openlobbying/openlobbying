## Crawler structure

Each crawler lives in its own directory under `datasets/<country>/`, at any depth: for example `datasets/gb/orcl/` or `datasets/gb/parliament/members/`. muckrake finds every `config.yml` under `datasets/`.

Each crawler must have a `config.yml` and a `crawler.py`. Look at existing datasets for examples. Each crawler must define a `crawl(dataset: Dataset)` function.

When fetching data like JSON, HTML or CSV, use `dataset.fetch_text()`, `dataset.fetch_json()`, `dataset.fetch_html()` with a `cache_days=N` parameter. This ensures we don't overload servers as we develop crawlers. Those responses are cached in the working database's `cache` table. Whole files fetched with `dataset.fetch_resource(name, url)` are saved under `data/datasets/<dataset_name>/resources/` instead, and never expire: delete a file to force a fresh download ([fetch_resource files never expire, so re-crawls silently reuse stale source files](https://github.com/openlobbying/muckrake/issues/41)).

## Creating entities

For each dataset, you'll want to create multiple [entities](https://followthemoney.tech/explorer/schemata/) (e.g., [Person](https://followthemoney.tech/explorer/schemata/Person/), Company, Organization, Employment, Representation, etc.). You can create an entity with `entity = dataset.make("Person")`.

Each entity has a unique stable ID that you can generate with `entity.id = dataset.make_id('entity', 'name')`. Prefer unique identifiers such as registration numbers, IDs, etc. If there's no unique identifier, use a combination of properties that are unlikely to change (e.g., name + date of birth for a person).

We use the [org-id](https://org-id.guide/about) schema when available, so if you have a company registration number, you can generate the ID with `dataset.make_id(reg_nr=..., register='GB-COH')`.

## Properties

Before creating a new entity type, check [its documentation](https://followthemoney.tech/explorer/schemata/) (`https://followthemoney.tech/explorer/schemata/<EntityType>/`) to see what properties it has. Do this every time.

You can then add properties like `entity.add('name', 'John Doe')`.

All entries in the `gb` directory will have the property `jurisdiction` set to `gb`. For Scottish datasets, it should be `gb-sct`.

An important property is `topics`, which is used for categorisation. For example, you might add `entity.add('topics', 'role.lobby')` for lobbyists, `entity.add('topics', 'role.pep')` for politicians, `entity.add('topics', 'gov')` for government departments, etc.

Once you've added all the properties, you can emit the entity with `dataset.emit(entity)`.

If you can't be sure about something when creating an entity, crash loudly rather than guessing or falling back to a potentially incorrect value.

## Units of work

Long crawlers over many independent sources (files, pages, records) should wrap each one in `dataset.run_unit(key, func, *args)`, with a stable key such as the source URL. If `func` raises, only that unit fails: nothing it emitted is written, the run finishes as `partial` with the failures counted by error type, and `uv run muckrake crawl <dataset> --retry-failed` re-runs the failed units (and resumes a crawl that crashed) without redoing the rest. Crashing loudly still applies inside a unit: raise rather than guess, and the unit is skipped and reported. See `datasets/gb/gov_transparency/crawler.py`.

## Completeness warnings

A crawler must not drop data silently. If it knowingly stops short of the full source (a page cap, an API returning fewer items than its reported total, a linked file that 404s), record it with `dataset.warn_incomplete("fixed reason phrase", **context)` instead of only logging it. The run then finishes as `partial`, the warning is counted in the crawl summary, and `release-build` reports it. Paginated Parliament APIs should use `iter_api_items` in `datasets/gb/parliament/util.py`, which checks `totalResults`. Errors that mean the scraper no longer matches the site (unrecognised markup) should still raise.