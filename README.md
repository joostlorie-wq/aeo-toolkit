# aeo-toolkit

Scripts and a playbook for making web pages **citable by AI search** (ChatGPT, Perplexity, Google AI Mode): answer engine optimization (AEO / GEO).

It audits the structure of a page against published findings on what LLMs lift into their answers, then checks your rewrite before it goes live.

## What's inside

| Path | Purpose |
|---|---|
| `scripts/html_to_md.py` | Convert a page's HTML to clean Markdown (keeps headings, lists, tables; drops nav/footer chrome) |
| `scripts/analyze.py` | Measure the page: answer position, definition sentences, entity density, tables, freshness signals, question headings |
| `scripts/extract_blocks.py` | Pull out the blocks AI engines quote most: opening, bullets, H2/H3 intros |
| `scripts/check_rewrite.py` | Compare original and rewrite: did the key factors actually improve? |
| `scripts/run_audit.py` | One-shot: fetch a URL, run the checks, print a scorecard |
| `scripts/build_doc.py` | Render an audit JSON into a readable HTML report |
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

- Standard library plus `requests` where noted in the scripts.
- The heuristics (entities, definitions, question words) are tuned for English. For other languages treat the output as directional.
- Evidence strength varies per factor. `docs/evidence.md` says which findings are strong and which are anecdotal. Read it before you treat a number as law.
