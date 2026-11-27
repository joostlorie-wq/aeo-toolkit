# Competitor and SERP check before you rewrite a page

Goal: find out why a competitor is cited and you are not, before you change a single sentence. Run this when:

- your brand is **named but not cited** in AI answers for a prompt,
- a prompt scores 0% and you do not know why,
- a tool recommends "create a page about X" and you first need to know whether you already have a page that should win that query.

Skip it for a pure snippet check or a small FAQ addition.

## Steps

1. **Collect the AI answers and their sources** for the prompt from your AI-visibility tracker (several runs per model). Save the JSON and tally it:
   `python scripts/citation_tally.py responses.json --brand yourbrand`
   You get, per run, whether the brand is named and whether your domain is cited, plus the most cited domains and the pages cited in more than one run.
2. **Look at the SERP** for the same topic in the right language and country: top five organic results, the AI Overview and its sources, People Also Ask. Note the page type of each winner: category page, comparison list, blog post, directory.
3. **Analyse the top three cited pages** with the same criteria you use on your own page (`docs/structure-optimizer.md`, `scripts/extract_blocks.py`): definition in the first paragraph, table, FAQ, concrete numbers, sub-questions answered, price transparency, schema. Run `scripts/run_audit.py` on your page so the comparison is like for like.
4. **Check live what you have or lack** before you write "missing": all languages, the blog, the page you assume does not exist.
5. **Classify the gaps**

   | Gap | Action |
   |---|---|
   | A sub-question is missing on an existing page | add a section or FAQ entry |
   | No page serves the intent | new page, after sign-off |
   | Competitor is cited with equal content | improve extractability, schema, proof |

6. **Feed the gaps into your rewrite list**, ordered like the rest of the audit.

## Pitfalls

- Do not copy competitor claims. Verify each one against your own product documentation before it goes on your page.
- A source that appears in every answer tells you about the winning page type, not about that one competitor.
- AI answers vary between runs. Look for patterns over all runs, not at one answer.
- A brand mention in the answer proves nothing about citation. Measure citations separately.
