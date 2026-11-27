#!/usr/bin/env python3
"""Tally which pages and domains AI answers cite for a prompt.

Usage: python citation_tally.py <responses.json> --brand yourbrand[,alias]

Input: a JSON file with a top-level "runs" list. Each run needs "citationUrls"
(list of URLs) and optionally "responseText", "aiModel", "ownedMentions" and
"ownedCitations" (the shape AI-visibility trackers such as HubSpot AEO return).
Text before the first "{" in the file is ignored, so raw tool output works.

Output: per run, whether your brand is named and whether your domain is cited;
then the most cited domains and the pages cited in more than one run.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8")


def load(path):
    text = open(path, encoding="utf-8").read()
    return json.loads(text[text.index("{"):])


def domain(url):
    host = urlparse(url if "//" in url else "//" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def normalize(url):
    url = re.sub(r"[?#].*$", "", url)
    return re.sub(r"^https?://(www\.)?", "https://", url).rstrip("/")


def main():
    args = sys.argv[1:]
    if not args or "--brand" not in args:
        sys.exit(__doc__)
    i = args.index("--brand")
    brands = [b.strip().lower() for b in args[i + 1].split(",") if b.strip()]
    del args[i:i + 2]
    runs = load(args[0]).get("runs", [])
    if not runs:
        sys.exit("No runs found.")

    dom_count, page_count, pages_by_dom = Counter(), Counter(), defaultdict(set)
    print(f"{len(runs)} runs\n")
    print("Per run: model | brand named | brand cited | sources")
    for r in runs:
        urls = [normalize(u) for u in r.get("citationUrls", [])]
        text = (r.get("responseText") or "").lower()
        named = any(b in text for b in brands) or r.get("ownedMentions", 0) > 0
        cited = any(b in domain(u) for u in urls for b in brands) or r.get("ownedCitations", 0) > 0
        print(f"  {r.get('aiModel', '?'):14} | {'yes' if named else 'no':3} | {'yes' if cited else 'no':3} | {len(urls)}")
        for u in set(urls):
            d = domain(u)
            dom_count[d] += 1
            page_count[u] += 1
            pages_by_dom[d].add(u)

    print("\nDomains (number of runs citing them):")
    for d, n in dom_count.most_common(15):
        print(f"  {n}x {d}")
    print("\nPages cited in more than one run:")
    multi = [(u, n) for u, n in page_count.most_common() if n > 1]
    print("\n".join(f"  {n}x {u}" for u, n in multi) if multi else "  none")
    print("\nAll cited pages by domain:")
    for d, _ in dom_count.most_common():
        for u in sorted(pages_by_dom[d]):
            print(f"  {u}")
    print("\nNamed without being cited usually means the model knows the brand but prefers"
          " another page as a source. Compare those pages with yours before rewriting.")


if __name__ == "__main__":
    main()
