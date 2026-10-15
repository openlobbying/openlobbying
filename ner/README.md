# NER extraction results

`candidates.jsonl.gz` holds every entity-extraction candidate muckrake has made
for these datasets, with its review decision: composite names such as
"Tony Gallagher; Editor; Times, Ted Verity; Editor-in-Chief; Mail" split into
separate people and organisations. `release-build` and `load` apply the approved
ones.

LLM extraction is paid, so the results are kept here and never re-queried.
Restore them into a fresh working database before extracting anything new:

```bash
uv run muckrake ner-import ner/candidates.jsonl.gz
uv run muckrake ner-extract <dataset> --extractor llm --workers 32   # only new texts are sent
uv run muckrake ner-review --auto                                    # or review in the TUI
uv run muckrake ner-export ner/candidates.jsonl.gz                   # then commit
```

Import never overwrites a decision already in the database. Decisions made in
the review TUI take precedence over `--auto`, which only decides pending
candidates (reviewer `muckrake/auto`).

Contents as of 15 Oct 2026 (ingest 4): 38,320 candidates extracted with
`anthropic:claude-haiku-5-5`; 37,402 auto-approved splits, 918 rejected
because the extraction only repeated the source text.
