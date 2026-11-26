#!/usr/bin/env python
"""One-shot AEO audit: live URL -> html/md -> structure analysis (Nectiv) + 160-char snippet scoring (DEJAN).
Usage: python run_audit.py <url> --kw "term1,term2" [--out <workdir>] [--brand YourBrand]
Writes page.html, page.md, analyze.json, snippets.json to the workdir (default: $TEMP/aeo_work/<slug>)
and prints one combined summary. Never run with the workdir inside the skill folder.
"""
import sys, os, re, json, subprocess, tempfile, urllib.request
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_blocks as eb  # noqa

def main():
    a = sys.argv[1:]
    url = a[0]
    kws = a[a.index("--kw") + 1].split(",") if "--kw" in a else []
    brand = a[a.index("--brand") + 1] if "--brand" in a else "YourBrand"
    slug = re.sub(r"[^a-z0-9]+", "-", url.split("//")[-1].lower()).strip("-")
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(tempfile.gettempdir(), "aeo_work", slug)
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, PYTHONUTF8="1")
    req = urllib.request.Request(url + ("&" if "?" in url else "?") + "cb=aeo", headers={"User-Agent": "Mozilla/5.0"})
    html_src = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    open(os.path.join(out, "page.html"), "w", encoding="utf-8").write(html_src)
    md = subprocess.run([sys.executable, os.path.join(HERE, "html_to_md.py"), os.path.join(out, "page.html")],
                        capture_output=True, text=True, encoding="utf-8", env=env).stdout
    open(os.path.join(out, "page.md"), "w", encoding="utf-8").write(md)
    an = subprocess.run([sys.executable, os.path.join(HERE, "analyze.py"), os.path.join(out, "page.md"),
                         "--html", os.path.join(out, "page.html")], capture_output=True, text=True, encoding="utf-8", env=env).stdout
    open(os.path.join(out, "analyze.json"), "w", encoding="utf-8").write(an)
    A = json.loads(an)
    rows = []
    for b in eb.blocks(html_src):
        b["score"] = eb.score(b, brand, kws); b["head"] = b["text"][:160]; rows.append(b)
    json.dump(rows, open(os.path.join(out, "snippets.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = [r["score"]["total"] for r in rows if len(r["text"]) > 30]
    weak = [r for r in rows if r["score"]["total"] <= 3 and len(r["text"]) > 30 and r["tag"] != "li" or
            (r["score"]["1_volledige_zin"] == 0 and len(r["text"]) > 160)]
    qa, ent, tk, fr = A.get("QA", {}), A.get("ENTITY", {}), A.get("TAKEAWAYS", {}), A.get("FRESH", {})
    print(f"URL: {url}\nWORKDIR: {out}\nwoorden: {A.get('word_count')}")
    print(f"[STRUCTUUR] vraagkoppen {qa.get('question_headings')}/{qa.get('headings_total')} | entity-dichtheid {ent.get('entity_density_pct')}% "
          f"| zinnen zonder entity {ent.get('pct_sentences_with_zero_entities')}% | Key Takeaways: {'ja' if tk.get('passes') else 'nee'} "
          f"| dagen sinds update {fr.get('days_since_update')} | definitief {A.get('DEFINITIVE', {}).get('pct_sentences_definitive')}%")
    print(f"[TABELLEN] LET OP: html_table_elements={A.get('TABLE', {}).get('html_table_elements')} telt layouttabellen mee; negeer voor [TABLE]")
    print(f"[SNIPPET] {len(rows)} blokken, gem. score {sum(tot)/max(1,len(tot)):.1f}/7, zwak/afkapproblemen: {len(weak)}")
    for r in weak[:12]:
        print(f"   [{r['tag']}] {r['score']['total']}/7 | {r['head']}")
    print("LET OP: analyze.py-heuristieken (entity, definitief, FK, vraagwoorden) zijn Engelstalig; voor NL/DE/PT alleen richtinggevend.")

if __name__ == "__main__":
    main()
