# aeo-toolkit

Scripts and a playbook for making web pages **citable by AI search** (ChatGPT, Perplexity, Google AI Mode): answer engine optimization (AEO / GEO).

It audits the structure of a page against published findings on what LLMs lift into their answers, then checks your rewrite before it goes live.

## What's inside

| Path | Purpose |
|---|---|
| `scripts/html_to_md.py` | Convert a page's HTML to clean Markdown (keeps headings, lists, tables; drops nav/footer chrome) |
| `scripts/analyze.py` | Measure the page: answer position, definition sentences, entity density, tables, freshness signals, question headings |
| `scripts/extract_blocks.py` | Extract candidate snippet blocks from a live page and score their first 160 characters |
| `scripts/check_rewrite.py` | Check a full rewrite against the original before delivery (e.g. headings unchanged in order and level) |
| `scripts/run_audit.py` | One-shot: live URL to HTML/Markdown, structure analysis and 160-character snippet scoring |
| `scripts/build_doc.py` | Build a client-facing report as HTML (importable into Google Docs) from an audit JSON |
| `docs/structure-optimizer.md` | The full workflow and rewrite rules |
| `docs/evidence.md` | The research behind each factor, with the stat and its limits |

## Quick start

```bash
curl -sL -A "Mozilla/5.0" "https://example.com/page" -o page.html
python scripts/html_to_md.py page.html > page.md
python scripts/analyze.py page.md --html page.html
# after rewriting:
python scripts/check_rewrite.py page.md page_final.md
```

Or the shortcut: `python scripts/run_audit.py https://example.com/page --kw "term1,term2" --brand YourBrand`

## Notes

- Python standard library only. No paid scraper or extra packages needed.
- The heuristics (entities, definitions, question words) are tuned for English. For other languages treat the output as directional.
- Evidence strength varies per factor. `docs/evidence.md` says which findings are strong and which are anecdotal. Read it before you treat a number as law.

## Credits and license

The structure analysis (`analyze.py`, `html_to_md.py`, `check_rewrite.py`, `build_doc.py`), `docs/structure-optimizer.md` and `docs/evidence.md` are adapted from [Nectiv Digital's claude skills](https://github.com/Nectiv-Digital/nectiv-claude-skills) (MIT, see `LICENSE-NECTIV`). The research they build on is credited per study in `docs/evidence.md`. The 160-character snippet scoring (`extract_blocks.py`, the snippet part of `run_audit.py`) follows [DEJAN's analysis of how AI Mode selects snippets](https://dejan.ai/blog/how-ai-mode-selects-snippets/). Changes and additions are mine.
